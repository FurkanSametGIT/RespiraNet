-- RespiraNet: PostgreSQL 15+ örnek şeması
-- Araştırma prototipi: tanı / klinik karar sistemi değildir.
-- Çalıştırma: psql -v ON_ERROR_STOP=1 -f db/schema.sql
BEGIN;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(120) NOT NULL,
    email CITEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,    -- bcrypt/argon2 gibi güçlü parola özeti; düz metin asla değil
    role VARCHAR(16) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'researcher', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Yalnız uygulama tarafından hazırlanan ve kimliği doğrulanmış örnekler kaydedilir.
-- Harici yüklemenin kayıt anahtarını doldurarak kendisini doğrulanmış olarak göstermesine izin verilmez.
CREATE TABLE IF NOT EXISTS reference_samples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_key VARCHAR(32) NOT NULL DEFAULT 'ICBHI2017' CHECK (dataset_key = 'ICBHI2017'),
    recording_key TEXT NOT NULL UNIQUE,
    patient_code TEXT NOT NULL,
    split_name VARCHAR(12) NOT NULL CHECK (split_name IN ('train', 'validation', 'test', 'demo')),
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recordings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reference_sample_id UUID REFERENCES reference_samples(id) ON DELETE RESTRICT,
    source_type VARCHAR(24) NOT NULL CHECK (source_type IN ('reference_sample', 'external_upload')),
    original_filename VARCHAR(255) NOT NULL,
    file_storage_key TEXT, -- uygulamaya ait korumalı dosya alanındaki anahtar, herkese açık URL değil
    mime_type VARCHAR(80) NOT NULL DEFAULT 'audio/wav',
    file_size_bytes BIGINT CHECK (file_size_bytes IS NULL OR file_size_bytes > 0),
    duration_ms INTEGER CHECK (duration_ms IS NULL OR duration_ms > 0),
    sample_rate_hz INTEGER CHECK (sample_rate_hz IS NULL OR sample_rate_hz > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT recording_reference_coherent CHECK (
        (source_type = 'reference_sample' AND reference_sample_id IS NOT NULL)
        OR (source_type = 'external_upload' AND reference_sample_id IS NULL)
    )
);
CREATE INDEX IF NOT EXISTS recordings_by_user_time ON recordings(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS quality_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recording_id UUID NOT NULL UNIQUE REFERENCES recordings(id) ON DELETE CASCADE,
    status VARCHAR(16) NOT NULL CHECK (status IN ('pending', 'accepted', 'rejected')),
    reason_codes JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(reason_codes) = 'array'),
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metrics) = 'object'),
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    condition_code VARCHAR(2) NOT NULL CHECK (condition_code IN ('E0', 'E1', 'E2')),
    version_tag VARCHAR(60) NOT NULL,
    architecture VARCHAR(120) NOT NULL,
    input_representation VARCHAR(32) NOT NULL CHECK (input_representation IN ('MFCC', 'LOG_MEL')),
    artifact_storage_key TEXT NOT NULL,
    artifact_sha256 CHAR(64) NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    status VARCHAR(16) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'retired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (condition_code, version_tag),
    CONSTRAINT representation_matches_condition CHECK (
        (condition_code = 'E0' AND input_representation = 'MFCC')
        OR (condition_code IN ('E1', 'E2') AND input_representation = 'LOG_MEL')
    )
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_version_per_condition
    ON model_versions(condition_code) WHERE status = 'active';

CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recording_id UUID NOT NULL REFERENCES recordings(id) ON DELETE CASCADE,
    model_version_id UUID NOT NULL REFERENCES model_versions(id) ON DELETE RESTRICT,
    predicted_label VARCHAR(24) NOT NULL CHECK (predicted_label IN ('normal', 'crackle', 'wheeze', 'both')),
    class_probabilities JSONB NOT NULL CHECK (jsonb_typeof(class_probabilities) = 'object'),
    inference_ms INTEGER CHECK (inference_ms IS NULL OR inference_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT probabilities_four_keys CHECK (
        class_probabilities ?& ARRAY['normal','crackle','wheeze','both']
    )
);
CREATE INDEX IF NOT EXISTS predictions_by_recording ON predictions(recording_id, created_at DESC);

-- Veritabanı ek koruması: doğrulanmamış harici ses için 4 sınıflı tahmin kaydetme.
-- Kaynağı doğrulama / dosya bütünlüğü kontrolü asıl olarak API katmanında yapılmalıdır.
CREATE OR REPLACE FUNCTION verify_prediction_source() RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
  valid_source BOOLEAN;
BEGIN
  SELECT (r.source_type = 'reference_sample' AND r.reference_sample_id IS NOT NULL AND qc.status = 'accepted')
  INTO valid_source
  FROM recordings r LEFT JOIN quality_checks qc ON qc.recording_id = r.id
  WHERE r.id = NEW.recording_id;
  IF NOT COALESCE(valid_source, FALSE) THEN
    RAISE EXCEPTION '4-class prediction requires accepted, server-verified ICBHI reference sample';
  END IF;
  RETURN NEW;
END; $$;
DROP TRIGGER IF EXISTS trg_verify_prediction_source ON predictions;
CREATE TRIGGER trg_verify_prediction_source
BEFORE INSERT OR UPDATE OF recording_id ON predictions
FOR EACH ROW EXECUTE FUNCTION verify_prediction_source();

CREATE TABLE IF NOT EXISTS experiment_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_version_id UUID NOT NULL REFERENCES model_versions(id) ON DELETE RESTRICT,
    split_manifest_sha256 CHAR(64) NOT NULL CHECK (split_manifest_sha256 ~ '^[0-9a-f]{64}$'),
    random_seed INTEGER NOT NULL,
    train_config JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(train_config) = 'object'),
    status VARCHAR(16) NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','running','completed','failed')),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS experiment_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_run_id UUID NOT NULL REFERENCES experiment_runs(id) ON DELETE CASCADE,
    -- NULL: orijinal temiz test; 20 ve 10: yapay gürültülü aynı test döngüleri
    snr_db SMALLINT CHECK (snr_db IS NULL OR snr_db IN (10,20)),
    sample_count INTEGER NOT NULL CHECK (sample_count > 0),
    patient_count INTEGER NOT NULL CHECK (patient_count > 0),
    macro_f1 NUMERIC(6,5) CHECK (macro_f1 IS NULL OR macro_f1 BETWEEN 0 AND 1),
    sensitivity NUMERIC(6,5) CHECK (sensitivity IS NULL OR sensitivity BETWEEN 0 AND 1),
    specificity NUMERIC(6,5) CHECK (specificity IS NULL OR specificity BETWEEN 0 AND 1),
    icbhi_score NUMERIC(6,5) GENERATED ALWAYS AS (
        CASE WHEN sensitivity IS NOT NULL AND specificity IS NOT NULL
             THEN (sensitivity + specificity) / 2 ELSE NULL END
    ) STORED,
    confusion_matrix JSONB NOT NULL DEFAULT '{}'::jsonb,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS experiment_metrics_one_clean_per_run
ON experiment_metrics (experiment_run_id) WHERE snr_db IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS experiment_metrics_unique_snr_per_run
ON experiment_metrics (experiment_run_id, snr_db) WHERE snr_db IS NOT NULL;
COMMIT;
