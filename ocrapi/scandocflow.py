# Gerekli kütüphaneleri import et
# Not: Kurulum için: pip install google-generativeai openpyxl python-dotenv
import requests
import time
import json
import os
from datetime import datetime

# .env dosyasını yükle
load_dotenv()
print("\n📋 Sistem Kontrolü:")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️  python-dotenv kütüphanesi kurulu değil!")
    print("   Kurmak için: pip install python-dotenv")
    print("   Environment variables sistem üzerinden ayarlanmalı.\n")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini API kütüphanesi kurulu değil!")
    print("   Kurmak için: pip install google-generativeai")
    print("   OCR işlemi devam edecek ancak Gemini analizi yapılamayacak.\n")

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("⚠️  OpenPyXL kütüphanesi kurulu değil!")
    print("   Kurmak için: pip install openpyxl")
    print("   Excel çıktısı oluşturulamayacak.\n")

API_KEY = os.getenv("SCANDOCFLOW_API_KEY", "rtsuU4o3Cpyhhmc8JoGVotVQTYUanls0mPg8moTNRHaEvJfeS6j4C123e0lbFHfD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBnPw6fjlSk4BDDLAG-IbQItB5N03ZmqPs")
UPLOAD_URL = "https://backend.scandocflow.com/v1/api/documents/extractAsync"
STATUS_URL = "https://backend.scandocflow.com/v1/api/documents/status"
file_path = os.getenv("OCR_FILE_PATH", "./image8.jpg")  # Dosya yolu da env'den alınabilir
excel_template_path = os.getenv("EXCEL_TEMPLATE_PATH", "./beyanname şablon.xlsx")

# Gemini API yapılandırması
if GEMINI_AVAILABLE and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=GEMINI_API_KEY)
print(f"✅ API anahtarları yüklendi.")
print(f"📁 OCR dosyası: {file_path}")
print(f"📊 Excel şablonu: {excel_template_path}\n")

# OCR işlemi için parametreler
payload = {
    "type": "ocr",
    "lang": "tur",
    "retain": "true",
}

# Dosya kontrolü
if not os.path.exists(file_path):
    print(f"❌ Hata: '{file_path}' dosyası bulunamadı!")
    print("   Lütfen OCR yapılacak görsel dosyasını kontrol edin.")
    exit()

# Dosya yükleyip OCR işlemini başlat
print(f"📸 Dosya yükleniyor: {file_path}")
with open(file_path, "rb") as file:
    response = requests.post(
        UPLOAD_URL,
        params={"access_token": API_KEY},
        data=payload,
        files={"files": file}
    )

print(f"Upload yanıt kodu: {response.status_code}")
print(f"Upload yanıtı: {response.text}")

