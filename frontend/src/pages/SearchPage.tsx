import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { motion } from 'framer-motion';
import { searchApi } from '../services/api';
import { SearchResult, SearchMode } from '../types';
import { useDocuments } from '../hooks/useDocuments';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchMode, setSearchMode] = useState<SearchMode>('hybrid');
  const [selectedDocIds, setSelectedDocIds] = useState<number[]>([]);
  const [author, setAuthor] = useState('');
  const [filename, setFilename] = useState('');
  const { data: documents } = useDocuments();

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await searchApi.search({
        query: query.trim(),
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
        author: author || undefined,
        filename: filename || undefined,
        search_mode: searchMode,
        top_k: 15,
      });
      setResults(res.data.results);
    } catch {
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">Search Documents</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          Semantic, keyword, and hybrid search across your uploaded documents.
        </p>

        <div className="card p-6 mb-6 space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search your documents..."
                className="input-field pl-9"
              />
            </div>
            <button onClick={handleSearch} disabled={loading} className="btn-primary">
              Search
            </button>
          </div>

          <div className="flex flex-wrap gap-3">
            <select
              value={searchMode}
              onChange={(e) => setSearchMode(e.target.value as SearchMode)}
              className="text-sm px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800"
            >
              <option value="hybrid">Hybrid</option>
              <option value="semantic">Semantic</option>
              <option value="keyword">Keyword</option>
            </select>
            <input
              type="text"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              placeholder="Filter by author"
              className="input-field text-sm w-48"
            />
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="Filter by filename"
              className="input-field text-sm w-48"
            />
          </div>

          {documents && documents.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2 flex items-center gap-1">
                <Filter className="w-4 h-4" /> Filter by document:
              </p>
              <div className="flex flex-wrap gap-2">
                {documents.map((doc: { id: number; filename: string }) => (
                  <button
                    key={doc.id}
                    onClick={() => {
                      setSelectedDocIds((prev) =>
                        prev.includes(doc.id)
                          ? prev.filter((id) => id !== doc.id)
                          : [...prev, doc.id]
                      );
                    }}
                    className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                      selectedDocIds.includes(doc.id)
                        ? 'bg-primary-100 border-primary-300 text-primary-700 dark:bg-primary-900/30 dark:border-primary-700 dark:text-primary-300'
                        : 'border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    {doc.filename}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner text="Searching..." />
          </div>
        ) : results.length > 0 ? (
          <div className="space-y-3">
            <p className="text-sm text-gray-500">{results.length} results found</p>
            {results.map((result, idx) => (
              <motion.div
                key={`${result.document_id}-${result.chunk_index}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="card p-4"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-medium text-sm">{result.document_name}</p>
                    <p className="text-xs text-gray-500">Page {result.page_number}</p>
                  </div>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300">
                    Score: {(result.score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
                  {result.content}
                </p>
              </motion.div>
            ))}
          </div>
        ) : query ? (
          <p className="text-center text-gray-500 py-12">No results found</p>
        ) : null}
      </div>
    </div>
  );
}
