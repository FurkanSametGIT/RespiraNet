"""ICBHI 2017 parsing, leakage-free splitting and audio preparation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np

LABELS = ["normal", "crackle", "wheeze", "both"]
TARGET_SR = 16000


def label_from_flags(crackle: int, wheeze: int) -> str:
    if crackle not in (0, 1) or wheeze not in (0, 1):
        raise ValueError("crackle/wheeze flag should be 0 or 1")
    return {(0, 0): "normal", (1, 0): "crackle", (0, 1): "wheeze", (1, 1): "both"}[(crackle, wheeze)]


def collect_cycles(root: Path):
    """Return cycle rows, exclusions. Expects WAV and same-stem TXT anywhere under root."""
    from soundfile import info
    rows, problems = [], []
    root = Path(root).resolve()
    wavs = sorted(root.rglob("*.wav"))
    if not wavs:
        raise ValueError(f"No WAV files found under {root}; obtain the official dataset first")
    for wav in wavs:
        ann = wav.with_suffix(".txt")
        if not ann.exists():
            matching = sorted(root.rglob(wav.stem + ".txt"))
            ann = matching[0] if matching else ann
        if not ann.exists():
            problems.append({"file": str(wav.relative_to(root)), "reason": "MISSING_ANNOTATION"})
            continue
        patient = wav.stem.split("_")[0]
        if not patient.isdigit():
            problems.append({"file": str(wav.relative_to(root)), "reason": "INVALID_PATIENT_ID"})
            continue
        try:
            meta = info(str(wav))
            duration = meta.duration
            if duration <= 0:
                raise ValueError("EMPTY_AUDIO")
        except Exception as exc:
            problems.append({"file": str(wav.relative_to(root)), "reason": f"BAD_WAV:{type(exc).__name__}"})
            continue
        for line_no, line in enumerate(ann.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                parts = line.split()
                if len(parts) != 4:
                    raise ValueError("wrong column count")
                start, end = float(parts[0]), float(parts[1])
                c, w = int(parts[2]), int(parts[3])
                if not 0 <= start < end <= duration + 0.08:
                    raise ValueError("cycle outside audio duration")
                label = label_from_flags(c, w)
                rows.append({"cycle_id": f"{wav.stem}:{line_no}", "patient_id": patient,
                    "recording": wav.stem, "wav_path": str(wav), "start_s": start, "end_s": min(end, duration),
                    "duration_s": round(end-start, 4), "label": label, "sample_rate": meta.samplerate})
            except Exception as exc:
                problems.append({"file": str(ann.relative_to(root)), "line": line_no, "reason": f"INVALID_CYCLE:{exc}"})
    if not rows:
        raise ValueError("No valid annotated respiratory cycles found")
    return rows, problems


def group_split(rows, seed=42, train_ratio=0.7, val_ratio=0.15):
    """Split by patient, never by cycle. Fixed RNG seed and disjoint patient lists."""
    patients = sorted({r["patient_id"] for r in rows})
    if len(patients) < 3:
        raise ValueError("Need at least 3 distinct patients for train/val/test")
    rng = np.random.default_rng(seed)
    rng.shuffle(patients)
    n = len(patients)
    n_train = max(1, min(n-2, round(n * train_ratio)))
    n_val = max(1, min(n-n_train-1, round(n * val_ratio)))
    assignments = {p: ("train" if i<n_train else "validation" if i<n_train+n_val else "test")
                   for i,p in enumerate(patients)}
    assigned = [dict(r, split=assignments[r["patient_id"]]) for r in rows]
    train={p for p,s in assignments.items() if s=="train"}
    val={p for p,s in assignments.items() if s=="validation"}
    test={p for p,s in assignments.items() if s=="test"}
    assert not (train & val or train & test or val & test)
    return assigned


def read_audio_cycle(row, sr=TARGET_SR, max_seconds=8):
    """Read only an annotated cycle; mono/resample; truncate unusually long cycles with warning in docs."""
    import soundfile as sf
    import librosa
    path = row["wav_path"]
    with sf.SoundFile(path) as sound:
        original_sr = sound.samplerate
        start = max(0, int(float(row["start_s"]) * original_sr))
        stop = max(start + 1, int(float(row["end_s"]) * original_sr))
        sound.seek(start)
        y = sound.read(frames=stop-start, dtype="float32", always_2d=True)
    if not len(y):
        raise ValueError("Empty cycle")
    mono = y.mean(axis=1)
    if original_sr != sr:
        mono = librosa.resample(mono, orig_sr=original_sr, target_sr=sr)
    if len(mono) > sr * max_seconds:
        center = len(mono)//2
        mono = mono[center - (sr * max_seconds)//2: center + (sr * max_seconds)//2]
    return np.asarray(mono, dtype=np.float32)


def add_noise(y, snr_db, row_id, seed=42):
    """Deterministic synthetic white noise for *paired* evaluation; not natural device shift."""
    if snr_db is None:
        return np.asarray(y, dtype=np.float32).copy()
    digest = hashlib.sha256(f"{row_id}:{seed}:{snr_db}".encode()).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    noise = rng.normal(size=len(y)).astype(np.float32)
    power = float(np.mean(y*y))
    if power < 1e-12:
        return y.copy()
    noise_power = max(float(np.mean(noise*noise)), 1e-12)
    scale = np.sqrt(power / (noise_power * (10**(snr_db/10))))
    return np.clip(y+noise*scale, -1, 1).astype(np.float32)


def extract_mfcc(y, sr=TARGET_SR):
    import librosa
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20, n_fft=1024, hop_length=256)
    return np.concatenate([mfcc.mean(axis=1), mfcc.std(axis=1)]).astype(np.float32)


def logmel_image(y, sr=TARGET_SR, n_mels=64, frames=128):
    import librosa
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=256, n_mels=n_mels)
    db = librosa.power_to_db(mel, ref=np.max)
    if db.shape[1] < frames:
        db = np.pad(db, ((0,0),(0,frames-db.shape[1])), constant_values=-80)
    else:
        # Deterministically sample full duration rather than silently cropping the beginning.
        indices = np.linspace(0, db.shape[1]-1, frames).astype(int)
        db = db[:, indices]
    img = np.clip((db + 80) / 80, 0, 1).astype(np.float32)
    return np.stack((img, img, img), axis=0)


def metrics_four_class(truth, predictions):
    from sklearn.metrics import f1_score, confusion_matrix, recall_score
    truth, predictions = list(truth), list(predictions)
    if not truth: raise ValueError("Empty test set")
    abnormal = [i for i,x in enumerate(truth) if x != "normal"]
    normal = [i for i,x in enumerate(truth) if x == "normal"]
    se = (sum(truth[i] == predictions[i] for i in abnormal)/len(abnormal)) if abnormal else None
    sp = (sum(predictions[i] == "normal" for i in normal)/len(normal)) if normal else None
    return {"n_cycles":len(truth), "macro_f1":float(f1_score(truth, predictions, labels=LABELS, average="macro",zero_division=0)),
            "sensitivity":se, "specificity":sp,
            "icbhi_score":((se+sp)/2 if se is not None and sp is not None else None),
            "class_recall":{label:float(v) for label,v in zip(LABELS,recall_score(truth,predictions,labels=LABELS,average=None,zero_division=0))},
            "confusion_matrix":confusion_matrix(truth,predictions,labels=LABELS).tolist()}


def patient_bootstrap_delta(rows, e1_pred, e2_pred, seed=42, n_boot=1000):
    """Paired patient-level bootstrap; report only when actual E1/E2 data exist."""
    patients = sorted({r["patient_id"] for r in rows})
    if len(patients)<2: return None
    idx = {p:[i for i,r in enumerate(rows) if r["patient_id"]==p] for p in patients}
    rng=np.random.default_rng(seed)
    diffs=[]
    for _ in range(n_boot):
        sample=rng.choice(patients,size=len(patients),replace=True)
        take=[i for p in sample for i in idx[p]]
        t=[rows[i]["label"] for i in take]
        a=metrics_four_class(t,[e1_pred[i] for i in take])["sensitivity"]
        b=metrics_four_class(t,[e2_pred[i] for i in take])["sensitivity"]
        if a is not None and b is not None: diffs.append(b-a)
    if not diffs:return None
    return {"lower":float(np.percentile(diffs,2.5)),"upper":float(np.percentile(diffs,97.5)),"unit":"patient"}
