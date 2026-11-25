# RespiraNet — Hafta 3, 4, 5 teslim ve çalışma rehberi

**Proje:** Solunum Seslerinde Hırıltı ve Çıtırtının Sınıflandırılması ve Gürültüye Dayanıklılığın İncelenmesi  
**Öğrenciler:** Furkan Tekin (230291009), Abdulsamet Karayel (230291034)  
**Repo:** https://github.com/FurkanSametGIT/RespiraNet  
**Mevcut klasör düzeni:** `RespiraNet_GitHub_Teslim/`

## Bu paketin mevcut repoya ekleyeceği klasörler

- `docs/hafta-3/` — EDA notebook, veri edinme ve E0 rapor şablonu
- `ml/` — ICBHI veri ayrımı, EDA, E0 MFCC+SVM, E1/E2 MobileNetV3 ve metrik karşılaştırması
- `docs/hafta-4/` — Backend kontrol listesi, Postman koleksiyonu, test kanıtı
- `backend/` — FastAPI, JWT, Argon2, WAV kalite kontrolü, kayıt CRUD, ORM, migration, API testleri
- `docs/hafta-5/` — Ara demo planı ve sentetik kalite testi için iki WAV
- `frontend/` — 6 ekrana sahip React/Vite arayüzü; gerçek API bağlantısı
- `experiments/` — Deney çıktılarının nasıl doldurulacağı
- `docker-compose.dev.yml`, `.env.example`, `.gitignore`

## Önce: GitHub'a webden ekle

1. Bu ZIP'i Windows'ta **Tümünü Ayıkla** ile aç.
2. İçindeki `RespiraNet_GitHub_Teslim` klasörünü aç.
3. Mevcut repo klasörü: https://github.com/FurkanSametGIT/RespiraNet/tree/main/RespiraNet_GitHub_Teslim
4. O sayfada **Add file → Upload files** seç.
5. Açtığın yerel `RespiraNet_GitHub_Teslim` klasörünün **içindekileri** (örn. `backend`, `frontend`, `ml`, `docs`, `experiments` ve kök dosyaları) yükleme alanına sürükle. Aynı adla ikinci bir `RespiraNet_GitHub_Teslim` alt klasörü oluşturma.
6. Commit mesajı: `Add RespiraNet weeks 3-5 data pipeline, API and frontend`.
7. **Commit directly to the main branch** → **Commit changes**.
8. GitHub'da aynı seviyede `backend`, `frontend`, `ml`, `docs/hafta-3`, `docs/hafta-4`, `docs/hafta-5` göründüğünü kontrol et.

**Dikkat:** GitHub'a yalnız ZIP atma. Eski `docs/hafta-1`, `docs/hafta-2`, `db/schema.sql`, mockup ve diyagramları **silme**. Bu ek paket öncekileri korur. Repo GitHub'da zaten iç içe tek `RespiraNet_GitHub_Teslim` klasöründen oluştuğu için dosya yükleme konumunu doğru seç.

## Hızlı API + React denemesi (Windows)

### Terminal 1 — FastAPI / SQLite (lokal hızlı demo)

`RespiraNet_GitHub_Teslim` içinde:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DATABASE_URL="sqlite:///./respiranet-dev.db"
$env:AUTO_CREATE_TABLES="true"
$env:JWT_SECRET="BUNU-EN-AZ-32-KARAKTERLIK-KENDI-RASGELE-ANAHTARINLA-DEGISTIR"
uvicorn app.main:app --reload
```

API: http://localhost:8000/api/health  
Swagger: http://localhost:8000/docs

### Terminal 2 — React (Node.js 20.19+ veya 22.12+ önerilir)

Aynı `RespiraNet_GitHub_Teslim` altında:

```powershell
cd frontend
npm install
npm run dev
```

Web: http://localhost:5173

1. Kaydol / giriş yap.
2. `docs/hafta-5/synthetic_tone.wav` yükle; kalite uygun dönmeli.
3. `docs/hafta-5/synthetic_silence.wav` yükle; sessizlik nedeniyle ret gerekçesi dönmeli.
4. Geçmiş sayfasında not ekle / güncelle / sil.
5. Model Deneyleri ekranında **ölçüm bekleniyor** mesajını incele. Bunlar **sentetik test tonu**, solunum sesi değildir; AI başarımında kullanılmaz.

### PostgreSQL ile (ayrı seçenek)

`RespiraNet_GitHub_Teslim` köküne `.env` dosyası açıp `JWT_SECRET=...` (en az 32 rastgele karakter) yaz; sonra `docker compose -f docker-compose.dev.yml up --build`. Bu, **yalnız yerel geliştirme** dağıtımıdır. PostgreSQL şeması 2. hafta dosyası + 4. hafta migration ile oluşur. Mevcut DB volume varsa init SQL tekrar uygulanmaz.

## Hafta 3 — Gerçek veri hazır olunca

Resmî ICBHI 2017 verisini kendin indirip **GitHub dışındaki** `data/icbhi/` klasörüne aç:

```powershell
python -m pip install -r ml/requirements.txt
python -m ml.prepare_icbhi --data data/icbhi
python -m ml.eda
python -m ml.train_e0
python -m ml.compare
```

E1/E2 için ayrıca PyTorch/torchvision ve uygun GPU gerekli olabilir:

```powershell
python -m pip install torch torchvision
python -m ml.train_e1_e2 --epochs 5
python -m ml.compare
```

**Sonuç:** `ml/outputs/` altında gerçek EDA / model raporları çıkar. `experiments/comparison.*` yalnız ölçülmüş sonuçları gösterir. Ham WAV'ları ve hasta düzeyi kayıtları repoya gönderme; paylaşılacak istatistikleri anonim ve toplulaştırılmış tut.

## Kontrol edilmiş ve bekleyenler

| İş | Durum |
|---|---|
| Python unit/API testleri | **10 test geçti** (sentetik/lokal test ortamı) |
| Veri alma, hasta ayrımı, EDA, E0 rapor hattı | Küçük **sentetik** testte uçtan uca çalıştı; çıktılar teslimde ölçüm sayılmadı |
| Gerçek ICBHI indirip 920 WAV üzerinde çalışma | **Bekliyor** — gerçek veri sağlanmadı |
| E0/E1/E2 gerçek F1 ve SNR testleri | **Bekliyor** — veri/hesaplama gerekli |
| PostgreSQL Docker entegrasyon testi | Bu ortamda çalıştırılmadı |
| React Vite üretim derlemesi | Ağ/npm indirme sınırı nedeniyle burada doğrulanmadı; JSX sözdizimi kontrol edildi |

Hedefleri sonuç diye sunmayın; dersin 3. haftası için gerçek baseline metriklerini veri üzerinde çalıştırdıktan sonra tamamlayın.
