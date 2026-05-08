import React, { useRef } from 'react';
import axios from 'axios';
import { FiDownload, FiCopy, FiCheck } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';

export default function ResultViewer({ tailoredResume }) {
  const [copied, setCopied] = React.useState(false);
  const [downloading, setDownloading] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(tailoredResume);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/generate-pdf', {
        text: tailoredResume
      }, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Tailored_Resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('PDF Generation failed:', err);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  if (!tailoredResume) return null;

  return (
    <div className="mt-20 pt-16 border-t border-slate-200 animate-in fade-in slide-in-from-bottom-8 duration-1000">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-10 gap-6">
        <div>
          <h2 className="text-3xl font-black text-slate-900 tracking-tight mb-2">Tailored Resume</h2>
          <p className="text-slate-500 font-medium">Your optimized resume is ready for review.</p>
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <button 
            onClick={handleCopy}
            className="flex-1 sm:flex-none inline-flex items-center justify-center px-6 py-3 bg-white border-2 border-slate-100 hover:border-blue-500 hover:text-blue-600 text-slate-600 rounded-2xl transition-all duration-300 font-bold shadow-sm active:scale-95"
          >
            {copied ? <FiCheck className="mr-2 text-emerald-500" /> : <FiCopy className="mr-2" />}
            {copied ? 'Copied!' : 'Copy Text'}
          </button>
          <button 
            onClick={handleDownload}
            disabled={downloading}
            className={`flex-1 sm:flex-none inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl transition-all duration-300 font-bold shadow-xl shadow-blue-500/25 active:scale-95 ${downloading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {downloading ? (
               <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
               </svg>
            ) : <FiDownload className="mr-2" />}
            {downloading ? 'Generating...' : 'Download PDF'}
          </button>
        </div>
      </div>
      
      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
        <div className="relative bg-white p-8 sm:p-16 rounded-[2.5rem] shadow-2xl shadow-slate-200/50 border border-slate-50 min-h-[600px]">
          <div className="prose prose-slate prose-lg max-w-none text-slate-800 selection:bg-blue-100">
             <ReactMarkdown>{tailoredResume}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}
