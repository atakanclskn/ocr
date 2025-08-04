# ScanDocFlow OCR ve Beyanname İşleme Sistemi

Bu proje, gümrük beyannamelerinin OCR ile okunması ve Excel'e otomatik aktarılması için geliştirilmiştir.

## 🚀 Özellikler

- 📸 Görsel dosyalardan OCR ile metin çıkarma
- 🤖 Gemini AI ile beyanname bilgilerini otomatik tanıma
- 📊 Excel şablonuna otomatik veri aktarımı
- 🔒 Environment variables ile güvenli API key yönetimi

## 📋 Gereksinimler

- Python 3.8+
- pip (Python paket yöneticisi)

## 🛠️ Kurulum

1. **Repoyu klonlayın:**
```bash
git clone https://github.com/kullaniciadi/scandocflow-ocr.git
cd scandocflow-ocr
```

2. **Gerekli kütüphaneleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Environment variables ayarlayın:**
   - `.env.example` dosyasını `.env` olarak kopyalayın
   - Gemini API key'inizi ekleyin
```bash
cp .env.example .env
# .env dosyasını düzenleyip API key'inizi ekleyin
```

4. **Excel şablonunu hazırlayın:**
   - `beyanname şablon.xlsx` dosyasının proje klasöründe olduğundan emin olun

## 🔑 API Key Alma

### Gemini API Key:
1. https://makersuite.google.com/app/apikey adresine gidin
2. Google hesabınızla giriş yapın
3. "Create API Key" butonuna tıklayın
4. API key'i `.env` dosyasına ekleyin

## 💻 Kullanım

```bash
python scandocflow.py
```

Program otomatik olarak:
1. `image8.jpg` dosyasını OCR ile okur
2. Beyanname bilgilerini çıkarır
3. Excel şablonunu doldurur
4. Sonuçları ekranda gösterir

## 📁 Dosya Yapısı

```
scandocflow-ocr/
├── scandocflow.py          # Ana program
├── beyanname şablon.xlsx   # Excel şablonu
├── .env                    # API anahtarları (gitignore'da)
├── .env.example            # Örnek environment dosyası
├── .gitignore              # Git ignore listesi
├── requirements.txt        # Python bağımlılıkları
└── README.md              # Bu dosya
```

## 🔧 Yapılandırma

### Gemini Model Seçimi
Kodda farklı Gemini modelleri kullanabilirsiniz:
- `gemini-1.5-pro` - En güçlü model (varsayılan)
- `gemini-1.5-flash` - Hızlı model
- `gemini-2.0-flash-exp` - Deneysel model

### Görsel Dosya
Varsayılan olarak `image8.jpg` dosyası işlenir. Farklı bir dosya kullanmak için:
```python
file_path = "./dosyaniz.jpg"
```

## 📊 Çıktılar

Program şu bilgileri otomatik çıkarır ve Excel'e aktarır:
- Alıcı firma adı
- Alıcı VKN (Vergi Kimlik No)
- Konteyner No
- Teslim şekli
- Brüt KG
- Son ambar
- Özet beyan no
- Beyanname tescil tarihi
- TAREKS-TARIM-TSE durumu

## 🐛 Sorun Giderme

### "Gemini API kütüphanesi kurulu değil" hatası
```bash
pip install google-generativeai
```

### "Excel şablonu bulunamadı" hatası
`beyanname şablon.xlsx` dosyasının kod ile aynı klasörde olduğundan emin olun.

### API anahtarı hatası
`.env` dosyasında `GEMINI_API_KEY` değerinin doğru ayarlandığından emin olun.

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'e push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın