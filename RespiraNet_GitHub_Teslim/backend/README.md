# FastAPI + PostgreSQL (Hafta 4/5)

Bu API **tanı değil, araştırma/dosya kalitesi prototipidir**. Harici WAV yüklenince hastalık, wheeze veya crackle tahmini oluşturmaz. Dört sınıflı E0/E1/E2 sonuçları gerçek ICBHI testiyle ayrı offline deneylerde ölçülür.

## Hızlı kurulum: yalnız lokal SQLite

`RespiraNet_GitHub_Teslim` içindeki `backend` klasörüne geçin:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# .env içindeki JWT_SECRET'i uzun, rastgele bir değerle değiştirin.
# PowerShell ortam değişkenleri (örnek):
$env:DATABASE_URL="sqlite:///./respiranet-dev.db"
$env:AUTO_CREATE_TABLES="true"
$env:JWT_SECRET="buraya-en-az-32-karakterlik-rastgele-bir-sir-yazin"
uvicorn app.main:app --reload
```

`http://localhost:8000/docs` Swagger UI, `http://localhost:8000/api/health` servis durumunu gösterir.

## PostgreSQL ile çalışma

Repo içindeki `RespiraNet_GitHub_Teslim` köküne dönüp en az 32 karakterlik gizli anahtarı `.env` dosyasında tanımlayın:

```text
JWT_SECRET=buraya-32-karakterden-uzun-rastgele-secret-yazin
```

Sonra:

```powershell
docker compose -f docker-compose.dev.yml up --build
```

PostgreSQL ilk başlatmada **mevcut 2. hafta `db/schema.sql` şemasını** ve `001_add_recording_notes.sql` geçişini uygular. Mevcut bir Docker veritabanı varsa init scriptleri tekrar çalışmaz: migration'ı elle çalıştırmanız gerekir. `docker compose down -v` veritabanı içindeki kayıtları **siler**; ders çalışmaları için yedek almadan kullanmayın.

## API uç noktaları

| Metot | Yol | Açıklama |
|---|---|---|
| GET | `/api/health` | Servis çalışıyor mu? |
| POST | `/api/auth/register` | Hesap oluştur |
| POST | `/api/auth/login` | OAuth2 formuyla JWT al (`username` alanı e-postadır) |
| GET | `/api/auth/me` | Kendi hesabını göster |
| POST | `/api/recordings` | WAV yükle, kalite ölç, kişisel dosyaya kaydet |
| GET | `/api/recordings` | Sadece kendi kayıtlarını listele |
| GET | `/api/recordings/{id}` | Kendi kaydını görüntüle |
| PATCH | `/api/recordings/{id}` | Kayıt notunu değiştir (güncelleme) |
| DELETE | `/api/recordings/{id}` | Kendi kaydını ve dosyasını sil |
| GET | `/api/experiments` | Gerçek deneylerin karşılaştırma dosyasını oku veya beklemede de |

**WAV kısıtları:** Maksimum 12 MB; PCM16, mono/stereo, 8–48 kHz, 1–30 saniye. Çok sessiz ve kırpılmış dosyalar kayıt altına `rejected` kalite durumuyla alınır; dört sınıflı tahmin üretmez. Mimari doğrulama API'de, gizlilik özel depolamada, kullanıcı izolasyonu sorguda uygulanır.

**Klinik sınır:** Algoritmaların ICBHI göğüs kayıtlarıyla telefon kayıtlarının eşdeğerliği gösterilmemiştir. Web uygulaması tanı aracı değildir.
