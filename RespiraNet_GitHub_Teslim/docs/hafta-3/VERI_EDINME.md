# ICBHI 2017 — erişim ve dosya denetimi

**Resmî kaynak:** https://bhichallenge.med.auth.gr/ICBHI_2017_Challenge

Veri kümesi ilk yayımlandığında toplam 126 katılımcı, 920 kayıt ve 6.898 etiketli solunum döngüsü bildirilmiştir. Bu sayılar verinin **tanımıdır**, bizim veri temizleme veya model başarısı sonucumuz değildir.

- ZIP dosyasını kendi bilgisayarına/Colab Drive'ına indirip aç.
- WAV ve dört sütunlu eşleşen `.txt` anotasyonları `data/icbhi/` altında bulunsun.
- Dosya isimleri `{patient}_{recording}_{location}_{mode}_{device}.wav` yapısındadır; örneğin `101_1b1_Al_sc_Meditron.wav`.
- TXT satırı: `start_sec end_sec crackle(0|1) wheeze(0|1)`.
- Bir hastanın kayıtlarını eğitim/validasyon/test arasında paylaşma.
- `excluded.json` bozuk/eksik anotasyonları gerekçeleriyle listeler.
- Dataset orijinal resmî sayfada 2017 sürümündeki 92 cihaz adı düzeltmesiyle ilgili uyarı içerir. Kaynağa uyumlu güncel dosyalarla çalış.
- `.gitignore` ham sesleri, lokal split çıktıları ve model ağırlıklarını GitHub'dan dışlar.

Bu proje teşhis algoritması değil, dört sınıflı **ses olayı** sınıflandırma deneyidir. Sağlık alanında veriyle çalışırken iddialar yalnız doğrulanmış etiketlerin izin verdiği ölçüde yapılmalıdır.
