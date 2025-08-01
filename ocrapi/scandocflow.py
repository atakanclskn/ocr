import requests
import time
import json

API_KEY = "lHHnyClmPHpxAPMCLDqDtMykU8U2kON7lLG9TOuRVNtV4cHxVtCOTaxIXjkCiBQE"
UPLOAD_URL = "https://backend.scandocflow.com/v1/api/documents/extractAsync"
STATUS_URL = "https://backend.scandocflow.com/v1/api/documents/status"
file_path = "./image8.jpg"

# OCR işlemi için parametreler
payload = {
    "type": "ocr",
    "lang": "tur",
    "retain": "true",
}

# Dosya yükleyip OCR işlemini başlat
print("Dosya yükleniyor...")
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
                    
                    # Metni dosyaya kaydet
                    with open("ocr_result.txt", "w", encoding="utf-8") as f:
                        f.write(all_text)
                    print("✅ Metin 'ocr_result.txt' dosyasına kaydedildi.")
                    
                    # İlk 500 karakteri göster
                    print("\n--- Çıkarılan Metin (İlk 500 karakter) ---")
                    print(all_text[:500] + "..." if len(all_text) > 500 else all_text)
                    print("--- Metin Sonu ---")
                    
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
                    with open("api_full_response.json", "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print("Tam API yanıtı 'api_full_response.json' dosyasına kaydedildi.")
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
    
print("\n\nİşlem tamamlandı.")