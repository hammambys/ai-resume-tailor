import React, { useState } from 'react';
import axios from 'axios';
import UploadSection from './components/UploadSection';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResultViewer from './components/ResultViewer';
import { FiCpu, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleTailor = async () => {
    if (!file) {
      setError("Please upload a resume file.");
      return;
    }
    if (!jobDescription.trim()) {
      setError("Please paste a job description.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('resume_file', file);
    formData.append('job_description', jobDescription);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/tailor', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setResult(response.data.tailored_resume);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "An error occurred while tailoring the resume.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] py-16 px-4 sm:px-6 lg:px-8 font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Background Decorative Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-blue-100/50 blur-[120px] rounded-full" />
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-indigo-100/50 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-4xl mx-auto relative">
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-2xl shadow-blue-500/30 mb-8 transform hover:scale-110 transition-transform duration-500">
            <FiCpu className="text-4xl text-white" />
          </div>
          <h1 className="text-5xl font-black text-slate-900 tracking-tight mb-6">
            AI <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Resume Tailor</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Optimize your career trajectory. Upload your resume and let our advanced AI align your skills with your dream job in seconds.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-2xl shadow-slate-200/60 border border-white p-8 sm:p-14 mb-10 transition-all duration-500">
          {error && (
            <div className="mb-10 p-5 bg-red-50/80 border border-red-100 text-red-800 rounded-2xl font-medium flex items-center animate-shake">
              <FiAlertCircle className="mr-3 text-xl flex-shrink-0" />
              {error}
            </div>
          )}

          <div className="space-y-10">
            <UploadSection file={file} onFileUpload={setFile} />
            
            <JobDescriptionInput value={jobDescription} onChange={setJobDescription} />

            <button
              onClick={handleTailor}
              disabled={loading}
              className={`w-full py-5 rounded-2xl font-bold text-xl text-white transition-all duration-500 shadow-xl overflow-hidden relative group ${
                loading 
                  ? 'bg-slate-400 cursor-not-allowed' 
                  : 'bg-slate-900 hover:bg-slate-800 hover:shadow-slate-300/50 hover:-translate-y-1 active:scale-[0.98]'
              }`}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <span className="relative z-10 flex items-center justify-center">
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing with AI...
                  </>
                ) : (
                  'Generate Tailored Resume'
                )}
              </span>
            </button>
          </div>
        </div>

        <ResultViewer tailoredResume={result} />
        
        <footer className="mt-16 text-center text-slate-400 text-sm font-medium">
          Built with advanced AI to help you land your next big role.
        </footer>
      </div>
    </div>
  );
}

export default App;
