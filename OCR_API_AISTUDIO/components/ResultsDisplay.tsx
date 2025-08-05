import React from 'react';
import { DeclarationData } from '../types';
import { CheckCircleIcon, DocumentTextIcon, DownloadIcon } from './Icons';

interface ResultsDisplayProps {
  data: DeclarationData;
  rawText: string;
  onReset: () => void;
  fileName: string;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ data, rawText, onReset, fileName }) => {
  const handleDownloadCSV = () => {
    const headers = Object.keys(data).join(',');
    const values = Object.values(data).map(val => `"${String(val ?? '').replace(/"/g, '""')}"`).join(',');
    const csvContent = `data:text/csv;charset=utf-8,${headers}\n${values}`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    const safeFileName = fileName.split('.')[0];
    link.setAttribute("download", `${safeFileName}_beyanname.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-gray-800 rounded-xl shadow-2xl p-8">
      <div className="flex items-center mb-6">
        <CheckCircleIcon className="w-10 h-10 text-green-400 mr-4" />
        <h1 className="text-3xl font-bold text-gray-50">Analiz Tamamlandı</h1>
      </div>

      <div className="bg-gray-900/50 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4 text-blue-300">Çıkarılan Beyanname Bilgileri</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-y-4 gap-x-8">
          {Object.entries(data).map(([key, value]) => (
            <div key={key}>
              <p className="text-sm text-gray-400">{key}</p>
              <p className="text-lg font-medium text-gray-100">{value || 'N/A'}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <details className="bg-gray-900/50 rounded-lg">
          <summary className="cursor-pointer p-4 font-semibold text-gray-200 flex items-center justify-between hover:bg-gray-700/50 rounded-lg">
            <span>
              <DocumentTextIcon className="w-5 h-5 inline-block mr-2" />
              İşlenmiş Ham Metni Görüntüle
            </span>
            <span className="text-xs text-gray-400">Genişletmek için tıkla</span>
          </summary>
          <div className="p-4 border-t border-gray-700">
            <pre className="whitespace-pre-wrap text-sm text-gray-300 bg-gray-900 p-4 rounded-md max-h-64 overflow-y-auto">
              {rawText}
            </pre>
          </div>
        </details>
        
        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <button
            onClick={handleDownloadCSV}
            className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-green-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
          >
            <DownloadIcon className="w-5 h-5" />
            CSV Olarak İndir
          </button>
          <button
            onClick={onReset}
            className="flex-1 bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
          >
            Başka Bir Belge İşle
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;