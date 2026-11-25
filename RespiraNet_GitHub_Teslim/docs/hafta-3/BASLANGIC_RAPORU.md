# Hafta 3 — MFCC+SVM (E0) başlangıç raporu

> **Durum: ÖLÇÜLMEDİ.** Gerçek ICBHI dosyaları kullanıcı tarafından henüz sağlanmadı. Bu şablon bilerek boş bırakıldı.

| Ölçüt | Sonuç | Kanıt |
|---|---|---|
| Kullanılabilir WAV sayısı | Bekleniyor | `ml/outputs/summary.json` |
| Kullanılabilir solunum döngüsü | Bekleniyor | `ml/outputs/summary.json` |
| Hasta bazlı split: ortak hasta | Bekleniyor (hedef 0) | `ml/outputs/eda/eda.json` |
| Test hastası / döngüsü | Bekleniyor | `ml/outputs/summary.json` |
| MFCC + SVM (E0) Macro-F1 | Bekleniyor (hedef ≥0,55) | `ml/outputs/E0/E0_metrics.json` |
| Anormal ses duyarlılığı Se | Bekleniyor | E0 metrik dosyası |
| Normal ses özgüllüğü Sp | Bekleniyor | E0 metrik dosyası |
| ICBHI = (Se + Sp)/2 | Bekleniyor | E0 metrik dosyası |

**Çalıştırılacak komutlar:** [`ml/README.md`](../../ml/README.md). Sonuçlar otomatik JSON olarak oluşur; tablonun gerçek değerlerini sonra bu dosyalardan güncelleyin. Dataset açıklamasındaki 920/6.898 sayılarını modelin ölçülmüş çıktısı gibi yazmayın.
