import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud, FiFileText, FiCheckCircle } from 'react-icons/fi';

export default function UploadSection({ onFileUpload, file }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024 // 5MB
  });

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-slate-800 tracking-tight">1. Upload Resume</h2>
      <div 
        {...getRootProps()} 
        className={`relative overflow-hidden border-2 border-dashed rounded-[2rem] p-12 text-center cursor-pointer transition-all duration-500 group ${
          isDragActive 
            ? 'border-blue-500 bg-blue-50/50 scale-[1.01]' 
            : 'border-slate-200 bg-slate-50/30 hover:border-blue-400 hover:bg-white hover:shadow-2xl hover:shadow-blue-500/5'
        }`}
      >
        <input {...getInputProps()} />
        
        {/* Animated Background Decor */}
        <div className={`absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

        <div className="relative z-10">
          <div className={`w-20 h-20 mx-auto mb-6 rounded-[1.5rem] flex items-center justify-center transition-all duration-500 ${
            file ? 'bg-emerald-100' : 'bg-blue-100 group-hover:scale-110 group-hover:rotate-3'
          }`}>
            {file ? (
              <FiCheckCircle className="text-4xl text-emerald-600" />
            ) : (
              <FiUploadCloud className="text-4xl text-blue-600" />
            )}
          </div>
          
          {isDragActive ? (
            <p className="text-blue-600 font-bold text-xl animate-pulse">Drop the resume here</p>
          ) : (
            <div className="space-y-2">
              <p className="text-slate-700 text-xl font-medium">
                {file ? file.name : <>Drag & drop resume, or <span className="text-blue-600">browse</span></>}
              </p>
              <p className="text-slate-400 font-medium">Supports PDF and TXT up to 5MB</p>
            </div>
          )}
        </div>
      </div>

      {file && (
        <div className="flex items-center p-4 bg-emerald-50/50 border border-emerald-100 text-emerald-700 rounded-2xl animate-in fade-in slide-in-from-top-2 duration-500">
          <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center mr-4">
            <FiFileText className="text-xl" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold uppercase tracking-wider opacity-60">Ready to tailor</p>
            <p className="font-semibold truncate max-w-xs">{file.name}</p>
          </div>
          <button 
            onClick={(e) => { e.stopPropagation(); onFileUpload(null); }}
            className="p-2 hover:bg-emerald-100 rounded-lg transition-colors text-emerald-600 font-bold text-sm"
          >
            Change
          </button>
        </div>
      )}
    </div>
  );
}
