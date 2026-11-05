# RespiraNet — Teknoloji yığını ve gerekçeler

| Katman | Seçim | Bu projedeki görevi | Alternatif / sınır |
|---|---|---|---|
| Ön yüz | React + Vite | Giriş, ses yükleme, kayıt geçmişi, sonuç ve deney metrikleri | Sade HTML prototip yalnız tasarım aşamasındadır |
| Tasarım | Figma | 6 ekranlık tıklanabilir kullanıcı akışı | SVG ekran taslakları içeri aktarılır |
| API | FastAPI (Python) | Kimlik doğrulama, WAV kontrolü, model servisleştirme, geçmiş API | OpenAPI/Swagger otomatik dokümantasyon |
| Veri tabanı | PostgreSQL 15+ | Kullanıcılar, kayıt meta verisi, kalite sonuçları, model sürümleri ve deney metrikleri | Ham sesler DB'ye konmaz |
| Nesne/dosya saklama | Yerel korumalı dizin (geliştirme) | WAV ve model artefaktları, erişim denetimi ile | Deploy'da S3-uyumlu sistem değerlendirilebilir |
| Modelleme | scikit-learn | E0: MFCC + SVM başlangıç modeli | Sabit hasta test ayrımı |
| Modelleme | PyTorch + torchvision | E1/E2: Log-Mel + MobileNetV3-Small | E1-E2 aynı mimari ve başlangıç ayarı |
| Ses işleme | librosa / soundfile / scipy | WAV, ses döngüsü, MFCC, Log-Mel, yapay gürültü | SNR deneyi **offline** yapılır |
| Ölçüm | scikit-learn + NumPy | Macro-F1, Se, Sp, ICBHI, hata matrisi | Hasta düzeyinde bootstrap belirsizliği |
| Dağıtım | Docker Compose | API, veritabanı, ön yüz; yeniden üretilebilir ortam | 8. hafta hedefi; henüz geliştirilmedi |
| Test | pytest + HTTPX / Locust | Fonksiyon, entegrasyon, stres ve yetki testleri | 9. haftanın planlı teslimi |
| Takip | GitHub Issues + Markdown | FR/NFR, görev, kabul kriteri, kanıt linki | `issues.json` taslakları aktarılabilir |

**Kapsam:** Güncel sistem planında AST, Gammatone ve tanı uygulaması yoktur. Dokümantasyon, son önerideki E0/E1/E2 araştırma tasarımına bağlıdır.
