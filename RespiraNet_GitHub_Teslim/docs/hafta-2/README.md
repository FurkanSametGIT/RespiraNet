# Hafta 2 — Figma ekranları, ER, SQL ve sözlük

## Teslim dosyaları

| Çıktı | Dosya |
|---|---|
| ER diyagramı | [SVG](diyagramlar/07_er_diyagrami.svg) / [GitHub Mermaid](diyagramlar/07_er_diyagrami.mmd) / [DOT](diyagramlar/07_er_diyagrami.dot) |
| PostgreSQL şeması | [`db/schema.sql`](../../db/schema.sql) |
| Veri sözlüğü | [`veri-sozlugu.md`](veri-sozlugu.md) |
| Teknoloji yığını | [`teknoloji-yigini.md`](teknoloji-yigini.md) |
| 6 ekranlık tasarım | [`figma-svg`](figma-svg/) içindeki 6 adet SVG / PNG |
| Tıklanabilir HTML prototipi | [`prototip/index.html`](prototip/index.html) |
| Figma aktarımı | [`figma-svg/FIGMA_AKTARIM.md`](figma-svg/FIGMA_AKTARIM.md) |

## Ekranlar ve geçişler

| Ekran | Giriş | Tıklanabilir çıkış |
|---|---|---|
| 01 Giriş | İlk açılış | Demo oturumu → Ana panel |
| 02 Ana panel | Giriş sonrası | Ses yükleme, model deneyleri |
| 03 Ses yükleme | Ana panel | ICBHI temsili örneği → Sonuç, harici WAV → yalnız kalite raporu; hata dalı |
| 04 Analiz sonucu | Yükleme | Yeni kayıt, geçmiş |
| 05 Geçmiş | Yan menü | Kayıt inceleme, mockup kaydı silme |
| 06 Model deneyleri | Yan menü | E0/E1/E2 ve 3 SNR için boş ölçüm tablosu |

**Önemli:** SVG dosyaları Figma içine alınabilir, ancak SVG dosyalarının kendisi tıklanabilir bir Figma prototype bağlantısı içermez. Figma'da çerçeveler arasında etkileşim oluşturulmalıdır. HTML sürümü şimdi tıklanabilir; **gerçek ses analiz servisi, kullanıcı hesabı veya veritabanı bağlantısı içermez**.

## SQL çalışma komutu

PostgreSQL 15 veya üstünde yeni bir veritabanı açtıktan sonra:

```bash
psql -v ON_ERROR_STOP=1 -d respiranet -f db/schema.sql
```

İlişkiler, PK/FK, `UNIQUE` ve `CHECK` kısıtları tanımlanmıştır. Tahmin tablosundaki tetikleyici yalnız doğrulanmış ICBHI referansına ait, kabul edilmiş kayıtlar için tahmine izin verecek şekilde planlanmıştır. Gerçek sistemde ayrıca API seviyesinde yetki ve içerik denetimi zorunludur.
