
import React, { useState, useCallback } from 'react';
import { UploadIcon } from './Icons';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  disabled: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, disabled }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [onFileSelect]);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  return (
    <div
      className={`relative w-full p-8 border-2 border-dashed rounded-xl transition-colors duration-300 ${
        isDragging ? 'border-blue-500 bg-gray-800' : 'border-gray-600 hover:border-blue-600'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
    >
      <input
        type="file"
        id="file-upload"
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        onChange={handleFileChange}
        accept="image/jpeg,image/png,image/jpg,application/pdf"
        disabled={disabled}
      />
      <label htmlFor="file-upload" className="flex flex-col items-center justify-center text-center">
        <UploadIcon className="w-12 h-12 mb-4 text-gray-400" />
        <p className="text-xl font-semibold text-gray-300">Dosyayı sürükleyip bırakın</p>
        <p className="text-gray-500">veya seçmek için tıklayın</p>
        <p className="text-xs text-gray-600 mt-4">Desteklenen formatlar: JPG, PNG, PDF</p>
      </label>
    </div>
  );
};

export default FileUpload;
