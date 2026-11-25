# Hafta 4 — Backend iskeleti, veritabanı, kimlik doğrulama

Bu hafta için *yalnızca gerekli* yazılım: FastAPI servisleri, kimlik doğrulama, temel kayıt CRUD uçları, Swagger/OpenAPI, örnek ortam ayarları ve SQL geçişi.

## Dosyalar ve kanıtlar

| İstenen | Teslim |
|---|---|
| Backend iskeleti | [`backend/app/main.py`](../../backend/app/main.py) |
| Veritabanı bağlantısı ve ORM | [`backend/app/db.py`](../../backend/app/db.py) |
| 2. hafta şeması üzerine migration | [`backend/migrations/001_add_recording_notes.sql`](../../backend/migrations/001_add_recording_notes.sql) |
| JWT + Argon2 parola özeti | [`backend/app/security.py`](../../backend/app/security.py) |
| Temel CRUD / kalite kontrol | `/api/recordings`, `/api/auth/*` |
| Swagger/OpenAPI | `http://localhost:8000/docs`, `http://localhost:8000/openapi.json` |
| Postman örnek istekler | [`RespiraNet.postman_collection.json`](RespiraNet.postman_collection.json) |
| `.env.example` | [`backend/.env.example`](../../backend/.env.example) |
| Otomatik testler | [`backend/tests`](../../backend/tests) |

## Kurulum

[`backend/README.md`](../../backend/README.md) hem hızlı SQLite testi hem PostgreSQL Docker geliştirme ortamını açıklar. PostgreSQL için **mevcut** `db/schema.sql` silinmez; yeni `notes` alanı migration ile eklenir. Kişisel ses dosyaları yalnız özel klasörde saklanır.

## Özellikle test edilen hata dalları

- WAV olmayan dosya → 415 veya 422.
- Başka kullanıcıya ait kayıt → 404 (kullanıcılar birbirinin varlığını görmez).
- Aşırı sessiz kayıt → `rejected` kalite durumu ve açık gerekçe.
- Geçersiz JWT → 401.
- Harici WAV → dört sınıflı tıbbi tahmin yok.

**Kısıt:** Bu iskelet üretim ortamı için güvenlik sertifikası değildir; ileri seviye yük testi/CI, loglama ve güvenlik denetimi ders takviminde 9. hafta kapsamındadır.
