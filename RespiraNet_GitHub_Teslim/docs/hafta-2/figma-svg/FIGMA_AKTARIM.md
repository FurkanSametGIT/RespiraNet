# Figma'ya aktarılacak 6 ekran

SVG dosyaları 1440 × 900 masaüstü çerçevesi olarak tasarlanmıştır. Metin, kutu ve çizgiler vektör öğeleridir; Figma'ya içe aktarıldıktan sonra düzenlenebilir. Aynı adların PNG karşılıkları hızlı önizleme içindir.

1. `01_login.svg` — Giriş / oturum.
2. `02_dashboard.svg` — Ana panel.
3. `03_upload.svg` — Ses kaynağı ve dosya seçimi.
4. `04_result.svg` — Sonuç ve kalite raporu.
5. `05_history.svg` — Kayıt geçmişi.
6. `06_models.svg` — Deney karşılaştırması.

## Figma'da tamamlanacak tıklanabilir prototip

1. Figma'da `RespiraNet - Hafta 2` adında yeni bir tasarım dosyası açın.
2. **Frame** aracıyla 1440 × 900 boyutunda altı Frame açın; her SVG'yi ilgili Frame içine sürükleyin. SVG'ler vektör içeriklidir, fakat her SVG yerleşim için ayrı bir alt grup olarak kalabilir.
3. **Prototype** sekmesinde aşağıdaki `On click → Navigate to` bağlantılarını kurun:
   - Giriş / **Demo oturumu aç** → Ana Panel
   - Ana Panel / **Ses yükleme** → Ses Yükleme
   - Ana Panel / **Deneyleri gör** → Model Karşılaştırma
   - Ses Yükleme / **Kontrolü başlat** → Analiz Sonucu
   - Analiz Sonucu / **Yeni kayıt** → Ses Yükleme
   - Analiz Sonucu / **Kayıt geçmişi** → Geçmiş
   - Geçmiş / **İncele** → Analiz Sonucu
   - Sol menüdeki sekmeler → ilgili Frame
4. Kaynak **Harici WAV** seçilirse, sonuç sayfasının `yalnız kalite raporu` varyantını ayrıca bir **component variant / overlay** olarak oluşturun; dört sınıflı sonuç göstermeyin.
5. Hatalı WAV örneğini göstermek için **Hatalı format / boş dosya** toast'ını ayrı overlay olarak bağlayın.
6. Flow starting point olarak giriş ekranını seçin; **Present** modunda tüm altı ekrana geçilebildiğini test edin ve Figma linkini GitHub README'ye ekleyin.

## Hazır, tıklanabilir referans

Ayrıca `../prototip/index.html` dosyasını tarayıcıda açarak altı ekran arasında gezebilirsiniz. Bu dosya gerçek model veya API içermez, yalnız kullanıcı etkileşimini taklit eder.
