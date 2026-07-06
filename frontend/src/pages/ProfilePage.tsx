import { useState } from 'react';
import { User, Mail, Calendar, Download } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authApi, exportApi } from '../services/api';
import { useChatHistory } from '../hooks/useChat';
import toast from 'react-hot-toast';

export default function ProfilePage() {
  const { user, updateUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [saving, setSaving] = useState(false);
  const { data: history } = useChatHistory();

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await authApi.updateMe({ full_name: fullName });
      updateUser(res.data);
      toast.success('Profile updated');
    } catch {
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async (convId: number, format: 'markdown' | 'pdf' | 'docx') => {
    try {
      const res = await exportApi.exportChat(convId, format);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat-export.${format === 'markdown' ? 'md' : format}`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Exported successfully');
    } catch {
      toast.error('Export failed');
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">Profile</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">Manage your account and export chats.</p>

        <div className="card p-6 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 rounded-full bg-primary-600 flex items-center justify-center text-white text-2xl font-bold">
              {user?.username?.[0]?.toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-semibold">{user?.username}</h2>
              <p className="text-gray-500">{user?.email}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="input-field pl-9"
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input type="email" value={user?.email || ''} disabled className="input-field pl-9 opacity-60" />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Member Since</label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''}
                  disabled
                  className="input-field pl-9 opacity-60"
                />
              </div>
            </div>
            <button onClick={handleSave} disabled={saving} className="btn-primary">
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Download className="w-5 h-5" /> Export Chats
          </h2>
          {history && history.length > 0 ? (
            <div className="space-y-2">
              {history.slice(0, 10).map((conv: { id: number; title: string }) => (
                <div key={conv.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-slate-800">
                  <span className="text-sm truncate flex-1">{conv.title}</span>
                  <div className="flex gap-1">
                    {(['markdown', 'pdf', 'docx'] as const).map((fmt) => (
                      <button
                        key={fmt}
                        onClick={() => handleExport(conv.id, fmt)}
                        className="text-xs px-2 py-1 rounded bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 hover:bg-primary-200"
                      >
                        {fmt.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No conversations to export yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
