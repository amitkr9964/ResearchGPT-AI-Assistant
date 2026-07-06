import { useState } from 'react';
import {
  FileText, Trash2, Edit2, Check, X, Search, MoreVertical,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Document } from '../types';
import { useDocuments, useDeleteDocument, useRenameDocument } from '../hooks/useDocuments';
import LoadingSpinner from './LoadingSpinner';

interface DocumentPanelProps {
  selectedIds: number[];
  onSelectionChange: (ids: number[]) => void;
}

export default function DocumentPanel({ selectedIds, onSelectionChange }: DocumentPanelProps) {
  const [search, setSearch] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState('');
  const { data: documents, isLoading } = useDocuments(search);
  const deleteDoc = useDeleteDocument();
  const renameDoc = useRenameDocument();

  const toggleSelect = (id: number) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((i) => i !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleRename = (id: number) => {
    if (editName.trim()) {
      renameDoc.mutate({ id, filename: editName.trim() });
    }
    setEditingId(null);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <h2 className="text-lg font-semibold mb-3">Documents</h2>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search files..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-9 text-sm"
          />
        </div>
        {selectedIds.length > 0 && (
          <p className="text-xs text-primary-600 mt-2">
            {selectedIds.length} document(s) selected for chat
          </p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {isLoading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner size="sm" />
          </div>
        ) : !documents?.length ? (
          <p className="text-center text-sm text-gray-500 py-8">No documents uploaded yet</p>
        ) : (
          <div className="space-y-1">
            {documents.map((doc: Document, idx: number) => (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className={`group p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedIds.includes(doc.id)
                    ? 'bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800'
                    : 'hover:bg-gray-50 dark:hover:bg-slate-800 border border-transparent'
                }`}
                onClick={() => toggleSelect(doc.id)}
              >
                <div className="flex items-start gap-2">
                  <FileText className="w-4 h-4 text-primary-500 mt-0.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    {editingId === doc.id ? (
                      <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                        <input
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                          className="input-field text-xs py-1"
                          autoFocus
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleRename(doc.id);
                            if (e.key === 'Escape') setEditingId(null);
                          }}
                        />
                        <button onClick={() => handleRename(doc.id)} className="p-1 text-green-600">
                          <Check className="w-3 h-3" />
                        </button>
                        <button onClick={() => setEditingId(null)} className="p-1 text-red-600">
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ) : (
                      <p className="text-sm font-medium truncate">{doc.filename}</p>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">{formatSize(doc.file_size)}</span>
                      <span className="text-xs text-gray-500">{doc.page_count} pages</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                        doc.status === 'ready'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                          : doc.status === 'processing'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                          : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                      }`}>
                        {doc.status}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => { setEditingId(doc.id); setEditName(doc.filename); }}
                      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-slate-700"
                    >
                      <Edit2 className="w-3 h-3 text-gray-500" />
                    </button>
                    <button
                      onClick={() => deleteDoc.mutate(doc.id)}
                      className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30"
                    >
                      <Trash2 className="w-3 h-3 text-red-500" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
