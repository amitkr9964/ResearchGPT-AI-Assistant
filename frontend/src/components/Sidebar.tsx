import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  MessageSquare, FileText, Search, Settings, User, LogOut,
  Moon, Sun, Plus, Star, Trash2, Sparkles, BookOpen,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useChatHistory, useDeleteConversation } from '../hooks/useChat';
import { Conversation } from '../types';

interface SidebarProps {
  onNewChat: () => void;
  activeConversationId: number | null;
  onSelectConversation: (id: number) => void;
}

export default function Sidebar({
  onNewChat,
  activeConversationId,
  onSelectConversation,
}: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();
  const { data: history } = useChatHistory();
  const deleteConv = useDeleteConversation();

  const navItems = [
    { path: '/dashboard', icon: MessageSquare, label: 'Chat' },
    { path: '/documents', icon: FileText, label: 'Documents' },
    { path: '/search', icon: Search, label: 'Search' },
    { path: '/tools', icon: Sparkles, label: 'AI Tools' },
    { path: '/settings', icon: Settings, label: 'Settings' },
    { path: '/profile', icon: User, label: 'Profile' },
  ];

  return (
    <aside className="w-64 h-full flex flex-col bg-white dark:bg-slate-900 border-r border-gray-200 dark:border-slate-700">
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-primary-600">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg">ResearchGPT</h1>
            <p className="text-xs text-gray-500">AI Research Assistant</p>
          </div>
        </div>
      </div>

      <div className="p-3">
        <button onClick={onNewChat} className="btn-primary w-full flex items-center justify-center gap-2 text-sm">
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      <nav className="px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-item ${isActive ? 'sidebar-item-active' : 'sidebar-item-inactive'}`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="flex-1 overflow-y-auto px-3 mt-4">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">
          Recent Chats
        </p>
        <div className="space-y-1">
          {history?.slice(0, 15).map((conv: Conversation) => (
            <motion.div
              key={conv.id}
              whileHover={{ x: 2 }}
              className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-sm ${
                activeConversationId === conv.id
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-800'
              }`}
              onClick={() => {
                onSelectConversation(conv.id);
                navigate('/dashboard');
              }}
            >
              <MessageSquare className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate flex-1">{conv.title}</span>
              {conv.is_favorite && <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteConv.mutate(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-0.5 hover:text-red-500"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="p-3 border-t border-gray-200 dark:border-slate-700 space-y-2">
        <button
          onClick={toggleDarkMode}
          className="sidebar-item sidebar-item-inactive w-full"
        >
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          {darkMode ? 'Light Mode' : 'Dark Mode'}
        </button>
        <div className="flex items-center gap-2 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-sm font-medium">
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.username}</p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
          <button onClick={logout} className="p-1 hover:text-red-500" title="Logout">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
