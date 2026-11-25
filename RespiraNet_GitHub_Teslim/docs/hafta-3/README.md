# Hafta 3 — Veri + EDA + AI Baseline (sınıfta 5 dk demo)

## Dersin kontrol listesi

| İstenen çıktı | Dosya / kanıt | Şu anki durum |
|---|---|---|
| ICBHI verisini temin etme | [`VERI_EDINME.md`](VERI_EDINME.md) | Kaynak doğrulandı; gerçek veri bu teslimde **yok** |
| EDA notebook | [`EDA_ICBHI.ipynb`](EDA_ICBHI.ipynb) | Hazır, gerçek veriyi bekliyor |
| Test kümesini ayırma | [`ml/prepare_icbhi.py`](../../ml/prepare_icbhi.py) | Hasta temelli ayrım kodu hazır; gerçek split henüz hesaplanmadı |
| İlk AI prototipi (baseline) | [`ml/train_e0.py`](../../ml/train_e0.py) | MFCC + SVM kodu hazır; gerçek deney koşulmadı |
| İlk metrikler / nicel hedef | [`BASLANGIC_RAPORU.md`](BASLANGIC_RAPORU.md) | Şablon hazır; F1 **ölçülmedi** |

## Teslim için yapılacaklar

1. Resmî ICBHI 2017 ZIP arşivini edinip `data/icbhi/` içine çıkarın; yeniden dağıtım şartlarını ayrıca kontrol edin.
2. Proje kökünde bağımlılıkları yükleyin: `pip install -r ml/requirements.txt`.
3. `python -m ml.prepare_icbhi --data data/icbhi` ile hasta ayrımı ve `excluded.json` oluşturun.
4. `python -m ml.eda` ile kalite/etiket/süre grafikleri ve notebook çıktılarını oluşturun.
5. `python -m ml.train_e0` ile E0 MFCC+SVM modelini eğitip **gerçek** test metriklerini kaydedin.
6. `python -m ml.compare` çalıştırın. `ml/outputs` içindeki ses/model ve özel verileri doğrudan GitHub'a yüklemeyin. Paylaşmak için kişisel veri içermeyen özet tabloları ve grafik görsellerini `docs/hafta-3/sonuclar/` altına seçerek ekleyin.
7. Beş dakikalık sınıf demosunda CSV, EDA, veri sızıntısı denetimi ve ölçülen F1/Se/Sp değerlerini gösterin. Hedef Macro-F1 ≥0,55 **başarı garantisi değildir**.

**Neden otomatik indirme yok?** ICBHI arşivi büyük olabilir; bu teslim ham veri içermez ve erişim koşulları kullanıcı tarafından kontrol edilmelidir. Veri yokken performans raporu üretmek bilimsel açıdan yanlış olur.
