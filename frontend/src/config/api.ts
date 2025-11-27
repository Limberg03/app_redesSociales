/**
 * ⚙️ CONFIGURACIÓN DE API
 * 
 * Esta configuración detecta automáticamente el entorno:
 * - Desarrollo local: http://127.0.0.1:8000
 * - Producción (Render): tu-backend.onrender.com
 */

const isDevelopment = import.meta.env.MODE === 'development';

// URL base del backend
export const API_BASE_URL = isDevelopment 
  ? 'http://127.0.0.1:8000'
  : import.meta.env.VITE_API_URL || 'https://tu-backend.onrender.com';

// Endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  REGISTER: `${API_BASE_URL}/api/auth/register`,
  LOGOUT: `${API_BASE_URL}/api/auth/logout`,
  ME: `${API_BASE_URL}/api/auth/me`,
  
  // Chat
  CONVERSATIONS: `${API_BASE_URL}/api/chat/conversations`,
  CONVERSATION_DETAIL: (id: number) => `${API_BASE_URL}/api/chat/conversations/${id}`,
  CONVERSATION_MESSAGES: (id: number) => `${API_BASE_URL}/api/chat/conversations/${id}/messages`,
  DELETE_CONVERSATION: (id: number) => `${API_BASE_URL}/api/chat/conversations/${id}`,
};

// Helper para headers con autenticación
export const getAuthHeaders = (token: string | null) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// Logs en desarrollo
if (isDevelopment) {
  console.log('🔧 [DEV] API Config:', {
    baseUrl: API_BASE_URL,
    mode: import.meta.env.MODE
  });
}