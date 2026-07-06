import { useState } from 'react';
import {
  FileText, GitCompare, HelpCircle, Layers, BookOpen, Tag, Users,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useDocuments } from '../hooks/useDocuments';
import { advancedApi } from '../services/api';
import MarkdownRenderer from '../components/MarkdownRenderer';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { QuizQuestion, Flashcard } from '../types';

type ToolType = 'summary' | 'compare' | 'quiz' | 'flashcards' | 'literature' | 'entities' | 'keywords';

export default function ToolsPage() {
  const { data: documents } = useDocuments();
  const [activeTool, setActiveTool] = useState<ToolType>('summary');
  const [selectedDoc, setSelectedDoc] = useState<number | null>(null);
  const [selectedDoc2, setSelectedDoc2] = useState<number | null>(null);
  const [selectedDocs, setSelectedDocs] = useState<number[]>([]);
  const [result, setResult] = useState<string>('');
  const [quiz, setQuiz] = useState<QuizQuestion[]>([]);
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const tools = [
    { id: 'summary' as ToolType, icon: FileText, label: 'Summarize' },
    { id: 'compare' as ToolType, icon: GitCompare, label: 'Compare Papers' },
    { id: 'quiz' as ToolType, icon: HelpCircle, label: 'Generate Quiz' },
    { id: 'flashcards' as ToolType, icon: Layers, label: 'Flashcards' },
    { id: 'literature' as ToolType, icon: BookOpen, label: 'Literature Review' },
    { id: 'entities' as ToolType, icon: Users, label: 'Entity Extraction' },
    { id: 'keywords' as ToolType, icon: Tag, label: 'Keywords' },
  ];

  const runTool = async () => {
    setLoading(true);
    setResult('');
    setQuiz([]);
    setFlashcards([]);
    setKeywords([]);

    try {
      switch (activeTool) {
        case 'summary':
          if (!selectedDoc) return toast.error('Select a document');
          const summaryRes = await advancedApi.summarize(selectedDoc);
          setResult(summaryRes.data.summary);
          break;
        case 'compare':
          if (!selectedDoc || !selectedDoc2) return toast.error('Select two documents');
          const compareRes = await advancedApi.compare(selectedDoc, selectedDoc2);
          setResult(
            `## Comparison\n\n${compareRes.data.comparison}\n\n` +
            `### Similarities\n${compareRes.data.similarities.map((s: string) => `- ${s}`).join('\n')}\n\n` +
            `### Differences\n${compareRes.data.differences.map((d: string) => `- ${d}`).join('\n')}`
          );
          break;
        case 'quiz':
          if (!selectedDoc) return toast.error('Select a document');
          const quizRes = await advancedApi.quiz(selectedDoc);
          setQuiz(quizRes.data.questions);
          break;
        case 'flashcards':
          if (!selectedDoc) return toast.error('Select a document');
          const fcRes = await advancedApi.flashcards(selectedDoc);
          setFlashcards(fcRes.data.cards);
          break;
        case 'literature':
          if (selectedDocs.length < 2) return toast.error('Select at least 2 documents');
          const litRes = await advancedApi.literatureReview(selectedDocs);
          setResult(litRes.data.review);
          break;
        case 'entities':
          if (!selectedDoc) return toast.error('Select a document');
          const entRes = await advancedApi.entities(selectedDoc);
          setResult(entRes.data.entities);
          break;
        case 'keywords':
          if (!selectedDoc) return toast.error('Select a document');
          const kwRes = await advancedApi.keywords(selectedDoc);
          setKeywords(kwRes.data.keywords);
          break;
      }
      toast.success('Done!');
    } catch {
      toast.error('Tool execution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">AI Research Tools</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          Advanced AI features powered by your uploaded documents.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-6">
          {tools.map((tool) => (
            <button
              key={tool.id}
              onClick={() => setActiveTool(tool.id)}
              className={`p-3 rounded-lg border text-sm font-medium flex flex-col items-center gap-2 transition-colors ${
                activeTool === tool.id
                  ? 'bg-primary-100 border-primary-300 text-primary-700 dark:bg-primary-900/30 dark:border-primary-700'
                  : 'border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800'
              }`}
            >
              <tool.icon className="w-5 h-5" />
              {tool.label}
            </button>
          ))}
        </div>

        <div className="card p-6 mb-6 space-y-4">
          {activeTool === 'compare' ? (
            <div className="grid grid-cols-2 gap-4">
              <select
                value={selectedDoc || ''}
                onChange={(e) => setSelectedDoc(Number(e.target.value))}
                className="input-field"
              >
                <option value="">Document 1</option>
                {documents?.map((d: { id: number; filename: string }) => (
                  <option key={d.id} value={d.id}>{d.filename}</option>
                ))}
              </select>
              <select
                value={selectedDoc2 || ''}
                onChange={(e) => setSelectedDoc2(Number(e.target.value))}
                className="input-field"
              >
                <option value="">Document 2</option>
                {documents?.map((d: { id: number; filename: string }) => (
                  <option key={d.id} value={d.id}>{d.filename}</option>
                ))}
              </select>
            </div>
          ) : activeTool === 'literature' ? (
            <div className="flex flex-wrap gap-2">
              {documents?.map((d: { id: number; filename: string }) => (
                <button
                  key={d.id}
                  onClick={() => setSelectedDocs((prev) =>
                    prev.includes(d.id) ? prev.filter((id) => id !== d.id) : [...prev, d.id]
                  )}
                  className={`text-xs px-3 py-1.5 rounded-full border ${
                    selectedDocs.includes(d.id)
                      ? 'bg-primary-100 border-primary-300 text-primary-700'
                      : 'border-gray-300'
                  }`}
                >
                  {d.filename}
                </button>
              ))}
            </div>
          ) : (
            <select
              value={selectedDoc || ''}
              onChange={(e) => setSelectedDoc(Number(e.target.value))}
              className="input-field"
            >
              <option value="">Select a document</option>
              {documents?.map((d: { id: number; filename: string }) => (
                <option key={d.id} value={d.id}>{d.filename}</option>
              ))}
            </select>
          )}

          <button onClick={runTool} disabled={loading} className="btn-primary">
            {loading ? 'Processing...' : 'Run'}
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12"><LoadingSpinner text="AI is working..." /></div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-6">
            {result && <MarkdownRenderer content={result} />}
            {quiz.length > 0 && (
              <div className="space-y-4">
                {quiz.map((q, i) => (
                  <div key={i} className="p-4 rounded-lg bg-gray-50 dark:bg-slate-800">
                    <p className="font-medium mb-2">{i + 1}. {q.question}</p>
                    <ul className="text-sm space-y-1 mb-2">
                      {q.options.map((opt, j) => (
                        <li key={j} className={opt === q.answer ? 'text-green-600 font-medium' : ''}>
                          {String.fromCharCode(65 + j)}. {opt}
                        </li>
                      ))}
                    </ul>
                    <p className="text-xs text-gray-500">{q.explanation}</p>
                  </div>
                ))}
              </div>
            )}
            {flashcards.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {flashcards.map((fc, i) => (
                  <div key={i} className="p-4 rounded-lg border border-gray-200 dark:border-slate-700">
                    <p className="font-medium text-sm mb-2">{fc.front}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{fc.back}</p>
                  </div>
                ))}
              </div>
            )}
            {keywords.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {keywords.map((kw, i) => (
                  <span key={i} className="px-3 py-1 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm">
                    {kw}
                  </span>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
