import React, { useState, useCallback, useEffect } from 'react';
import { DeclarationData, ProcessingStep } from './types';
import { uploadAndPoll } from './services/ocrService';
import { analyzeText } from './services/geminiService';
import FileUpload from './components/FileUpload';
import StatusIndicator from './components/StatusIndicator';
import ResultsDisplay from './components/ResultsDisplay';
import ApiKeyInput from './components/ApiKeyInput';
import { ErrorIcon } from './components/Icons';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [step, setStep] = useState<ProcessingStep>(ProcessingStep.IDLE);
  const [extractedText, setExtractedText] = useState<string>('');
  const [declarationData, setDeclarationData] = useState<DeclarationData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocrProgress, setOcrProgress] = useState(0);
  const [scandocflowApiKey, setScandocflowApiKey] = useState<string | null>(null);

  useEffect(() => {
    const storedKey = localStorage.getItem('scandocflowApiKey');
    if (storedKey) {
      setScandocflowApiKey(storedKey);
    }
  }, []);

  const handleApiKeySave = (key: string) => {
    const trimmedKey = key.trim();
    if (!trimmedKey) {
      setError("API anahtarı boş olamaz.");
      return;
    }
    localStorage.setItem('scandocflowApiKey', trimmedKey);
    setScandocflowApiKey(trimmedKey);
    setError(null);
  };

  const handleChangeApiKey = () => {
    localStorage.removeItem('scandocflowApiKey');
    setScandocflowApiKey(null);
    setFile(null);
    setError(null);
  };

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
  };

  const handleReset = () => {
    setFile(null);
    setStep(ProcessingStep.IDLE);
    setExtractedText('');
    setDeclarationData(null);
    setError(null);
    setOcrProgress(0);
  };

  const progressCallback = useCallback((progress: number) => {
    setOcrProgress(progress);
  }, []);

  const handleSubmit = async () => {
    if (!file) {
      setError('Lütfen işlemek için bir dosya seçin.');
      return;
    }
    if (!scandocflowApiKey) {
      setError('Scandocflow API anahtarı ayarlanmamış.');
      return;
    }

    setError(null);
    setStep(ProcessingStep.UPLOADING);

    try {
      setStep(ProcessingStep.POLLING_OCR);
      const ocrText = await uploadAndPoll(file, scandocflowApiKey, progressCallback);
      if (!ocrText || ocrText.trim() === '') {
        throw new Error('OCR işlemi metin çıkaramadı. Lütfen görselin netliğini kontrol edin.');
      }
      setExtractedText(ocrText);
      
      setStep(ProcessingStep.ANALYZING);
      const data = await analyzeText(ocrText);
      setDeclarationData(data);

      setStep(ProcessingStep.SUCCESS);

    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'Bilinmeyen bir hata oluştu.';
      console.error(e);
      setError(errorMessage);
      setStep(ProcessingStep.ERROR);
    }
  };

  const renderContent = () => {
    if (!scandocflowApiKey) {
      return <ApiKeyInput onSave={handleApiKeySave} error={error} />;
    }

    switch (step) {
      case ProcessingStep.IDLE:
        return (
          <div className="w-full max-w-2xl">
            <h1 className="text-4xl font-bold text-center mb-2 text-gray-50">Gümrük Beyannamesi Analiz Aracı</h1>
            <p className="text-lg text-center text-gray-400 mb-8">Beyanname görselini yükleyin, verileri sizin için AI çıkarsın.</p>
            <FileUpload onFileSelect={handleFileSelect} disabled={false} />
            {file && (
              <div className="text-center mt-6">
                <p className="text-gray-300 mb-4">Seçilen Dosya: <span className="font-semibold text-gray-100">{file.name}</span></p>
                <button
                  onClick={handleSubmit}
                  className="bg-blue-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-blue-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                >
                  Analizi Başlat
                </button>
              </div>
            )}
             {error && (
              <div className="mt-4 text-center text-red-400 bg-red-900/50 p-3 rounded-lg">
                <p>{error}</p>
              </div>
            )}
          </div>
        );
      case ProcessingStep.POLLING_OCR:
      case ProcessingStep.ANALYZING:
      case ProcessingStep.UPLOADING:
        return <StatusIndicator step={step} progress={ocrProgress} />;
      case ProcessingStep.SUCCESS:
        return declarationData && (
          <ResultsDisplay 
            data={declarationData} 
            rawText={extractedText} 
            onReset={handleReset} 
            fileName={file?.name || 'document'}
          />
        );
      case ProcessingStep.ERROR:
        return (
          <div className="text-center bg-gray-800 p-8 rounded-lg shadow-2xl">
            <ErrorIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-red-400 mb-2">Hata Oluştu</h2>
            <p className="text-gray-300 bg-gray-900 p-4 rounded-md mb-6">{error}</p>
            <button
              onClick={handleReset}
              className="bg-blue-600 text-white font-bold py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Tekrar Dene
            </button>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl mx-auto">
        {renderContent()}
      </div>
       <footer className="absolute bottom-4 text-gray-500 text-sm w-full text-center">
        <span>Powered by Scandocflow & Google Gemini</span>
        {scandocflowApiKey && (step === ProcessingStep.IDLE || step === ProcessingStep.ERROR) && (
          <>
            <span className="mx-2">|</span>
            <button onClick={handleChangeApiKey} className="hover:text-gray-300 hover:underline transition-colors">
                API Anahtarını Değiştir
            </button>
          </>
        )}
      </footer>
    </div>
  );
}

export default App;