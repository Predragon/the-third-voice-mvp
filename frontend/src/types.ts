// API Types for The Third Voice

export interface User {
  id: string;
  email: string;
  is_active: boolean;
}

export interface Contact {
  id: string;
  name: string;
  context: 'romantic' | 'coparenting' | 'workplace' | 'family' | 'friend';
  user_id: string;
  created_at: string;
  updated_at?: string;
  message_count?: number;
  last_message_date?: string;
}

export interface Message {
  id: string;
  contact_id: string;
  contact_name: string;
  type: 'transform' | 'interpret';
  original: string;
  result?: string;
  sentiment?: 'positive' | 'neutral' | 'negative' | 'unknown';
  emotional_state?: string;
  model?: string;
  healing_score?: number;
  user_id: string;
  created_at: string;
  updated_at?: string;
}

export interface ContactStats {
  contact: Contact;
  total_messages: number;
  transform_count: number;
  interpret_count: number;
  avg_healing_score: number;
  sentiment_breakdown: {
    positive: number;
    neutral: number;
    negative: number;
    unknown: number;
  };
  messages_with_scores: number;
  recent_activity: Message[];
  last_message_date?: string;
}

export interface MessageHistoryResponse {
  contact: Contact;
  messages: Message[];
  total_messages: number;
  limit_applied: number;
}

export interface TransformResult {
  transformed_message: string;
  explanation?: string;
  healing_score?: number;
  model_used?: string;
  backend_id?: string;
  analysis_depth?: string;
  saved?: boolean;
}

export interface InterpretResult {
  interpretation?: string;
  explanation?: string;
  suggested_responses?: string[];
  emotional_needs?: string[];
  model_used?: string;
  backend_id?: string;
  analysis_depth?: string;
  saved?: boolean;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}