if response.status_code == 200:
    result = response.json()
    request_id = result.get("id")
    
    if not request_id:
        print("Request ID bulunamadı. Tam yanıt:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        exit()
    
    print(f"İşlem başladı, Request ID: {request_id}")
    print(f"Status: {result.get('status')}")
    
    if result.get("webhook"):
        print(f"Webhook durumu: {result['webhook'].get('status')}")
else:
    print(f"Yükleme sırasında hata: {response.status_code}, {response.text}")
    exit()

# İşlem tamamlanana kadar status kontrolü yap
print("\nOCR işlemi devam ediyor, status kontrol ediliyor...")

max_wait_time = 120  # 2 dakika (dokümantasyonda 2 dakikaya kadar sürebileceği belirtilmiş)
time_waited = 0
interval = 5
success = False

while time_waited < max_wait_time:
    print(f"\n[{time_waited}s] Status kontrol ediliyor...")
    
    # Status kontrolü için doğru endpoint ve parametreler
    status_params = {
        "access_token": API_KEY,
        "request_id": request_id
    }
    
    response = requests.get(STATUS_URL, params=status_params)
    
    print(f"Status yanıt kodu: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        status = result.get("status", "").lower()
        
        print(f"İşlem durumu: {status}")
        
        if status == "success" or status == "completed":
            print("\nOCR işlemi başarıyla tamamlandı!")
            
            # Webhook durumunu kontrol et
            if result.get("webhook"):
                webhook_status = result["webhook"].get("status")
                print(f"Webhook durumu: {webhook_status}")
            
            # Dokümanları işle
            documents = result.get("documents", [])
            
            if documents:
                print(f"\n{len(documents)} doküman bulundu.")
                
                all_text = ""
                
                for idx, doc in enumerate(documents):
                    print(f"\n--- Doküman {idx + 1} ---")
                    print(f"Tip: {doc.get('type')}")
                    
                    # textAnnotation içindeki metni çıkar
                    text_annotation = doc.get("textAnnotation", {})
                    pages = text_annotation.get("Pages", [])
                    
                    doc_text = ""
                    
                    for page_idx, page in enumerate(pages):
                        print(f"Sayfa {page_idx + 1}: {len(page.get('Words', []))} kelime bulundu")
                        
                        words = page.get("Words", [])
                        
                        # Kelimeleri birleştir
                        page_text = " ".join([word.get("Text", "") for word in words])
                        doc_text += page_text + "\n\n"
                    
                    all_text += f"=== Doküman {idx + 1} ===\n{doc_text}\n\n"
                
                if all_text.strip():
                    print(f"\nToplam {len(all_text)} karakter metin çıkarıldı.")
                    
                    # Dosya adını ve tarih bilgisini hazırla
                    base_filename = os.path.basename(file_path)
                    name_without_ext = os.path.splitext(base_filename)[0]
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    
                    # İlk 500 karakteri göster
                    print("\n--- Çıkarılan Metin (İlk 500 karakter) ---")
                    print(all_text[:500] + "..." if len(all_text) > 500 else all_text)
                    print("--- Metin Sonu ---")
                    
                    # OCR sonucunu Gemini'ye gönder
                    if GEMINI_AVAILABLE and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
                        print("\n\n📤 Beyanname bilgileri çıkarılıyor...")
                        
                        try:
                            # Gemini model oluştur (güncel model adını kullan)
                            # Mevcut modeller: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp
                            model = genai.GenerativeModel('gemini-1.5-pro')  # En güçlü model
                            
                            # Prompt hazırla
                            prompt = f"""
                            Sen bir gümrük beyannamesi uzmanısın. Aşağıdaki OCR ile çıkarılmış beyanname metnini analiz et ve sadece istenen bilgileri çıkar.
                            
                            İstenen bilgiler ve açıklamaları:
                            - Alıcı: İthalatçı firma adı
                            - ALICI VKN: Alıcı firma vergi kimlik numarası (10 veya 11 haneli sayı)
                            - KONTEYNER NO: Konteyner numarası (varsa)
                            - Teslim şekli: Teslim şekli bilgisi (örn: EXW, FCA, FOB, CIF vb.)
                            - Brüt KG: Brüt ağırlık kilogram cinsinden
                            - SON AMBAR: Gümrük müdürlüğü adı
                            - ÖZET BEYAN NO: Beyanname numarası
                            - BEYANNAME TESCİL TARİHİ: Beyanname tescil tarihi
                            - TAREKS-TARIM-TSE: Belgelerde TAREKS, TARIM veya TSE ibaresi geçiyorsa VAR, geçmiyorsa YOK yaz
                            
                            ÇIKTI FORMATI (SADECE BU FORMATTA YAZ, BAŞKA BİR ŞEY EKLEME):
                            Alıcı: [değer]
                            ALICI VKN: [değer]
                            KONTEYNER NO: [değer veya "Belirtilmemiş"]
                            Teslim şekli: [değer veya "Belirtilmemiş"]
                            Brüt KG: [değer veya "Belirtilmemiş"]
                            SON AMBAR: [değer]
                            ÖZET BEYAN NO: [değer]
                            BEYANNAME TESCİL TARİHİ: [değer]
                            TAREKS-TARIM-TSE: [VAR veya YOK]
                            
                            OCR Metni:
                            {all_text}
                            """
                            
                            # Gemini'ye gönder
                            response = model.generate_content(prompt)
                            
                            # Gemini yanıtını göster
                            gemini_text = response.text if hasattr(response, 'text') else str(response)
                            print("\n✅ Gemini API yanıtı alındı!")
                            print("\n" + "="*50)
                            print("BEYANNAME BİLGİLERİ (EXCEL FORMATI):")
                            print("="*50)
                            print(gemini_text)
                            print("="*50)
                            
                            # Excel şablonuna verileri yaz
                            if EXCEL_AVAILABLE:
                                try:
                                    # Gemini yanıtını parse et
                                    lines = gemini_text.strip().split('\n')
                                    data_dict = {}
                                    for line in lines:
                                        if ':' in line:
                                            key, value = line.split(':', 1)
                                            data_dict[key.strip()] = value.strip()
                                    
                                    print("\n📊 Çıkarılan veriler:")
                                    for key, value in data_dict.items():
                                        print(f"   {key}: {value}")
                                    
                                    # Şablon Excel dosyasını aç
                                    if os.path.exists(excel_template_path):
                                        workbook = openpyxl.load_workbook(excel_template_path)
                                        sheet = workbook.active
                                        
                                        # Sütun başlıklarını ve indekslerini bul
                                        column_mapping = {}
                                        max_col = sheet.max_column if sheet.max_column else 1
                                        for col in range(1, max_col + 1):
                                            header = sheet.cell(row=1, column=col).value
                                            if header and isinstance(header, str):
                                                header_clean = header.strip()
                                                # Tam eşleşme kontrolü
                                                if header_clean == "Alıcı D.Ö":
                                                    column_mapping["Alıcı"] = col
                                                elif header_clean == "ALICI VKN":
                                                    column_mapping["ALICI VKN"] = col
                                                elif header_clean == "KONTEYNER NO":
                                                    column_mapping["KONTEYNER NO"] = col
                                                elif header_clean == "Teslim şekli":
                                                    column_mapping["Teslim şekli"] = col
                                                elif header_clean == "Brüt KG":
                                                    column_mapping["Brüt KG"] = col
                                                elif header_clean == "SON AMBAR":
                                                    column_mapping["SON AMBAR"] = col
                                                elif header_clean == "ÖZET BEYAN NO":
                                                    column_mapping["ÖZET BEYAN NO"] = col
                                                elif header_clean == "BEYANNAME TESCİL TARİHİ":
                                                    column_mapping["BEYANNAME TESCİL TARİHİ"] = col
                                                elif header_clean == "TAREKS-TARIM-TSE (VAR-YOK)" or header_clean == "TAREKS-TARIM-TSE":
                                                    column_mapping["TAREKS-TARIM-TSE"] = col
                                        
                                        print(f"\n📋 Excel'de bulunan sütunlar: {list(column_mapping.keys())}")
                                        
                                        # İlk boş satırı bul
                                        next_row = 2
                                        max_row = sheet.max_row if sheet.max_row else 1
                                        max_col = sheet.max_column if sheet.max_column else 1
                                        for row in range(2, max_row + 2):
                                            # A sütununda (Alıcı) veri yoksa boş satırdır
                                            if column_mapping.get("Alıcı") and not sheet.cell(row=row, column=column_mapping["Alıcı"]).value:
                                                next_row = row
                                                break
                                            # Veya ilk birkaç sütunda veri yoksa
                                            elif not any(sheet.cell(row=row, column=col).value for col in range(1, min(5, max_col + 1))):
                                                next_row = row
                                                break
                                        
                                        print(f"\n📝 Veriler {next_row}. satıra yazılacak")
                                        
                                        # Verileri yaz
                                        written_count = 0
                                        for field, col in column_mapping.items():
                                            if field in data_dict:
                                                value = data_dict[field]
                                                # "Belirtilmemiş" değerini boş bırak
                                                if value.lower() != "belirtilmemiş":
                                                    sheet.cell(row=next_row, column=col).value = value
                                                    written_count += 1
                                                    print(f"   ✓ {field} → Sütun {col}: {value}")
                                        
                                        # Kayıt tarihini ekle (varsa)
                                        max_col = sheet.max_column if sheet.max_column else 1
                                        for col in range(1, max_col + 1):
                                            header = sheet.cell(row=1, column=col).value
                                            if header and isinstance(header, str) and "KAYIT TARİHİ" in header:
                                                sheet.cell(row=next_row, column=col).value = datetime.now().strftime("%d.%m.%Y")
                                                print(f"   ✓ Kayıt Tarihi → Sütun {col}: {datetime.now().strftime('%d.%m.%Y')}")
                                                break
                                        
                                        # Excel dosyasını kaydet
                                        excel_filename = f"{name_without_ext}_{timestamp}_beyanname_dolu.xlsx"
                                        workbook.save(excel_filename)
                                        workbook.close()
                                        
                                        print(f"\n✅ Excel şablonu dolduruldu: '{excel_filename}'")
                                        print(f"   Toplam {written_count} alan dolduruldu.")
                                        
                                    else:
                                        print(f"\n⚠️  Excel şablonu '{excel_template_path}' bulunamadı!")
                                        print("   Lütfen 'beyanname şablon.xlsx' dosyasını kod ile aynı klasöre koyun.")
                                        
                                        # Sadece değerleri göster
                                        print("\n📋 Çıkarılan değerler (manuel giriş için):")
                                        for key, value in data_dict.items():
                                            print(f"   {key}: {value}")
                                        
                                except Exception as e:
                                    print(f"\n❌ Excel işleme hatası: {e}")
                                    import traceback
                                    traceback.print_exc()
                            else:
                                print("\n⚠️  OpenPyXL kütüphanesi kurulu değil!")
                                print("   Excel çıktısı için: pip install openpyxl")
                            
                        except Exception as e:
                            print(f"\n❌ Gemini API hatası: {e}")
                            print("Not: API anahtarınızı ve internet bağlantınızı kontrol edin.")
                            print("Mevcut modeller: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp")
                    
                    # API'den doküman ID'sini al ve web export linkini oluştur
                    if documents:
                        first_doc = documents[0]
                        if "id" in first_doc:
                            doc_id = first_doc["id"]
                            print(f"\n📄 Doküman ID: {doc_id}")
                            print(f"🌐 Web arayüzünde görüntülemek için:")
                            print(f"   https://app.scandocflow.com/documents/{doc_id}")
                    
                    success = True
                else:
                    print("\nUYARI: Doküman bulundu ancak metin çıkarılamadı!")
                    
                    # Debug için tam yanıtı kaydet
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    debug_filename = f"api_response_{timestamp}.json"
                    with open(debug_filename, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"Tam API yanıtı '{debug_filename}' dosyasına kaydedildi.")
            else:
                print("\nUYARI: Hiç doküman bulunamadı!")
                print("Tam yanıt:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
            break
            
        elif status == "running" or status == "processing":
            print("İşlem devam ediyor...")
            
            # İşlem yüzdesini göster (varsa)
            if "progress" in result:
                print(f"İlerleme: %{result.get('progress', 0)}")
                
        elif status == "failed" or status == "error":
            print(f"\nİşlem başarısız oldu!")
            
            if "error" in result:
                print(f"Hata mesajı: {result.get('error')}")
            
            # Tam yanıtı göster
            print("Tam yanıt:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            break
            
        else:
            print(f"Bilinmeyen durum: {status}")
            print("Tam yanıt:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    else:
        print(f"Status kontrolü başarısız: {response.status_code}")
        
        try:
            error_detail = response.json()
            print(f"Hata detayı: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
        except:
            print(f"Hata metni: {response.text}")
        
        # 404 hatası alıyorsak request_id yanlış olabilir
        if response.status_code == 404:
            print("Request ID bulunamadı. İşlem silinmiş veya ID yanlış olabilir.")
            break
    
    time.sleep(interval)
    time_waited += interval

if not success:
    print(f"\n\nİşlem {max_wait_time} saniye içinde tamamlanamadı.")
    print("\nKontrol edilecekler:")
    print(f"1. Request ID: {request_id}")
    print("2. API anahtarınızın geçerli olduğundan emin olun")
    print("3. Web arayüzünde işlemin durumunu kontrol edin")
    print("4. Dosya boyutunun 50MB'ı aşmadığından emin olun")
    
print("\n" + "="*60)
print("✅ İşlem tamamlandı!")
print("="*60)