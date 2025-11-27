import { useState } from 'react';
import { Bot, Lock, Mail, User, ArrowRight, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import { API_ENDPOINTS } from '../config/api'; // ✅ IMPORTAR

interface LoginProps {
  onLoginSuccess: (token: string, user: any) => void;
}

function Login({ onLoginSuccess }: LoginProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // ✅ USAR ENDPOINTS DE LA CONFIG
      const endpoint = isLogin ? API_ENDPOINTS.LOGIN : API_ENDPOINTS.REGISTER;

      const body = isLogin
        ? { username, password }
        : { username, email, password };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error en autenticación');
      }

      if (data.success && data.token) {
        localStorage.setItem('token', data.token.access_token);
        localStorage.setItem('user', JSON.stringify(data.token.user));
        onLoginSuccess(data.token.access_token, data.token.user);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4 font-sans text-gray-100">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-green-600 rounded-2xl mx-auto flex items-center justify-center mb-6 shadow-lg shadow-green-900/20">
            <Bot size={40} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            {isLogin ? 'Welcome back' : 'Create an account'}
          </h1>
          <p className="text-gray-400">
            {isLogin
              ? 'Enter your credentials to access the workspace'
              : 'Join the UAGRM Social Media Management System'}
          </p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300 ml-1">Username</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User size={18} className="text-gray-500 group-focus-within:text-green-500 transition-colors" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="johndoe"
                  required
                  disabled={loading}
                  className="w-full bg-black border border-gray-800 text-white text-sm rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 block w-full pl-10 p-3 outline-none transition-all placeholder-gray-600"
                />
              </div>
            </div>

            {!isLogin && (
              <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                <label className="text-sm font-medium text-gray-300 ml-1">Email address</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail size={18} className="text-gray-500 group-focus-within:text-green-500 transition-colors" />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    required
                    disabled={loading}
                    className="w-full bg-black border border-gray-800 text-white text-sm rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 block w-full pl-10 p-3 outline-none transition-all placeholder-gray-600"
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300 ml-1">Password</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock size={18} className="text-gray-500 group-focus-within:text-green-500 transition-colors" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  disabled={loading}
                  className="w-full bg-black border border-gray-800 text-white text-sm rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 block w-full pl-10 p-3 outline-none transition-all placeholder-gray-600"
                />
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2 animate-in fade-in slide-in-from-top-1">
                <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={cn(
                "w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-500 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 shadow-lg shadow-green-900/20",
                loading && "opacity-70 cursor-not-allowed"
              )}
            >
              {loading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <>
                  {isLogin ? 'Sign in' : 'Create account'}
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-400">
              {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
              <button
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                }}
                className="font-medium text-green-500 hover:text-green-400 transition-colors focus:outline-none hover:underline"
              >
                {isLogin ? 'Sign up' : 'Log in'}
              </button>
            </p>
          </div>
        </div>

        <div className="mt-8 text-center text-xs text-gray-600">
          <p>© 2024 UAGRM Social Media System. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}

export default Login;