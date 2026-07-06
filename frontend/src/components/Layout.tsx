import { Outlet } from 'react-router-dom';
import { useState } from 'react';
import Sidebar from './Sidebar';
import { Message } from '../types';
import { useConversation } from '../hooks/useChat';

export default function Layout() {
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [localMessages, setLocalMessages] = useState<Message[]>([]);

  const handleNewChat = () => {
    setActiveConversationId(null);
    setLocalMessages([]);
  };

  const handleSelectConversation = (id: number) => {
    setActiveConversationId(id);
    setLocalMessages([]);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        onNewChat={handleNewChat}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
      />
      <main className="flex-1 overflow-hidden">
        <Outlet context={{
          activeConversationId,
          setActiveConversationId,
          localMessages,
          setLocalMessages,
        }} />
      </main>
    </div>
  );
}
