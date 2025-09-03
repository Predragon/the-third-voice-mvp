export const API_BASE = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000'  // Local development
  : 'http://100.71.78.118:8001';  // Pi server
