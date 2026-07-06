import { useTheme } from '../context/ThemeContext';
import { Moon, Sun, Bell, Shield } from 'lucide-react';
import { authApi } from '../services/api';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { darkMode, toggleDarkMode } = useTheme();

  const handleDarkModeToggle = async () => {
    toggleDarkMode();
    try {
      await authApi.updateMe({ dark_mode: !darkMode });
    } catch {
      // preference saved locally
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">Customize your ResearchGPT experience.</p>

        <div className="space-y-4">
          <div className="card p-6">
            <h2 className="text-lg font-semibold mb-4">Appearance</h2>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {darkMode ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
                <div>
                  <p className="font-medium">Dark Mode</p>
                  <p className="text-sm text-gray-500">Toggle dark/light theme</p>
                </div>
              </div>
              <button
                onClick={handleDarkModeToggle}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  darkMode ? 'bg-primary-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                    darkMode ? 'translate-x-6' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-lg font-semibold mb-4">RAG Configuration</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between py-2 border-b border-gray-100 dark:border-slate-800">
                <span className="text-gray-500">Search Mode Default</span>
                <span className="font-medium">Hybrid</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100 dark:border-slate-800">
                <span className="text-gray-500">Top-K Retrieval</span>
                <span className="font-medium">10</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100 dark:border-slate-800">
                <span className="text-gray-500">Rerank Top-K</span>
                <span className="font-medium">5</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-500">Embedding Model</span>
                <span className="font-medium text-xs">all-MiniLM-L6-v2</span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5" /> Privacy
            </h2>
            <p className="text-sm text-gray-500">
              Your documents are stored locally and processed on your server.
              No data is shared with third parties except the Gemini API for answer generation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
