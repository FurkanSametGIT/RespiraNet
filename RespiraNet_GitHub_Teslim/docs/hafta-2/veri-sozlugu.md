# RespiraNet — Veri sözlüğü

Bu sözlük, `db/schema.sql` içindeki PostgreSQL tablo ve sütunları açıklar. Üretim sistemi değil, ders kapsamında geliştirilecek bir araştırma prototipinin **tasarımıdır**. PK: birincil anahtar; FK: yabancı anahtar; UQ: benzersiz değer.

| Tablo | Alan | Veri tipi | Kısıt / anlam |
|---|---|---|---|
| `users` | `id` | UUID | PK; kullanıcı kimliği |
| `users` | `full_name` | VARCHAR(120) | Zorunlu görünen ad |
| `users` | `email` | CITEXT | UQ; büyük/küçük harf duyarsız e-posta |
| `users` | `password_hash` | TEXT | Güçlü parola özeti; düz şifre tutulmaz |
| `users` | `role` | VARCHAR(16) | `user`, `researcher`, `admin` |
| `users` | `created_at` | TIMESTAMPTZ | Hesap oluşturma zamanı |
| `reference_samples` | `id` | UUID | PK; sunucu tarafından kayıt altına alınan doğrulanmış ICBHI örneği |
| `reference_samples` | `dataset_key` | VARCHAR(32) | `ICBHI2017` |
| `reference_samples` | `recording_key` | TEXT | UQ; yerel örnek anahtarı; GitHub'a ses yükleme zorunluluğu yok |
| `reference_samples` | `patient_code` | TEXT | Hasta bazlı veri ayrımı ve sızıntı denetimi |
| `reference_samples` | `split_name` | VARCHAR(12) | `train`, `validation`, `test`, `demo` |
| `recordings` | `id` | UUID | PK; uygulamaya eklenen kayıt |
| `recordings` | `user_id` | UUID | FK → `users.id`; kaydın sahibi |
| `recordings` | `reference_sample_id` | UUID | Nullable FK → `reference_samples.id` |
| `recordings` | `source_type` | VARCHAR(24) | `reference_sample` ya da `external_upload` |
| `recordings` | `original_filename` | VARCHAR(255) | Kullanıcıya gösterilen dosya adı |
| `recordings` | `file_storage_key` | TEXT | Korumalı saklama anahtarı; herkese açık URL değil |
| `recordings` | `mime_type` | VARCHAR(80) | Örn. `audio/wav`; API'de gerçek içerik de doğrulanmalı |
| `recordings` | `file_size_bytes` | BIGINT | Bayt cinsinden dosya boyutu |
| `recordings` | `duration_ms` | INTEGER | Ses süresi (ms) |
| `recordings` | `sample_rate_hz` | INTEGER | Örnekleme frekansı (Hz) |
| `recordings` | `created_at` | TIMESTAMPTZ | Yükleme zamanı |
| `quality_checks` | `id` | UUID | PK |
| `quality_checks` | `recording_id` | UUID | UQ FK → `recordings.id`; her kayıt için tek güncel değerlendirme |
| `quality_checks` | `status` | VARCHAR(16) | `pending`, `accepted`, `rejected` |
| `quality_checks` | `reason_codes` | JSONB (dizi) | Örn. `BAD_FORMAT`, `TOO_LONG`, `SILENCE`, `CORRUPT` |
| `quality_checks` | `metrics` | JSONB (nesne) | RMS, clipping oranı vb. kalite ölçümleri; tıbbi etiket değil |
| `quality_checks` | `checked_at` | TIMESTAMPTZ | Ölçüm zamanı |
| `model_versions` | `id` | UUID | PK |
| `model_versions` | `condition_code` | VARCHAR(2) | `E0`, `E1`, `E2` |
| `model_versions` | `version_tag` | VARCHAR(60) | Örn. `v0.1.0` |
| `model_versions` | `architecture` | VARCHAR(120) | SVM ya da MobileNetV3-Small |
| `model_versions` | `input_representation` | VARCHAR(32) | `MFCC` veya `LOG_MEL` |
| `model_versions` | `artifact_storage_key` | TEXT | Modelin korumalı saklama yolu |
| `model_versions` | `artifact_sha256` | CHAR(64) | Model bütünlük özeti |
| `model_versions` | `status` | VARCHAR(16) | `draft`, `active`, `retired` |
| `predictions` | `id` | UUID | PK |
| `predictions` | `recording_id` | UUID | FK → `recordings.id` |
| `predictions` | `model_version_id` | UUID | FK → `model_versions.id` |
| `predictions` | `predicted_label` | VARCHAR(24) | `normal`, `crackle`, `wheeze`, `both` |
| `predictions` | `class_probabilities` | JSONB (nesne) | Dört sınıfın örnek olasılıkları (uygulamada ayrıca doğrulanır) |
| `predictions` | `inference_ms` | INTEGER | Çıkarım süresi |
| `predictions` | `created_at` | TIMESTAMPTZ | Tahmin zamanı |
| `experiment_runs` | `id` | UUID | PK |
| `experiment_runs` | `model_version_id` | UUID | FK → `model_versions.id` |
| `experiment_runs` | `split_manifest_sha256` | CHAR(64) | Sabit hasta bölmesi dosyasının özeti |
| `experiment_runs` | `random_seed` | INTEGER | Tekrarlanabilirlik için sabit tohum |
| `experiment_runs` | `train_config` | JSONB (nesne) | Eğitim parametreleri ve gürültü artırma ayarı |
| `experiment_runs` | `status` | VARCHAR(16) | `planned`, `running`, `completed`, `failed` |
| `experiment_metrics` | `id` | UUID | PK |
| `experiment_metrics` | `experiment_run_id` | UUID | FK → `experiment_runs.id` |
| `experiment_metrics` | `snr_db` | SMALLINT / NULL | `NULL` temiz, `20` ve `10` dB sentetik gürültü testi |
| `experiment_metrics` | `sample_count` | INTEGER | Döngü sayısı, bağımsız hasta sayısı değildir |
| `experiment_metrics` | `patient_count` | INTEGER | Ayrı test hastası sayısı |
| `experiment_metrics` | `macro_f1` | NUMERIC(6,5) | Dört sınıflı Macro-F1 |
| `experiment_metrics` | `sensitivity` | NUMERIC(6,5) | Anormal sınıflar için duyarlılık |
| `experiment_metrics` | `specificity` | NUMERIC(6,5) | Normal sınıf için özgüllük |
| `experiment_metrics` | `icbhi_score` | NUMERIC(6,5) | `(Se + Sp) / 2`, otomatik hesaplanır |
| `experiment_metrics` | `confusion_matrix` | JSONB | Sınıf bazlı hata tablosu |

## İlişkiler ve kurallar

- `users` → `recordings`: 1:N. Geçmiş API'si her zaman `recordings.user_id = current_user.id` filtresi uygular.
- `reference_samples` → `recordings`: 1:N, isteğe bağlı. Referans yalnız sunucu tarafından yetkilendirilmiş ICBHI örnekleri içindir.
- `recordings` → `quality_checks`: 1:0..1. Kalite kontrolünden geçmeyen ses için sonuç üretilmez.
- `recordings` → `predictions`: 1:N. **Harici/telefon sesinden dört sınıflı tahminin yazılması veritabanı tetikleyicisiyle engellenir.**
- `model_versions` → `predictions` ve `experiment_runs`: 1:N.
- `experiment_runs` → `experiment_metrics`: 1:N. Aynı test döngüsünün 3 SNR kopyası, 3 bağımsız örnek olarak yorumlanmaz.

**Not:** API, dosya içerik doğrulaması, kaynak yetkilendirmesi, erişim kontrolü, idempotency ve veri silme işlemlerini ayrıca uygulamalıdır. Bu SQL şeması tek başına tam güvenlik çözümü değildir.
