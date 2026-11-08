# RespiraNet — Yeni Figma Mockup Tasarımı

Kaynak yerleşim referansı: **Simple Dashboard Mockup**, Figma Community: https://www.figma.com/community/file/1048559673287861086/dashboard/

Bu tasarımlar kaynağın birebir kopyası değildir. RespiraNet'e uyarlanan özgün, masaüstü odaklı bir dashboard görsel dili kullanır: koyu yan menü, sade bilgi kartları, analiz tabloları ve ses dalga formu.

## Yenilenen ekranlar

| Dosya | Ekran |
|---|---|
| `01_login.svg` | Giriş / demo oturumu |
| `02_dashboard.svg` | Ana Panel |
| `03_upload.svg` | Ses yükleme ve kalite kontrolü |
| `04_result.svg` | Analiz sonucu |
| `05_history.svg` | Kayıt geçmişi |
| `06_models.svg` | E0/E1/E2 deney tablosu |

Her ekran **1440×900 SVG** olarak tasarlanmıştır; PNG dosyaları sadece önizlemedir. Metinler SVG içinde metin elemanıdır; Figma'ya aktarılınca dönüştürme durumuna göre katman düzenlenebilirliği kontrol edilmelidir.

### Figma prototipi

1. Figma Community'deki şablonun uygun lisans ve düzenlenebilir sürümünü kontrol edin. İsterseniz şablonu Duplicate edin; burada verilen SVG'ler ayrıca yeni bir Figma tasarımına da alınabilir.
2. Her SVG'yi ayrı **1440×900 Frame** içine aktarın. Gerekirse SVG'yi içe aktardıktan sonra Ungroup yapın.
3. **Prototype** sekmesinde `On click → Navigate to` bağlantılarını kurun:
   - Giriş → Ana Panel
   - Ana Panel → Ses Yükleme
   - Ses Yükleme → Analiz Sonucu
   - Analiz Sonucu → Kayıt Geçmişi
   - Kayıt Geçmişi → Analiz Sonucu
   - Sol menüden Model Deneyleri → Model Karşılaştırması
4. Harici WAV senaryosunda sonuç ekranına **yalnız kalite kontrolü, sınıf tahmini yok** varyantı ekleyin. Bu proje sınırını koruyun.
5. Figma'da Share → Copy link ile prototip URL'sini repodaki `README.md` dosyasına ekleyin.

> Etik sınır: ICBHI kayıtlarıyla telefon sesleri eşdeğer kabul edilmez. Gösterilen olasılıklar gerçek model ölçümü değildir; uygulama tıbbi tanı koymaz.
