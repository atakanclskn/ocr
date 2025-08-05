
import React from 'react';
import { ProcessingStep } from '../types';
import { SpinnerIcon } from './Icons';

interface StatusIndicatorProps {
  step: ProcessingStep;
  progress: number;
}

const statusMessages: Record<ProcessingStep, string> = {
  [ProcessingStep.UPLOADING]: "Dosya yükleniyor...",
  [ProcessingStep.POLLING_OCR]: "Görsel işleniyor ve metin çıkarılıyor...",
  [ProcessingStep.ANALYZING]: "AI ile beyanname verileri analiz ediliyor...",
  [ProcessingStep.IDLE]: "Bekleniyor",
  [ProcessingStep.SUCCESS]: "Başarılı",
  [ProcessingStep.ERROR]: "Hata",
};

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ step, progress }) => {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 bg-gray-800 rounded-lg shadow-2xl">
      <SpinnerIcon className="w-16 h-16 text-blue-500 mb-6" />
      <h2 className="text-2xl font-bold text-gray-100 mb-2">{statusMessages[step]}</h2>
      <p className="text-gray-400">Bu işlem birkaç dakika sürebilir. Lütfen bekleyiniz.</p>
      {step === ProcessingStep.POLLING_OCR && (
        <div className="w-full bg-gray-700 rounded-full h-2.5 mt-6">
          <div 
            className="bg-blue-600 h-2.5 rounded-full transition-all duration-500" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}
    </div>
  );
};

export default StatusIndicator;
