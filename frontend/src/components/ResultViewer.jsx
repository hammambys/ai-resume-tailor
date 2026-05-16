import React, { useRef } from 'react';
import { FiDownload, FiCopy, FiCheck } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import { PDFDownloadLink } from '@react-pdf/renderer';
import ResumePDFTemplate from './ResumePDFTemplate';

export default function ResultViewer({ tailoredResume }) {
  const [copied, setCopied] = React.useState(false);

  const ensureString = (val) => {
    if (!val) return '';
    if (typeof val === 'string') return val;
    
    if (Array.isArray(val)) {
      // If it's a list of strings, just join them
      if (val.length > 0 && typeof val[0] === 'string') {
        return val.join('\n');
      }
      // If it's a list of objects (like experience or education)
      return val.map(item => {
        if (typeof item === 'string') return item;
        if (typeof item === 'object') {
          // Format based on likely keys
          const parts = [];
          if (item.role || item.title) parts.push(`### ${item.role || item.title}`);
          if (item.company) parts.push(`**${item.company}**`);
          if (item.institution) parts.push(`**${item.institution}**`);
          if (item.degree) parts.push(`*${item.degree}*`);
          
          let meta = [item.location, item.duration].filter(Boolean).join(' | ');
          if (meta) parts.push(meta);
          
          if (item.responsibilities && Array.isArray(item.responsibilities)) {
            parts.push(item.responsibilities.map(r => `- ${r}`).join('\n'));
          } else if (item.description) {
            parts.push(item.description);
          }
          
          return parts.join('\n\n');
        }
        return String(item);
      }).join('\n\n---\n\n');
    }

    if (typeof val === 'object' && val !== null) {
      return Object.entries(val)
        .map(([key, value]) => `**${key}:** ${value}`)
        .join(' | ');
    }
    return String(val || '');
  };

  // Helper to join sections into a single markdown string
  const getFullMarkdown = () => {
    if (typeof tailoredResume === 'string') return tailoredResume;
    
    const { name, contact, summary, experience, education, skills } = tailoredResume;
    return [
      `# ${ensureString(name)}`,
      ensureString(contact),
      `## Summary\n${ensureString(summary)}`,
      `## Experience\n${ensureString(experience)}`,
      `## Education\n${ensureString(education)}`,
      `## Skills\n${ensureString(skills)}`
    ].filter(Boolean).join('\n\n');
  };

  const handleCopy = () => {
    const text = getFullMarkdown();
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!tailoredResume) return null;

  const renderSection = (title, content) => {
    if (!content) return null;
    
    // Ensure content is a string
    const stringContent = ensureString(content);

    return (
      <div className="mb-10 last:mb-0">
        <h3 className="text-xl font-bold text-slate-900 mb-4 pb-2 border-b border-slate-100 flex items-center">
          <span className="w-1.5 h-6 bg-blue-600 rounded-full mr-3"></span>
          {title}
        </h3>
        <div className="prose prose-slate prose-lg max-w-none text-slate-800">
          <ReactMarkdown>{stringContent}</ReactMarkdown>
        </div>
      </div>
    );
  };

  const isObject = typeof tailoredResume === 'object' && tailoredResume !== null;


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
          <PDFDownloadLink
            document={<ResumePDFTemplate resumeData={tailoredResume} />}
            fileName="Tailored_Resume.pdf"
            className="flex-1 sm:flex-none inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl transition-all duration-300 font-bold shadow-xl shadow-blue-500/25 active:scale-95"
          >
            {({ blob, url, loading, error }) => (
              <>
                {loading ? (
                   <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                   </svg>
                ) : <FiDownload className="mr-2" />}
                {loading ? 'Preparing PDF...' : 'Download PDF'}
              </>
            )}
          </PDFDownloadLink>
        </div>
      </div>
      
      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
        <div className="relative bg-white p-8 sm:p-16 rounded-[2.5rem] shadow-2xl shadow-slate-200/50 border border-slate-50 min-h-[600px]">
          {isObject ? (
            <div className="space-y-4">
              <div className="text-center mb-12">
                <h1 className="text-4xl font-black text-slate-900 mb-4">{ensureString(tailoredResume.name)}</h1>
                <div className="text-slate-600 font-medium">
                  <ReactMarkdown>{ensureString(tailoredResume.contact)}</ReactMarkdown>
                </div>
              </div>
              
              {renderSection("Summary", tailoredResume.summary)}
              {renderSection("Experience", tailoredResume.experience)}
              {renderSection("Education", tailoredResume.education)}
              {renderSection("Skills", tailoredResume.skills)}
            </div>
          ) : (
            <div className="prose prose-slate prose-lg max-w-none text-slate-800 selection:bg-blue-100">
               <ReactMarkdown>{ensureString(tailoredResume)}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
