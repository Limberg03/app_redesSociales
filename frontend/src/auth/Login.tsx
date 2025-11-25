import { useState } from 'react';
import './Login.css';

interface LoginProps {
  onLoginSuccess: (token: string, user: any) => void;
}

function Login({ onLoginSuccess }: LoginProps) {
  const [isLogin, setIsLogin] = useState(true); // true = Login, false = Register
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
      const endpoint = isLogin 
        ? 'http://127.0.0.1:8000/api/auth/login'
        : 'http://127.0.0.1:8000/api/auth/register';

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
        // Guardar token en localStorage
        localStorage.setItem('token', data.token.access_token);
        localStorage.setItem('user', JSON.stringify(data.token.user));
        
        // Notificar al componente padre
        onLoginSuccess(data.token.access_token, data.token.user);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🎓 Sistema Multi-Red Social</h1>
          <p>UAGRM - Gestión de Redes Sociales</p>
        </div>

        <div className="login-tabs">
          <button
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(true);
              setError('');
            }}
          >
            Iniciar Sesión
          </button>
          <button
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(false);
              setError('');
            }}
          >
            Registrarse
          </button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Usuario</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Ingresa tu usuario"
              required
              disabled={loading}
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ejemplo@correo.com"
                required
                disabled={loading}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Ingresa tu contraseña"
              required
              disabled={loading}
            />
          </div>

          {error && (
            <div className="error-message">
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            className="submit-button"
            disabled={loading}
          >
            {loading ? '⏳ Procesando...' : isLogin ? '🔓 Iniciar Sesión' : '📝 Registrarse'}
          </button>
        </form>

        <div className="login-footer">
          <p>
            {isLogin ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?'}
            {' '}
            <button
              className="link-button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
            >
              {isLogin ? 'Regístrate aquí' : 'Inicia sesión'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;