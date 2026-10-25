import { useState } from 'react';

export default function JobDescriptionInput({ value, onChange, onExtractLinkedIn, extracting }) {
  const [linkedinUrl, setLinkedinUrl] = useState('');

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-800 tracking-tight">2. Job Description</h2>
        <span className={`text-xs font-bold px-3 py-1 rounded-full transition-colors duration-300 ${value.length > 0 ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-400'}`}>
          {value.length.toLocaleString()} / 10,000 characters
        </span>
      </div>
      <div className="space-y-3 rounded-2xl border border-blue-100 bg-blue-50/50 p-5">
        <label htmlFor="linkedin-job-url" className="block">
          <span className="mb-2 block text-sm font-bold text-slate-700">Use a LinkedIn job link instead</span>
          <input
            id="linkedin-job-url"
            type="url"
            value={linkedinUrl}
            onChange={(event) => setLinkedinUrl(event.target.value)}
            placeholder="https://www.linkedin.com/jobs/view/..."
            autoComplete="url"
            className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-800 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          />
        </label>
        <button
          type="button"
          onClick={() => onExtractLinkedIn(linkedinUrl)}
          disabled={extracting || !linkedinUrl.trim()}
          className="rounded-xl bg-blue-600 px-4 py-2 font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {extracting ? 'Extracting description...' : 'Extract description'}
        </button>
        <p className="text-sm text-slate-500">
          The job must be publicly accessible. The extracted text will appear below so you can review or edit it.
        </p>
      </div>
      <div className="relative group">
        <textarea
          className="w-full h-64 p-6 border-2 border-slate-100 rounded-[2rem] focus:ring-0 focus:border-blue-500/50 resize-none transition-all duration-300 shadow-sm bg-slate-50/50 hover:bg-white text-slate-700 leading-relaxed placeholder:text-slate-300"
          placeholder="Paste the target job description here..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          maxLength={10000}
        />
        <div className="absolute inset-0 rounded-[2rem] border-2 border-transparent group-focus-within:border-blue-500/10 pointer-events-none transition-all duration-300" />
      </div>
    </div>
  );
}
