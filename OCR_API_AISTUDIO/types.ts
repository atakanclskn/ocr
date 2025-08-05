
export enum ProcessingStep {
  IDLE = 'IDLE',
  UPLOADING = 'UPLOADING',
  POLLING_OCR = 'POLLING_OCR',
  ANALYZING = 'ANALYZING',
  SUCCESS = 'SUCCESS',
  ERROR = 'ERROR',
}

export interface DeclarationData {
  [key: string]: string;
  'Alıcı'?: string;
  'ALICI VKN'?: string;
  'KONTEYNER NO'?: string;
  'Teslim şekli'?: string;
  'Brüt KG'?: string;
  'SON AMBAR'?: string;
  'ÖZET BEYAN NO'?: string;
  'BEYANNAME TESCİL TARİHİ'?: string;
  'TAREKS-TARIM-TSE'?: string;
}

export interface OcrStatusResponse {
  status: string;
  documents?: {
    textAnnotation?: {
      Pages?: {
        Words?: {
          Text?: string;
        }[];
      }[];
    };
  }[];
  error?: string;
  progress?: number;
}
