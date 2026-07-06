import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import ChatWindow from '../components/ChatWindow';
import DocumentPanel from '../components/DocumentPanel';
import { Message, SearchMode } from '../types';
import { useConversation } from '../hooks/useChat';

interface OutletContext {
  activeConversationId: number | null;
  setActiveConversationId: (id: number) => void;
  localMessages: Message[];
  setLocalMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

export default function DashboardPage() {
  const {
    activeConversationId,
    setActiveConversationId,
    localMessages,
    setLocalMessages,
  } = useOutletContext<OutletContext>();

  const [selectedDocIds, setSelectedDocIds] = useState<number[]>([]);
  const [searchMode, setSearchMode] = useState<SearchMode>('hybrid');
  const { data: conversation } = useConversation(activeConversationId);

  useEffect(() => {
    if (conversation?.messages) {
      setLocalMessages(conversation.messages);
    }
  }, [conversation, setLocalMessages]);

  const handleMessageAdded = (message: Message) => {
    setLocalMessages((prev) => [...prev, message]);
  };

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-slate-700">
          <h2 className="font-semibold">Chat</h2>
          <select
            value={searchMode}
            onChange={(e) => setSearchMode(e.target.value as SearchMode)}
            className="text-sm px-3 py-1.5 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800"
          >
            <option value="hybrid">Hybrid Search</option>
            <option value="semantic">Semantic Search</option>
            <option value="keyword">Keyword Search</option>
          </select>
        </div>
        <ChatWindow
          conversationId={activeConversationId}
          messages={localMessages}
          selectedDocIds={selectedDocIds}
          searchMode={searchMode}
          onConversationCreated={setActiveConversationId}
          onMessageAdded={handleMessageAdded}
        />
      </div>
      <div className="w-80 border-l border-gray-200 dark:border-slate-700 hidden lg:block">
        <DocumentPanel
          selectedIds={selectedDocIds}
          onSelectionChange={setSelectedDocIds}
        />
      </div>
    </div>
  );
}
