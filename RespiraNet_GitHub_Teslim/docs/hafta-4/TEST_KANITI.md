# Hafta 4 — Otomatik test özeti

**Komut:** `python -m pytest -q backend/tests ml/tests` (repo içindeki `RespiraNet_GitHub_Teslim` klasöründe)

**Bu çalışma oturumundaki gerçek sonuç:** `10 passed in 1.41s`.

Test kapsamı:
- Servis sağlık bilgisi (`/api/health`).
- Kayıt olma, JWT ile giriş ve kendi profilini görme.
- Geçerli WAV yükleme, kalite kontrolü, kayıtları listeleme, not güncelleme ve silme.
- Başka kullanıcıya ait kaydın okunması, düzenlenmesi veya silinmesinin engellenmesi.
- WAV olmayan içeriklerin reddi.
- Sessizlik durumunda kalite reddi.
- Gerçek deney raporu yokken metrik uydurulmaması.
- Hasta bazlı ayrımın tekrarlanabilir ve sızıntısız olması.
- Etiket eşleştirme ve deterministik gürültü.
- Dört sınıflı Macro-F1, Se, Sp hesaplaması.

**Sınırlar:** Bu testler SQLite üzerinde API testi ve sentetik ML fonksiyon kontrolleridir. PostgreSQL entegrasyonu, gerçek ICBHI başarı değerleri, Vite üretim derlemesi, yük/stres/güvenlik testleri veya 8. hafta canlı ortam kurulumu test edilmiş sayılmaz.
