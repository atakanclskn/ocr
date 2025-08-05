import React, { useState } from 'react';
import { KeyIcon } from './Icons';

interface ApiKeyInputProps {
  onSave: (key: string) => void;
  error: string | null;
}

const ApiKeyInput: React.FC<ApiKeyInputProps> = ({ onSave, error }) => {
  const [key, setKey] = useState('');

  const handleSaveClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    onSave(key);
  };
  
  const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSave(key);
  }

  return (
    <div className="w-full max-w-md mx-auto bg-gray-800 rounded-xl shadow-2xl p-8 text-center animate-fade-in">
      <KeyIcon className="w-12 h-12 text-blue-400 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-gray-100 mb-2">ScanDocFlow API Anahtarı</h2>
      <p className="text-gray-400 mb-6">
        Devam etmek için lütfen Scandocflow API anahtarınızı girin. Bu anahtar tarayıcınızda saklanacaktır.
      </p>
      <form onSubmit={handleFormSubmit} className="space-y-4">
        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="API anahtarınızı buraya yapıştırın"
          className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="ScanDocFlow API Key"
        />
        <button
          type="submit"
          onClick={handleSaveClick}
          className="w-full bg-blue-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-blue-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        >
          Kaydet ve Devam Et
        </button>
      </form>
      {error && (
        <div className="mt-4 text-red-400 bg-red-900/50 p-3 rounded-lg">
            <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default ApiKeyInput;
