# RespiraNet React (Hafta 5)

Altı Figma mockup ekranıyla aynı bilgi mimarisi: **Giriş, Dashboard, WAV Yükleme, Kalite Sonucu, Geçmiş, Model Karşılaştırma**. Figma ekranlarının birer görsel kopyası değildir; gerçek FastAPI ve veritabanı CRUD akışına bağlanır.

## Çalıştırma

Önce `backend/README.md` ile API'yi başlatın (`http://localhost:8000`). Ardından:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Tarayıcı: `http://localhost:5173`

Kendi e-postanızla kayıt olun. WAV yükleyin, kalite raporunu görün, geçmiş sayfasında notu güncelleyip kayıt silin. Model Deneyleri sayfası gerçek deneyler çalıştırılmadıysa **ölçüm bekleniyor** mesajı gösterir. `POST /api/recordings` kalite kabulü bir klinik tahmin değildir.

## Güvenlik ve kapsam

- JWT bu **yalnızca ders demosu** için tarayıcı localStorage'ında tutulur; üretimde HttpOnly güvenli cookie, CSRF/XSS ve oturum yenileme tasarımı gerektirir.
- CORS yerel Vite portu içindir. `backend/.env.example` dosyasındaki secret kullanılmamalıdır.
- Dosya kontrolü hastalık teşhisi veya hırıltı/çıtırtı sınıflandırması değildir.
- Frontend testleri ve stres testleri 9. hafta kapsamına ayrıca alınmalıdır; 5. hafta için çalışır bir CRUD demosu hedeflenmiştir.
