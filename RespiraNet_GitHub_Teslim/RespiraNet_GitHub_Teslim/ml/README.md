# Modelleme: E0 / E1 / E2

**Çalıştırma gerektirir. Bu repoda klinik tanı modeli ya da önceden ölçülmüş F1 değeri bulunmuyor.**

## Gerçek veriyi edinme

ICBHI 2017 arşivini **[resmî sayfadan](https://bhichallenge.med.auth.gr/ICBHI_2017_Challenge)** indirip `data/icbhi/` klasörüne açın. WAV ve aynı ada sahip dört sütunlu anotasyon TXT dosyaları aynı yerde veya klasör ağacında bulunabilir. Ham sesleri GitHub'a göndermeyin. 2017 kaynağının orijinal verileri 126 katılımcı, 920 kayıt ve 6.898 döngü içerir; **bu sayılar bizim çalışmamızın çıktısı değildir**. Dosya eşleştirme/kalite denetiminden sonra kullanılan gerçek sayı otomatik raporlanır.

Windows PowerShell, repo içindeki `RespiraNet_GitHub_Teslim` klasöründe (Python 3.10+):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ml/requirements.txt
python -m ml.prepare_icbhi --data data/icbhi --out ml/outputs
python -m ml.eda --cycles ml/outputs/cycles.csv --out ml/outputs/eda
python -m ml.train_e0 --cycles ml/outputs/cycles.csv --out ml/outputs/E0
python -m ml.compare
```

E1/E2 MobileNetV3 deneyleri için uygun PyTorch/torchvision kurulumu ve yeterli GPU önerilir:

```powershell
python -m pip install torch torchvision
python -m ml.train_e1_e2 --cycles ml/outputs/cycles.csv --out ml/outputs/mobile --epochs 5
python -m ml.compare
```

- `cycles.csv`: sabit hasta ayrımı + anotasyon döngüleri; `summary.json`: gerçek kişi/kayıt/döngü sayıları.
- `excluded.json`: anotasyon eşleşmesi/bozuk WAV nedenleri.
- `ml/outputs/E0/E0_metrics.json`: yalnız E0 çalıştırılınca oluşur.
- `ml/outputs/mobile/E1_metrics.json`, `E2_metrics.json`: iki derin öğrenme deneyi tamamlanınca oluşur.
- `experiments/comparison.md/csv/json`: yalnız mevcut ölçümleri birleştirir; eksikleri **beklemede** gösterir.

**Önemli deney kararları:** Hastalar çakışmaz; test ayrımı ilk hazırlıkta dondurulur. E1/E2 aynı ağın ağırlık başlatımı, epoch, optimizer ve veri bölmelerini kullanır. Yalnız E2'ye eğitim sırasında beyaz gürültü karıştırılır; testte her döngü aynı deterministik temiz/20/10 dB gürültülü sürüme sahiptir. Bu deney **gerçek telefon mikrofonu alan kayması** ölçümü değildir. Hastaya göre bootstrap, sınıf dengesizliğinde güven aralığı sunar. Başarı hedefi garanti değildir.

**Sınırlılık:** Cycle'ın çok uzun olduğu nadir durumda giriş en fazla 8 saniyeye kırpılır. E1/E2 için Log-Mel zaman ekseni sabit 128 frame'e örneklenir. Bu dönüşüm kısa olayları etkileyebilir; raporda açıklanmalıdır. Ders kapsamında veri alındıktan sonra bölme dağılımını ve sınıf mevcudiyetini gözden geçirin fakat test sonuçlarına göre bölmeyi değiştirmeyin.
