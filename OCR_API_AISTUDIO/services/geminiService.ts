import { GoogleGenAI, Type } from "@google/genai";
import { DeclarationData } from '../types';

if (!process.env.API_KEY) {
  throw new Error("Gemini API Anahtarı (API_KEY) bulunamadı.");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
const model = "gemini-2.5-flash";

const responseSchema = {
    type: Type.OBJECT,
    properties: {
        'Alıcı': { type: Type.STRING, description: 'İthalatçı firma adı' },
        'ALICI VKN': { type: Type.STRING, description: 'Alıcı firma vergi kimlik numarası (10 veya 11 haneli sayı)' },
        'KONTEYNER NO': { type: Type.STRING, description: 'Konteyner numarası (varsa, yoksa "Belirtilmemiş")' },
        'Teslim şekli': { type: Type.STRING, description: 'Teslim şekli bilgisi (örn: EXW, FCA, FOB, CIF vb.)' },
        'Brüt KG': { type: Type.STRING, description: 'Brüt ağırlık kilogram cinsinden' },
        'SON AMBAR': { type: Type.STRING, description: 'Gümrük müdürlüğü adı' },
        'ÖZET BEYAN NO': { type: Type.STRING, description: 'Beyanname numarası' },
        'BEYANNAME TESCİL TARİHİ': { type: Type.STRING, description: 'Beyanname tescil tarihi' },
        'TAREKS-TARIM-TSE': { type: Type.STRING, description: 'Belgelerde TAREKS, TARIM veya TSE ibaresi geçiyorsa "VAR", geçmiyorsa "YOK" yaz' },
    },
};

const getPrompt = (ocrText: string) => `
Sen bir gümrük beyannamesi uzmanısın. Sağlanan OCR metnini analiz et ve talep edilen bilgileri JSON formatında çıkar.
Metinde bulunamayan alanlar için "Belirtilmemiş" veya "Yok" gibi uygun bir metin kullan.

OCR Metni:
---
${ocrText}
---
`;


export async function analyzeText(text: string): Promise<DeclarationData> {
  const prompt = getPrompt(text);
  
  try {
    const response = await ai.models.generateContent({
      model: model,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: responseSchema,
      }
    });
    
    const responseText = response.text;
    if (!responseText) {
      throw new Error("Gemini API'den boş yanıt alındı.");
    }
    
    const jsonData = JSON.parse(responseText);

    // Create a result object that matches the DeclarationData interface,
    // ensuring all keys from the schema are present.
    const result: DeclarationData = {};
    for (const key in responseSchema.properties) {
        if (Object.prototype.hasOwnProperty.call(responseSchema.properties, key)) {
             result[key] = jsonData[key] || 'N/A';
        }
    }
    
    return result;

  } catch (error) {
    console.error("Gemini API Error:", error);
    if (error instanceof SyntaxError) {
      throw new Error("Gemini API'den gelen JSON yanıtı ayrıştırılamadı.");
    }
    throw new Error("Gemini API ile veri analiz edilirken bir hata oluştu.");
  }
}
