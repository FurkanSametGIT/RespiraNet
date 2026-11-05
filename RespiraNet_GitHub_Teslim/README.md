# RespiraNet

**Solunum Seslerinde Hırıltı ve Çıtırtının Sınıflandırılması ve Gürültüye Dayanıklılığın İncelenmesi**

Yapay Zeka ve Veri Mühendisliği Tasarımı — 1. ve 2. hafta diyagram / mockup / veritabanı dokümantasyon paketi.

**Proje üyeleri:** 230291009 Furkan Tekin · 230291034 Abdulsamet Karayel  
**Durum:** Dokümantasyon ve tasarım aşaması. Buradaki ekranlar gerçek çalışan model veya klinik ürün değildir.

## Hafta 1 · Diyagramlar ve isterler

**Altı diyagram tamamlandı** ve kaynak dosyalarıyla birlikte eklendi.

1. [Use Case diyagramı](docs/hafta-1/diyagramlar/01_use_case.svg)
2. [Sistem mimarisi](docs/hafta-1/diyagramlar/02_sistem_mimarisi.svg)
3. [Akış 1 — WAV yükleme / kalite kontrol](docs/hafta-1/diyagramlar/03_akis_ses_yukleme.svg)
4. [Akış 2 — Veri hazırlama / eğitim](docs/hafta-1/diyagramlar/04_akis_egitim.svg)
5. [Akış 3 — Sonuç / geçmiş / silme](docs/hafta-1/diyagramlar/05_akis_sonuc_gecmis.svg)
6. [AI Pipeline diyagramı](docs/hafta-1/diyagramlar/06_ai_pipeline.svg)

[Hafta 1 ayrıntıları](docs/hafta-1/README.md)

## Hafta 2 · Veritabanı ve Figma

- [ER Diyagramı](docs/hafta-2/diyagramlar/07_er_diyagrami.svg)
- [PostgreSQL SQL şeması](db/schema.sql)
- [Veri sözlüğü](docs/hafta-2/veri-sozlugu.md)
- [Teknoloji yığını tablosu](docs/hafta-2/teknoloji-yigini.md)
- [6 ekranlık Figma aktarım klasörü](docs/hafta-2/figma-svg/)
- [Tıklanabilir HTML prototipi](docs/hafta-2/prototip/index.html)
- [Figma'ya aktarma ve ekran bağlantıları](docs/hafta-2/figma-svg/FIGMA_AKTARIM.md)
- [Hafta 2 ayrıntıları](docs/hafta-2/README.md)

| Ekran | Önizleme |
|---|---|
| Giriş | [01_login.png](docs/hafta-2/figma-svg/01_login.png) |
| Ana Panel | [02_dashboard.png](docs/hafta-2/figma-svg/02_dashboard.png) |
| Ses Yükleme | [03_upload.png](docs/hafta-2/figma-svg/03_upload.png) |
| Analiz Sonucu | [04_result.png](docs/hafta-2/figma-svg/04_result.png) |
| Kayıt Geçmişi | [05_history.png](docs/hafta-2/figma-svg/05_history.png) |
| Model Deneyleri | [06_models.png](docs/hafta-2/figma-svg/06_models.png) |

## Araştırmanın ana sorusu

**E1 (temiz veriyle eğitim) ile E2 (aynı modelin eğitimine gürültü eklenmesi) arasında 10 dB SNR koşulunda anormal ses duyarlılığı açısından fark var mı?**

- **E0:** MFCC + SVM (başlangıç modeli).
- **E1:** Log-Mel + MobileNetV3-Small (temiz eğitim).
- **E2:** Aynı model ve ayarlarla yalnız eğitim sırasında kontrollü gürültü artırma.
- **Veri:** ICBHI 2017, hasta bazlı sabit train / validation / test.
- **Ölçüm:** Dört sınıflı Macro-F1, anormal olay duyarlılığı (Se), normal ses özgüllüğü (Sp), ICBHI skoru; temiz/20/10 dB test.

Öneride belirtilen hedefler **araştırma hedefidir**, ölçülmüş başarı değildir. Telefon/harici seslerin ICBHI ile aynı alanda olduğu varsayılmaz. Uygulama **hastalık teşhisi veya tıbbi öneri vermez**.

## GitHub'a yükleme

Bu klasör yerel olarak hazırlandı. **GitHub hesabına otomatik yüklenmedi.** Yeni bir repo oluşturup bu klasörü onun kökü olarak kullanın.

```bash
cd RespiraNet_GitHub_Teslim
git init
git add .
git commit -m "docs: RespiraNet hafta 1-2 diyagram, ER, mockup, SQL ve issue taslakları"
# GitHub'da boş bir repo açın, ardından kendi repo adresinizi kullanın:
git branch -M main
git remote add origin https://github.com/KULLANICI_ADI/RespiraNet.git
git push -u origin main
```

İki öğrencinin de git commit geçmişinin görünmesi için daha sonra arkadaşınızı **repo collaborator** olarak ekleyin. Kişi bilgisi, özel veriler, ham ICBHI ses dosyaları ve model ağırlıkları repoya yüklenmemelidir. `.gitignore` buna yardımcı olacak biçimde hazırlanmıştır.

## GitHub Issues aktarımı

`issues.json` ve `issues.csv` içinde toplam **21 taslak görev** vardır (ilk hafta 6 diyagram, ikinci hafta Figma/DB işleri, FR ve NFR isterleri). Aşağıdaki betik, **önizleme modunda** başlar:

```bash
python scripts/create_github_issues.py --repo KULLANICI_ADI/RespiraNet
# GitHub CLI kurulu, giriş yapılmış ve repo gerçekten oluşturulduktan sonra:
python scripts/create_github_issues.py --repo KULLANICI_ADI/RespiraNet --apply
```

`--apply` gerçek GitHub issue açar ve aynı başlıktaki mevcut issue'ları tekrar açmaz. GitHub CLI gerektirir (`gh auth login`). Betik otomatik çalıştırılmadı.

## Düzenleme / yeniden çizme

- `.dot` dosyaları [Graphviz](https://graphviz.org) ile yeniden oluşturulabilir: `dot -Tsvg diagram.dot -o diagram.svg`.
- `.mmd` dosyaları Mermaid kaynağıdır. GitHub Markdown'a Mermaid kod bloğu olarak gömülebilir.
- SVG ekranlar Figma içine alınabilir; gerçek **Figma dosyası ve Prototype bağlantıları** Figma editöründe oluşturulmalıdır.
- `docs/hafta-2/prototip/index.html` internet gerektirmeyen, tek dosyalı bir prototiptir; altı ekran etkileşimi içerir. Analiz, giriş ve veri saklama işlemleri yalnız simülasyondur.

## Dosya yapısı

```text
RespiraNet_GitHub_Teslim/
├── README.md
├── docs/
│   ├── respiranet_son_oneri_formu.docx
│   ├── hafta-1/
│   │   ├── README.md
│   │   └── diyagramlar/       # 6 x (.dot + .mmd + .svg + .png)
│   └── hafta-2/
│       ├── README.md
│       ├── diyagramlar/       # ER (.dot + .mmd + .svg + .png)
│       ├── figma-svg/        # 6 SVG + PNG, Figma aktarım rehberi
│       ├── prototip/         # tıklanabilir index.html
│       ├── veri-sozlugu.md
│       └── teknoloji-yigini.md
├── db/schema.sql
├── issues.json
├── issues.csv
├── scripts/create_github_issues.py
└── .github/ISSUE_TEMPLATE/
```
