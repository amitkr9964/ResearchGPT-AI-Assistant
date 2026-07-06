export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  dark_mode: boolean;
  created_at: string;
}

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  page_count: number;
  chunk_count: number;
  author: string | null;
  tags: string | null;
  summary: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  document_name: string;
  document_id: number;
  page_number: number;
  paragraph: string;
  confidence_score: number;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface SearchResult {
  document_id: number;
  document_name: string;
  page_number: number;
  content: string;
  score: number;
  chunk_index: number;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
  explanation: string;
}

export interface Flashcard {
  front: string;
  back: string;
}

export type SearchMode = 'semantic' | 'keyword' | 'hybrid';
