import { useState, useRef, useEffect } from 'react';
import { Send, Mic, Square, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Citation, Message, SearchMode } from '../types';
import { streamChat } from '../services/api';
import MarkdownRenderer from './MarkdownRenderer';
import CitationCard from './CitationCard';
import LoadingSpinner from './LoadingSpinner';

interface ChatWindowProps {
  conversationId: number | null;
  messages: Message[];
  selectedDocIds: number[];
  searchMode: SearchMode;
  onConversationCreated: (id: number) => void;
  onMessageAdded: (message: Message) => void;
}

export default function ChatWindow({
  conversationId,
  messages,
  selectedDocIds,
  searchMode,
  onConversationCreated,
  onMessageAdded,
}: ChatWindowProps) {
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [streamingCitations, setStreamingCitations] = useState<Citation[]>([]);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
      created_at: new Date().toISOString(),
    };
    onMessageAdded(userMessage);
    const messageText = input.trim();
    setInput('');
    setIsStreaming(true);
    setStreamingContent('');
    setStreamingCitations([]);

    let fullContent = '';
    let finalCitations: Citation[] = [];

    await streamChat(
      {
        message: messageText,
        conversation_id: conversationId || undefined,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
        search_mode: searchMode,
      },
      (token) => {
        fullContent += token;
        setStreamingContent(fullContent);
      },
      (meta) => {
        if (!conversationId) onConversationCreated(meta.conversation_id);
        finalCitations = meta.citations as Citation[];
        setStreamingCitations(finalCitations);
      },
      () => {
        onMessageAdded({
          id: Date.now() + 1,
          role: 'assistant',
          content: fullContent,
          citations: finalCitations.length > 0 ? finalCitations : undefined,
          created_at: new Date().toISOString(),
        });
        setIsStreaming(false);
        setStreamingContent('');
        setStreamingCitations([]);
      },
      () => {
        setIsStreaming(false);
        setStreamingContent('');
      }
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startVoiceInput = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event: any) => {
      setInput(event.results[0][0].transcript);
      setIsListening(false);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
    setIsListening(true);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isStreaming && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center h-full text-center px-4"
          >
            <div className="p-4 rounded-2xl bg-primary-100 dark:bg-primary-900/30 mb-4">
              <Sparkles className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h2 className="text-xl font-semibold mb-2">ResearchGPT</h2>
            <p className="text-gray-500 dark:text-gray-400 max-w-md">
              Upload your research papers and ask questions. I'll answer using only your documents with citations.
            </p>
            <div className="grid grid-cols-2 gap-2 mt-6 max-w-md w-full">
              {[
                'Summarize this paper',
                'Explain the methodology',
                'Compare key findings',
                'Generate quiz questions',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="text-sm p-3 rounded-lg border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors text-left"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'card'
                }`}
              >
                {msg.role === 'assistant' ? (
                  <>
                    <MarkdownRenderer content={msg.content} />
                    {msg.citations && <CitationCard citations={msg.citations} />}
                  </>
                ) : (
                  <p className="text-sm">{msg.content}</p>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isStreaming && streamingContent && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
            <div className="max-w-[80%] card rounded-2xl px-4 py-3">
              <MarkdownRenderer content={streamingContent} />
              {streamingCitations.length > 0 && <CitationCard citations={streamingCitations} />}
            </div>
          </motion.div>
        )}

        {isStreaming && !streamingContent && (
          <div className="flex justify-start">
            <div className="card rounded-2xl px-4 py-3">
              <LoadingSpinner size="sm" text="Searching documents..." />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-slate-700">
        <div className="flex items-end gap-2 card p-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows={1}
            className="flex-1 resize-none bg-transparent outline-none text-sm px-2 py-2 max-h-32"
            disabled={isStreaming}
          />
          <button
            onClick={startVoiceInput}
            className={`p-2 rounded-lg transition-colors ${
              isListening ? 'bg-red-100 text-red-600' : 'hover:bg-gray-100 dark:hover:bg-slate-800'
            }`}
            title="Voice input"
          >
            {isListening ? <Square className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            className="btn-primary p-2 rounded-lg"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2 text-center">
          Answers are generated only from your uploaded documents with citations.
        </p>
      </div>
    </div>
  );
}
