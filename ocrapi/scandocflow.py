import requests
import time
from fpdf import FPDF

API_KEY = "lHHnyClmPHpxAPMCLDqDtMykU8U2kON7lLG9TOuRVNtV4cHxVtCOTaxIXjkCiBQE"

UPLOAD_URL = "https://backend.scandocflow.com/v1/api/documents/extractAsync"

file_path = "./image6.jpg"

payload = {
    "type": "ocr",
    "lang": "tur",
    "retain": "true",
}

# Dosya yükleyip OCR işlemini başlat
with open(file_path, "rb") as file:
    response = requests.post(
        UPLOAD_URL,
        params={"access_token": API_KEY},
        data=payload,
        files={"files": file}
    )

if response.status_code == 200:
    result = response.json()
    document_id = result["id"]
    print("İşlem başladı, Document ID:", document_id)
else:
    print(f"Yükleme sırasında hata: {response.status_code}, {response.text}")
    exit()

# İşlem tamamlanana kadar bekleyip sonuçları al
RESULT_URL = f"https://backend.scandocflow.com/v1/api/documents/{document_id}"

max_wait_time = 30  # Maksimum bekleme süresi saniye cinsinden
time_waited = 0
interval = 5  # Kontrol aralığı saniye cinsinden

while time_waited < max_wait_time:
    response = requests.get(RESULT_URL, params={"access_token": API_KEY})

    if response.status_code == 200:
        result = response.json()

        if result["status"] == "completed":
            print("OCR işlemi tamamlandı.")

            # Metinleri PDF'ye dönüştür
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for page in result.get("pages", []):
                for line in page.get("lines", []):
                    pdf.multi_cell(0, 10, line.get("text", ""))

            pdf.output("ocr_result.pdf")
            print("Sonuç 'ocr_result.pdf' dosyasına kaydedildi.")
            break

        elif result["status"] == "running":
            print("İşlem devam ediyor, 5 saniye sonra tekrar denenecek...")
            time.sleep(interval)
            time_waited += interval

        else:
            print("Beklenmeyen durum:", result)
            break
    else:
        print(f"Sonuç sorgulama hatası: {response.status_code}, {response.text}")
        print("5 saniye sonra tekrar deneniyor...")
        time.sleep(interval)
        time_waited += interval
else:
    print("OCR işlemi verilen süre içinde tamamlanmadı.")