# Hafta 5 — Frontend + ara demo + model karşılaştırması

## Bu hafta gösterilebilen canlı akışlar

1. React arayüzünde hesap açma veya giriş.
2. WAV dosyası seçip FastAPI'ye yükleme.
3. Sonuç ekranında teknik kalite raporunu görüntüleme.
4. PostgreSQL/SQLite üzerinden kendi kayıtlarını listeme ve inceleme.
5. Kayıt notunu değiştirme (PATCH).
6. Kayıt ve dosyayı silme (DELETE).
7. Model deneyleri ekranında E0/E1/E2 için **yalnız gerçek ölçümlerin** gösterilmesi; veri yoksa "ölçüm bekleniyor" mesajı.

Frontend projesi: [`frontend/`](../../frontend/), kurulum: [`frontend/README.md`](../../frontend/README.md).

## 2–3 AI deneyi için deney tasarımı

| Kod | Model | Eğitim girdisi | Test |
|---|---|---|---|
| E0 | MFCC + SVM | ICBHI eğitim hastaları | temiz / 20 / 10 dB SNR |
| E1 | Log-Mel + MobileNetV3-Small | temiz eğitim | aynı test döngüleri |
| E2 | Log-Mel + aynı MobileNetV3 | **yalnız eğitimde** gürültü artırma | E1 ile **aynı** test döngüleri |

- Kodu: [`ml/train_e0.py`](../../ml/train_e0.py), [`ml/train_e1_e2.py`](../../ml/train_e1_e2.py).
- Rapor birleştirme: [`ml/compare.py`](../../ml/compare.py) → `experiments/comparison.csv/md/json`.
- Sınıf bazlı hatalar, F1, Se ve Sp hesaplanır; E1 ile E2 arasındaki 10 dB farkı test hasta düzeyinde bootstrap ile raporlanır.
- **Bu teslimde gerçek veri olmadığı için 2–3 eğitimin yapıldığı veya karşılaştırma metriklerinin ölçüldüğü iddia edilmemelidir.** 

## 5 dakikalık canlı demo senaryosu

| Süre | Gösterilecek |
|---|---|
| 0:00–0:45 | Proje amacı, ICBHI'da hasta bazlı değerlendirme sınırı |
| 0:45–1:30 | React giriş → ana panel |
| 1:30–2:45 | Geçerli WAV yükle → kalite sonucu |
| 2:45–3:35 | Geçmiş → not güncelle → sil, veritabanı CRUD |
| 3:35–4:15 | Bozuk/sessiz WAV hata davranışı |
| 4:15–5:00 | E0/E1/E2 deney planı ve gerçekten elde edilen sonuçlar (varsa) / bekleyen veri durumu |

## Gelecek haftaya bırakılanlar

6. hafta: ICBHI doğrulanmış örnekleri için gerçek model inference API entegrasyonu. 7. hafta: uçtan uca MVP. 8. hafta: dağıtım. 9. hafta: stres ve güvenlik testleri. Bu haftada **yapılmış gibi sunulmazlar**.
