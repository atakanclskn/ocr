import { OcrStatusResponse } from '../types';
import { UPLOAD_URL, STATUS_URL, MAX_POLL_TIME_MS, POLL_INTERVAL_MS } from '../constants';

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export async function uploadAndPoll(
  file: File,
  apiKey: string,
  onProgress: (progress: number) => void
): Promise<string> {
  if (!apiKey) {
    throw new Error("Scandocflow API anahtarı sağlanmadı.");
  }
  
  // 1. Upload file and start OCR process
  const formData = new FormData();
  formData.append('files', file);
  formData.append('type', 'ocr');
  formData.append('lang', 'tur');
  formData.append('retain', 'true');

  const uploadResponse = await fetch(`${UPLOAD_URL}?access_token=${apiKey}`, {
    method: 'POST',
    body: formData,
  });

  if (!uploadResponse.ok) {
     const errorBody = await uploadResponse.text();
     console.error("Upload error body:", errorBody);
     throw new Error(`Dosya yükleme hatası: ${uploadResponse.status} ${uploadResponse.statusText}`);
  }

  const uploadResult = await uploadResponse.json();
  const requestId = uploadResult.id;
  if (!requestId) {
    throw new Error('API yanıtından Request ID alınamadı.');
  }

  // 2. Poll for status
  let timeWaited = 0;
  while (timeWaited < MAX_POLL_TIME_MS) {
    const statusResponse = await fetch(`${STATUS_URL}?access_token=${apiKey}&request_id=${requestId}`);
    
    if (!statusResponse.ok) {
      // 404 can mean the job is done and cleaned up, but we should handle it gracefully
      if(statusResponse.status === 404) {
          throw new Error('İşlem durumu kontrol edilemedi (404). Request ID geçersiz veya işlem tamamlanıp silinmiş olabilir.');
      }
      const errorBody = await statusResponse.text();
      console.error("Status error body:", errorBody);
      throw new Error(`Durum kontrol hatası: ${statusResponse.status} ${statusResponse.statusText}`);
    }

    const result: OcrStatusResponse = await statusResponse.json();
    const status = result.status.toLowerCase();

    if (result.progress) {
      onProgress(result.progress);
    }
    
    if (status === 'success' || status === 'completed') {
      const allText = extractTextFromResponse(result);
      if (!allText) {
        throw new Error('İşlem başarılı ancak dokümandan metin çıkarılamadı.');
      }
      onProgress(100);
      return allText;
    }

    if (status === 'failed' || status === 'error') {
      throw new Error(`OCR işlemi başarısız oldu: ${result.error || 'Bilinmeyen hata'}`);
    }

    await sleep(POLL_INTERVAL_MS);
    timeWaited += POLL_INTERVAL_MS;
  }

  throw new Error('OCR işlemi zaman aşımına uğradı.');
}

function extractTextFromResponse(response: OcrStatusResponse): string {
    if (!response.documents || response.documents.length === 0) {
        return "";
    }

    let allText = "";
    response.documents.forEach(doc => {
        const pages = doc.textAnnotation?.Pages || [];
        pages.forEach(page => {
            const words = page.Words || [];
            const pageText = words.map(word => word.Text || "").join(" ");
            allText += pageText + "\n\n";
        });
    });

    return allText.trim();
}