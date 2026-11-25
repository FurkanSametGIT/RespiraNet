# Deney sonuçları

Bu klasörde **önceden ölçülmüş hiçbir metrik yoktur**. ICBHI 2017 verisini edinmeden bilimsel sonuç üretilemez.

`python -m ml.prepare_icbhi`, `python -m ml.train_e0`, `python -m ml.train_e1_e2` ve `python -m ml.compare` gerçek veri üzerinde başarıyla tamamlandığında oluşturulacak dosyalar:

- `comparison.csv` / `comparison.md` / `comparison.json`: sadece gerçekten ölçülmüş E0/E1/E2 sonuçları.
- Bekleyen E1/E2 deneyleri karşılaştırma raporunda açıkça belirtilir.
- Ham hasta sesleri ve model ağırlıkları GitHub'da yayımlanmamalıdır.

**Tüm test koşulları aynı hasta bazlı ayrımdan gelmelidir.** Sesin temiz, 20 dB ve 10 dB gürültülü sürümleri bağımsız örnek sayılamaz.
