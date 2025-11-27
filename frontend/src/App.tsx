import { useState, useEffect } from 'react';
import './App.css';
import Login from './auth/Login';
import ChatSidebar from './components/ChatSidebar';
import ChatArea from './components/ChatArea';
import { Menu } from 'lucide-react';
import { API_ENDPOINTS, getAuthHeaders } from './config/api'; // ✅ IMPORTAR

// Tipos
export interface Conversation {
  id: number;
  title: string;
  updated_at: string;
}

export interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  // Auth State
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);

  // Chat State
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Social Media State
  const [selectedNetworks, setSelectedNetworks] = useState<string[]>(['facebook', 'instagram']);

  // --- Auth Effects ---
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      setToken(savedToken);
      setCurrentUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
  }, []);

  // --- Chat Effects ---
  useEffect(() => {
    if (isAuthenticated && token) {
      fetchConversations();
    }
  }, [isAuthenticated, token]);

  useEffect(() => {
    if (currentConversationId && token) {
      fetchMessages(currentConversationId);
    } else {
      setMessages([]);
    }
  }, [currentConversationId, token]);

  // --- API Calls (✅ ACTUALIZADAS) ---

  const fetchConversations = async () => {
    try {
      const res = await fetch(API_ENDPOINTS.CONVERSATIONS, {
        headers: getAuthHeaders(token)
      });
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (err) {
      console.error("Error fetching conversations:", err);
    }
  };

  const fetchMessages = async (convId: number) => {
    try {
      const res = await fetch(API_ENDPOINTS.CONVERSATION_DETAIL(convId), {
        headers: getAuthHeaders(token)
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
      }
    } catch (err) {
      console.error("Error fetching messages:", err);
    }
  };

  const createConversation = async (title?: string) => {
    try {
      const res = await fetch(API_ENDPOINTS.CONVERSATIONS, {
        method: 'POST',
        headers: getAuthHeaders(token),
        body: JSON.stringify({ title })
      });
      if (res.ok) {
        const newConv = await res.json();
        setConversations([newConv, ...conversations]);
        return newConv.id;
      }
    } catch (err) {
      console.error("Error creating conversation:", err);
    }
    return null;
  };

  const deleteConversation = async (id: number) => {
    if (!confirm("¿Estás seguro de eliminar este chat?")) return;
    try {
      await fetch(API_ENDPOINTS.DELETE_CONVERSATION(id), {
        method: 'DELETE',
        headers: getAuthHeaders(token)
      });
      setConversations(conversations.filter(c => c.id !== id));
      if (currentConversationId === id) {
        setCurrentConversationId(null);
      }
    } catch (err) {
      console.error("Error deleting conversation:", err);
    }
  };

  const sendMessage = async (content: string) => {
    let convId = currentConversationId;

    if (!convId) {
      convId = await createConversation(content.substring(0, 30));
      if (convId) setCurrentConversationId(convId);
      else return;
    }

    const userMsg: Message = { role: 'user', content };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch(API_ENDPOINTS.CONVERSATION_MESSAGES(convId), {
        method: 'POST',
        headers: getAuthHeaders(token),
        body: JSON.stringify({
          role: 'user',
          content,
          selected_networks: selectedNetworks
        })
      });

      if (res.ok) {
        let attempts = 0;
        const maxAttempts = 15;

        const pollMessages = async () => {
          if (attempts >= maxAttempts) {
            setIsLoading(false);
            return;
          }

          try {
            const msgsRes = await fetch(API_ENDPOINTS.CONVERSATION_DETAIL(convId!), {
              headers: getAuthHeaders(token)
            });

            if (msgsRes.ok) {
              const data = await msgsRes.json();
              const newMessages = data.messages || [];
              const lastMsg = newMessages[newMessages.length - 1];

              if (lastMsg && lastMsg.role === 'assistant') {
                setMessages(newMessages);
                setIsLoading(false);
                fetchConversations();
              } else {
                attempts++;
                setTimeout(pollMessages, 2000);
              }
            }
          } catch (e) {
            console.error("Polling error", e);
            attempts++;
            setTimeout(pollMessages, 2000);
          }
        };

        setTimeout(pollMessages, 2000);
      }

    } catch (err) {
      console.error("Error sending message:", err);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error al procesar tu mensaje." }]);
      setIsLoading(false);
    }
  };

  // --- Handlers ---

  const handleLoginSuccess = (newToken: string, user: any) => {
    setToken(newToken);
    setCurrentUser(user);
    setIsAuthenticated(true);
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify(user));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setCurrentUser(null);
    setIsAuthenticated(false);
    setConversations([]);
    setMessages([]);
    setCurrentConversationId(null);
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 overflow-hidden font-sans">
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-gray-800 rounded-md shadow-md text-white"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
      >
        <Menu size={24} />
      </button>

      <div className={`
        fixed md:relative z-40 h-full transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0 md:w-0 md:overflow-hidden"}
        md:flex-shrink-0 bg-black border-r border-gray-800
      `}>
        <ChatSidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={(id) => {
            setCurrentConversationId(id);
            if (window.innerWidth < 768) setIsSidebarOpen(false);
          }}
          onNewChat={() => {
            setCurrentConversationId(null);
            if (window.innerWidth < 768) setIsSidebarOpen(false);
          }}
          onDeleteConversation={deleteConversation}
          onLogout={handleLogout}
          currentUser={currentUser}
        />
      </div>

      <div className="flex-1 flex flex-col h-full relative w-full bg-gray-900">
        <ChatArea
          messages={messages}
          onSendMessage={sendMessage}
          isLoading={isLoading}
          selectedNetworks={selectedNetworks}
          setSelectedNetworks={setSelectedNetworks}
        />
      </div>
    </div>
  );
}

export default App;