// API Client for The Third Voice
import type {
  User,
  Contact,
  MessageHistoryResponse,
  ContactStats,
  TransformResult,
  InterpretResult,
  AuthResponse
} from './types';

const API_BACKENDS = import.meta.env.DEV
  ? [''] // Development uses Vite proxy
  : [
      'https://api.thethirdvoice.ai',              // Pi primary
      'https://the-third-voice-mvp.onrender.com'   // Render failover
    ];

class ThirdVoiceAPI {
  private currentBackendIndex = 0;
  private backends = API_BACKENDS;
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  private async _fetchWithFallback<T>(endpoint: string, options: RequestInit): Promise<T> {
    const maxRetries = this.backends.length;
    let lastError: Error = new Error('No backends available');

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const backend = this.backends[this.currentBackendIndex];
      const url = import.meta.env.DEV
        ? `/api${endpoint}`
        : `${backend}/api${endpoint}`;

      try {
        console.log(`Attempting ${backend || 'local proxy'} (attempt ${attempt + 1}/${maxRetries})`);

        const res = await fetch(url, {
          ...options,
          headers: { ...this.getHeaders(), ...options.headers },
          signal: AbortSignal.timeout(40000)
        });

        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`HTTP ${res.status}: ${errorText || res.statusText}`);
        }

        console.log(`✅ Success with ${backend || 'local proxy'}`);
        return res.json();
      } catch (err) {
        const error = err as Error;
        console.warn(`❌ ${backend || 'local proxy'} failed:`, error.message);
        lastError = error;

        this.currentBackendIndex = (this.currentBackendIndex + 1) % this.backends.length;

        if (attempt === maxRetries - 1) {
          throw new Error(`All backends failed. Last error: ${lastError.message}`);
        }
      }
    }
    throw lastError;
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<AuthResponse> {
    return this._fetchWithFallback<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  async register(email: string, password: string): Promise<AuthResponse> {
    return this._fetchWithFallback<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  async startDemo(): Promise<AuthResponse> {
    return this._fetchWithFallback<AuthResponse>('/auth/demo', {
      method: 'POST'
    });
  }

  async getCurrentUser(): Promise<User> {
    return this._fetchWithFallback<User>('/auth/me', {
      method: 'GET'
    });
  }

  // Message endpoints
  async quickTransform(message: string, contactContext = 'coparenting', useDeep = false): Promise<TransformResult> {
    return this._fetchWithFallback<TransformResult>('/messages/quick-transform', {
      method: 'POST',
      body: JSON.stringify({
        message,
        contact_context: contactContext,
        use_deep_analysis: useDeep
      })
    });
  }

  async quickInterpret(message: string, contactContext = 'coparenting', useDeep = false): Promise<InterpretResult> {
    return this._fetchWithFallback<InterpretResult>('/messages/quick-interpret', {
      method: 'POST',
      body: JSON.stringify({
        message,
        contact_context: contactContext,
        use_deep_analysis: useDeep
      })
    });
  }

  // Contact endpoints
  async getContacts(): Promise<Contact[]> {
    return this._fetchWithFallback<Contact[]>('/contacts/', {
      method: 'GET'
    });
  }

  async createContact(name: string, context: string): Promise<Contact> {
    return this._fetchWithFallback<Contact>('/contacts/', {
      method: 'POST',
      body: JSON.stringify({ name, context })
    });
  }

  async getContact(contactId: string): Promise<Contact> {
    return this._fetchWithFallback<Contact>(`/contacts/${contactId}`, {
      method: 'GET'
    });
  }

  async deleteContact(contactId: string): Promise<void> {
    return this._fetchWithFallback<void>(`/contacts/${contactId}`, {
      method: 'DELETE'
    });
  }

  // Message history endpoints
  async getMessageHistory(contactId: string, limit = 50): Promise<MessageHistoryResponse> {
    return this._fetchWithFallback<MessageHistoryResponse>(
      `/contacts/${contactId}/messages?limit=${limit}`,
      { method: 'GET' }
    );
  }

  async getContactStats(contactId: string): Promise<ContactStats> {
    return this._fetchWithFallback<ContactStats>(
      `/contacts/${contactId}/stats`,
      { method: 'GET' }
    );
  }
}

export const api = new ThirdVoiceAPI();
export default api;
