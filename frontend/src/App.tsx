import { useCallback, useEffect, useRef, useState } from 'react';
import './App.css';
import Login from './auth/Login';

// Tipos de TypeScript
interface Validacion {
  es_academico: boolean;
  razon: string;
}

interface Adaptacion {
  text: string;
  hashtags: string[];
  character_count: number;
  suggested_image_prompt?: string;
  tts_text?: string;
}

interface ImagenGenerada {
  url: string;
  prompt: string;
}

interface Publicacion {
  id: string;
  link?: string;
  raw?: any;
}

interface Resultado {
  validacion: Validacion;
  adaptacion: Adaptacion;
  imagen_generada?: ImagenGenerada;
  publicacion?: Publicacion;
  mensaje: string;
  envio?: {
    message_sid: string;
    status: string;
    to: string;
    raw?: any;
  };
}

// 🆕 Tipos para publicación multi-red
interface ResultadoRedSocial {
  estado: 'exitoso' | 'error';
  id?: string;
  link?: string;
  error?: string;
  mensaje?: string;
  adaptacion?: Adaptacion;
  imagen_url?: string;
  share_url?: string;
  publish_id?: string;
  video_id?: string;
  como_ver?: string[];
  cuenta?: string;
  visibilidad?: string;
  nota?: string;
}

interface ResumenMultiRed {
  total_redes: number;
  redes_validas: number;
  exitosos: number;
  fallidos: number;
  tasa_exito: string;
  tiempo_segundos: number;
}

interface ResultadoMultiRed {
  validacion: Validacion;
  resultados: {
    [key: string]: ResultadoRedSocial;
  };
  resumen: ResumenMultiRed;
}

interface ErrorDetail {
  mensaje?: string;
  error?: string;
}

interface Mensaje {
  id: number;
  tipo: 'usuario' | 'sistema' | 'error' | 'multi-red';
  texto: string;
  redSocial: string;
  redesSeleccionadas?: string[];
  resultado?: Resultado;
  resultadoMultiRed?: ResultadoMultiRed;
  timestamp: Date;
}

type RedSocial = 'facebook' | 'instagram' | 'linkedin' | 'whatsapp' | 'tiktok';

function App() {
  const [texto, setTexto] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false); 
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  // 🆕 Ahora soporta selección múltiple
  const [redesSeleccionadas, setRedesSeleccionadas] = useState<Set<RedSocial>>(new Set(['facebook']));
  // 🆕 Modo de publicación
  const [modoMultiRed, setModoMultiRed] = useState<boolean>(false);
  
  // 🆕 Estados de autenticación
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);
  
  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isPublishingRef = useRef<boolean>(false);

  // 🆕 Verificar si hay sesión guardada al cargar
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setCurrentUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
  }, []);

  // 🆕 Función de login exitoso
  const handleLoginSuccess = (newToken: string, user: any) => {
    setToken(newToken);
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  // 🆕 Función de logout
  const handleLogout = async () => {
    try {
      await fetch('http://127.0.0.1:8000/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setToken(null);
      setCurrentUser(null);
      setIsAuthenticated(false);
      setMensajes([]);
    }
  };

  // Auto-scroll optimizado
  const scrollToBottom = useCallback(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [mensajes, scrollToBottom]);

  const agregarMensaje = useCallback((mensaje: Mensaje) => {
    setMensajes(prev => [...prev, mensaje]);
  }, []);

  // 🆕 Toggle de selección de red social
  const toggleRedSocial = (red: RedSocial) => {
    setRedesSeleccionadas(prev => {
      const newSet = new Set(prev);
      if (newSet.has(red)) {
        // Si es la única seleccionada, no permitir deseleccionar
        if (newSet.size === 1) return prev;
        newSet.delete(red);
      } else {
        newSet.add(red);
      }
      
      // Activar modo multi-red si hay más de una seleccionada
      setModoMultiRed(newSet.size > 1);
      
      return newSet;
    });
  };

  // 🆕 Publicación multi-red
  const publicarMultiRed = async (textoActual: string, redes: string[]) => {
    try {
      const endpoint = 'http://127.0.0.1:8000/api/posts/publish-multi';

      const controller = new AbortController();
      // Timeout más largo para multi-red (3 minutos)
      const timeoutId = setTimeout(() => controller.abort(), 180000);

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,  // 🔒 Agregar token
        },
        body: JSON.stringify({
          text: textoActual,
          target_networks: redes,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const data = await response.json();

      if (!response.ok) {
        const errorDetail = data.detail as ErrorDetail | string;
        const errorMessage = typeof errorDetail === 'string' 
          ? errorDetail 
          : errorDetail?.mensaje || errorDetail?.error || 'Error al publicar';
        throw new Error(errorMessage);
      }

      return data as ResultadoMultiRed;
    } catch (error) {
      throw error;
    }
  };

  // 🆕 Publicación individual (mantiene compatibilidad)
  const publicarIndividual = async (textoActual: string, red: string) => {
    let endpoint = '';
    if (red === 'facebook') {
      endpoint = 'http://127.0.0.1:8000/api/test/facebook';
    } else if (red === 'instagram') {
      endpoint = 'http://127.0.0.1:8000/api/test/instagram';
    } else if (red === 'linkedin') {
      endpoint = 'http://127.0.0.1:8000/api/test/linkedin';
    } else if (red === 'whatsapp') {
      endpoint = 'http://127.0.0.1:8000/api/test/whatsapp';
    } else if (red === 'tiktok') {
      endpoint = 'http://127.0.0.1:8000/api/test/tiktok';
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,  // 🔒 Agregar token
      },
      body: JSON.stringify({
        text: textoActual,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    const data = await response.json();

    if (!response.ok) {
      const errorDetail = data.detail as ErrorDetail | string;
      const errorMessage = typeof errorDetail === 'string' 
        ? errorDetail 
        : errorDetail?.mensaje || errorDetail?.error || 'Error al publicar';
      throw new Error(errorMessage);
    }

    return data;
  };

  const publicar = async () => {
    if (isPublishingRef.current || loading) {
      console.log('⚠️ Ya hay una publicación en proceso');
      return;
    }

    if (!texto.trim()) {
      agregarMensaje({
        id: Date.now(),
        tipo: 'error',
        texto: 'Por favor, ingresa un texto',
        redSocial: '',
        timestamp: new Date()
      });
      return;
    }

    if (redesSeleccionadas.size === 0) {
      agregarMensaje({
        id: Date.now(),
        tipo: 'error',
        texto: 'Por favor, selecciona al menos una red social',
        redSocial: '',
        timestamp: new Date()
      });
      return;
    }

    isPublishingRef.current = true;

    const redesArray = Array.from(redesSeleccionadas);
    
    agregarMensaje({
      id: Date.now(),
      tipo: 'usuario',
      texto: texto,
      redSocial: modoMultiRed ? 'multi-red' : redesArray[0],
      redesSeleccionadas: redesArray,
      timestamp: new Date()
    });

    const textoActual = texto;
    setTexto('');
    setLoading(true);

    try {
      if (modoMultiRed) {
        // 🆕 PUBLICACIÓN MULTI-RED
        const resultadoMulti = await publicarMultiRed(textoActual, redesArray);
        
        agregarMensaje({
          id: Date.now() + 1,
          tipo: 'multi-red',
          texto: `📊 Publicación en ${redesArray.length} redes completada`,
          redSocial: 'multi-red',
          redesSeleccionadas: redesArray,
          resultadoMultiRed: resultadoMulti,
          timestamp: new Date()
        });
      } else {
        // Publicación individual (comportamiento original)
        const red = redesArray[0];
        const data = await publicarIndividual(textoActual, red);

        // Normalizar la respuesta según la red social
        let resultadoNormalizado: Resultado;

        if (red === 'whatsapp') {
          resultadoNormalizado = {
            validacion: data.validacion || { es_academico: true, razon: 'Validado' },
            adaptacion: data.adaptacion || { text: textoActual, hashtags: [], character_count: textoActual.length },
            mensaje: data.mensaje || '✅ Mensaje enviado',
            envio: data.envio || { message_sid: 'N/A', status: 'enviado', to: 'N/A' },
            publicacion: {
              id: data.envio?.message_sid || 'N/A',
              link: undefined
            }
          };
        } else {
          resultadoNormalizado = data as Resultado;
        }

        agregarMensaje({
          id: Date.now() + 1,
          tipo: 'sistema',
          texto: `✅ Publicado en ${red}`,
          redSocial: red,
          resultado: resultadoNormalizado,
          timestamp: new Date()
        });
      }

    } catch (err) {
      let errorMessage = 'Error desconocido';
      
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          errorMessage = 'Tiempo de espera agotado. Intenta de nuevo.';
        } else {
          errorMessage = err.message;
        }
      }
      
      agregarMensaje({
        id: Date.now() + 2,
        tipo: 'error',
        texto: errorMessage,
        redSocial: '',
        timestamp: new Date()
      });
    } finally {
      setLoading(false);
      isPublishingRef.current = false;
      
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault();
      publicar();
    }
  };

  const getIconoRedSocial = (red: string) => {
    switch(red) {
      case 'facebook': return '📘';
      case 'instagram': return '📸';
      case 'linkedin': return '💼';
      case 'whatsapp': return '💬';
      case 'tiktok': return '🎵';
      case 'multi-red': return '🌐';
      default: return '📱';
    }
  };

  const getSocialIcon = (red: string) => {
    switch(red) {
      case 'facebook': return (
        <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
      );
      case 'instagram': return (
        <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
        </svg>
      );
      case 'linkedin': return (
        <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
      );
      case 'whatsapp': return (
        <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
        </svg>
      );
      case 'tiktok': return (
        <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
          <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-5.2 1.74 2.89 2.89 0 012.31-4.64 2.93 2.93 0 01.88.13V9.4a6.84 6.84 0 00-1-.05A6.33 6.33 0 005 20.1a6.34 6.34 0 0010.86-4.43v-7a8.16 8.16 0 004.77 1.52v-3.4a4.85 4.85 0 01-1.04-.1z"/>
        </svg>
      );
      default: return null;
    }
  };

  return (
    <div className="app-chat">
      
      {/* 🆕 Mostrar Login si no está autenticado */}
      {!isAuthenticated ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <>
          {/* 🆕 Header con información de usuario */}
          <div className="app-header">
            <div className="header-left">
              <h1>🎓 Sistema Multi-Red Social</h1>
              <p>UAGRM - Gestión de Contenido Académico</p>
            </div>
            <div className="header-right">
              <div className="user-info">
                <span className="user-icon">👤</span>
                <span className="user-name">{currentUser?.username}</span>
              </div>
              <button className="logout-button" onClick={handleLogout}>
                🚪 Cerrar Sesión
              </button>
            </div>
          </div>

          {/* Área de chat */}
          <div className="chat-container">
            <div className="chat-messages">
              {mensajes.length === 0 && (
                <div className="welcome-message">
                  <h2>👋 ¡Bienvenido, {currentUser?.username}!</h2>
              <p>Escribe tu contenido académico y selecciona las redes sociales donde quieres publicarlo.</p>
              <div className="features">
                <div className="feature">✨ Adaptación automática con IA</div>
                <div className="feature">📝 Validación de contenido académico</div>
                <div className="feature">🚀 Publicación individual o múltiple</div>
                <div className="feature">🌐 Multi-red simultánea</div>
              </div>
            </div>
          )}

          {mensajes.map((mensaje) => (
            <div key={mensaje.id} className={`message message-${mensaje.tipo}`}>
              <div className="message-header">
                <span className="message-icon">
                  {mensaje.tipo === 'usuario' ? '👤' : mensaje.tipo === 'error' ? '❌' : '🤖'}
                </span>
                <span className="message-time">
                  {mensaje.timestamp.toLocaleTimeString('es-BO', { hour: '2-digit', minute: '2-digit' })}
                </span>
                {mensaje.tipo === 'usuario' && (
                  <span className="message-red-social">
                    {modoMultiRed ? (
                      <>
                        🌐 {mensaje.redesSeleccionadas?.map(r => getIconoRedSocial(r)).join(' ')}
                      </>
                    ) : (
                      <>
                        {getIconoRedSocial(mensaje.redSocial)} {mensaje.redSocial}
                      </>
                    )}
                  </span>
                )}
              </div>

              <div className="message-content">
                {mensaje.tipo === 'usuario' && (
                  <div className="user-message">
                    <p>{mensaje.texto}</p>
                    {mensaje.redesSeleccionadas && mensaje.redesSeleccionadas.length > 1 && (
                      <div className="selected-networks">
                        <strong>Redes seleccionadas:</strong> {mensaje.redesSeleccionadas.join(', ')}
                      </div>
                    )}
                  </div>
                )}

                {mensaje.tipo === 'error' && (
                  <div className="error-message">
                    <strong>Error:</strong> {mensaje.texto}
                  </div>
                )}

                {/* 🆕 RESULTADO MULTI-RED */}
                {mensaje.tipo === 'multi-red' && mensaje.resultadoMultiRed && (
                  <div className="system-message multi-red-result">
                    <div className="result-header">
                      <h3>{mensaje.texto}</h3>
                    </div>
                  

                    {/* Resultados por Red Social */}
                    <div className="result-section">
                      <h4>🌐 Resultados por Red Social</h4>
                      <div className="networks-results">
                        {Object.entries(mensaje.resultadoMultiRed.resultados).map(([red, resultado]) => (
                          <div key={red} className={`network-result ${resultado.estado}`}>
                            <div className="network-header">
                              <span className="network-icon">{getIconoRedSocial(red)}</span>
                              <span className="network-name">{red.toUpperCase()}</span>
                              <span className={`network-status ${resultado.estado}`}>
                                {resultado.estado === 'exitoso' ? '✅' : '❌'}
                              </span>
                            </div>

                            {resultado.estado === 'exitoso' ? (
                              <div className="network-success-details">
                                {/* Texto adaptado */}
                                {resultado.adaptacion && (
                                  <div className="adapted-text-mini">
                                    {resultado.adaptacion.text.substring(0, 150)}...
                                    <div className="hashtags-container-mini">
                                      {resultado.adaptacion.hashtags?.slice(0, 3).map((tag, idx) => (
                                        <span key={idx} className="hashtag-mini">{tag}</span>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Link de publicación */}
                                {resultado.link && (
                                  <a 
                                    href={resultado.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="view-post-btn-mini"
                                  >
                                    Ver Publicación →
                                  </a>
                                )}

                                {/* Share URL para TikTok */}
                                {resultado.share_url && (
                                  <a 
                                    href={resultado.share_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="view-post-btn-mini"
                                  >
                                    Ver Video en TikTok →
                                  </a>
                                )}

                                {/* Info adicional para TikTok */}
                                {red === 'tiktok' && resultado.como_ver && (
                                  <div className="tiktok-info">
                                    <p><strong>Cuenta:</strong> {resultado.cuenta}</p>
                                    <p><strong>Visibilidad:</strong> {resultado.visibilidad}</p>
                                    {resultado.nota && <p className="tiktok-note">{resultado.nota}</p>}
                                  </div>
                                )}

                                {resultado.id && <p className="network-id">ID: <code>{resultado.id}</code></p>}
                              </div>
                            ) : (
                              <div className="network-error-details">
                                <p className="error-message">{resultado.error || resultado.mensaje}</p>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* RESULTADO INDIVIDUAL (comportamiento original) */}
                {mensaje.tipo === 'sistema' && mensaje.resultado && (
                  <div className="system-message">
                    <div className="result-header">
                      <h3>{mensaje.texto}</h3>
                    </div>

                    {/* Validación */}
                    {mensaje.resultado.validacion && (
                      <div className="result-section">
                        <h4>📋 Validación</h4>
                        <div className="validation-badge">
                          {mensaje.resultado.validacion.es_academico ? '✅ Contenido Académico' : '❌ No Académico'}
                        </div>
                        <p className="validation-reason">{mensaje.resultado.validacion.razon}</p>
                      </div>
                    )}

                    {/* Texto Adaptado */}
                    {mensaje.resultado.adaptacion && (
                      <div className="result-section">
                        <h4>✨ Texto Adaptado</h4>
                        <div className="adapted-text">
                          {mensaje.resultado.adaptacion.text}
                        </div>
                        {mensaje.resultado.adaptacion.hashtags && mensaje.resultado.adaptacion.hashtags.length > 0 && (
                          <div className="hashtags-container">
                            {mensaje.resultado.adaptacion.hashtags.map((tag, idx) => (
                              <span key={idx} className="hashtag">{tag}</span>
                            ))}
                          </div>
                        )}
                        <div className="char-count">
                          {mensaje.resultado.adaptacion.character_count} caracteres
                        </div>
                      </div>
                    )}

                    {/* Imagen Generada (Instagram) */}
                    {mensaje.resultado.imagen_generada && (
                      <div className="result-section">
                        <h4>🎨 Imagen Generada</h4>
                        <img 
                          src={mensaje.resultado.imagen_generada.url} 
                          alt="Imagen generada" 
                          className="generated-image"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      </div>
                    )}

                    {/* Link de Publicación o Estado de Envío */}
                    <div className="result-section">
                      <h4>🔗 Detalles</h4>
                      
                      {/* Para WhatsApp: mostrar info de envío */}
                      {mensaje.redSocial === 'whatsapp' && mensaje.resultado.envio ? (
                        <>
                          <p><strong>Message SID:</strong> <code>{mensaje.resultado.envio.message_sid}</code></p>
                          <p><strong>Estado:</strong> <span className="status-badge">{mensaje.resultado.envio.status}</span></p>
                          <p><strong>Enviado a:</strong> {mensaje.resultado.envio.to}</p>
                          <div className="whatsapp-note">
                            💬 El mensaje fue enviado por WhatsApp. Revisa tu aplicación móvil.
                          </div>
                        </>
                      ) : (
                        /* Para otras redes: mostrar link y ID */
                        <>
                          {mensaje.resultado.publicacion && (
                            <>
                              <p><strong>ID:</strong> <code>{mensaje.resultado.publicacion.id}</code></p>
                              {mensaje.resultado.publicacion.link && (
                                <a 
                                  href={mensaje.resultado.publicacion.link}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="view-post-btn"
                                >
                                  Ver Publicación →
                                </a>
                              )}
                            </>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message message-loading">
              <div className="message-header">
                <span className="message-icon">⏳</span>
                <span className="message-time">Ahora</span>
              </div>
              <div className="message-content">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p>
                  {modoMultiRed 
                    ? `Publicando en ${redesSeleccionadas.size} redes sociales...` 
                    : 'Procesando tu publicación...'}
                </p>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          {/* 🆕 Indicador de modo multi-red */}
          {/* {modoMultiRed && (
            <div className="multi-red-indicator">
              🌐 Modo Multi-Red Activo ({redesSeleccionadas.size} redes seleccionadas)
            </div>
          )} */}

          {/* Selector de red social con selección múltiple */}
          <div className="social-selector">
            <button
              className={`social-btn social-btn-facebook ${redesSeleccionadas.has('facebook') ? 'active' : ''}`}
              onClick={() => toggleRedSocial('facebook')}
              title="Facebook"
            >
              {getSocialIcon('facebook')}
            </button>
            <button
              className={`social-btn social-btn-instagram ${redesSeleccionadas.has('instagram') ? 'active' : ''}`}
              onClick={() => toggleRedSocial('instagram')}
              title="Instagram"
            >
              {getSocialIcon('instagram')}
            </button>
            <button
              className={`social-btn social-btn-linkedin ${redesSeleccionadas.has('linkedin') ? 'active' : ''}`}
              onClick={() => toggleRedSocial('linkedin')}
              title="LinkedIn"
            >
              {getSocialIcon('linkedin')}
            </button>
            <button
              className={`social-btn social-btn-whatsapp ${redesSeleccionadas.has('whatsapp') ? 'active' : ''}`}
              onClick={() => toggleRedSocial('whatsapp')}
              title="WhatsApp"
            >
              {getSocialIcon('whatsapp')}
            </button>
            <button
              className={`social-btn social-btn-tiktok ${redesSeleccionadas.has('tiktok') ? 'active' : ''}`}
              onClick={() => toggleRedSocial('tiktok')}
              title="TikTok"
            >
              {getSocialIcon('tiktok')}
            </button>
          </div>

          {/* Input de texto */}
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              className="chat-input"
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                modoMultiRed 
                  ? `Escribe tu contenido para publicar en ${redesSeleccionadas.size} redes...`
                  : `Escribe tu contenido académico para ${Array.from(redesSeleccionadas)[0]}...`
              }
              rows={3}
              disabled={loading}
            />
            <button
              className="send-button"
              onClick={publicar}
              disabled={loading || !texto.trim()}
            >
              {loading ? '⏳' : modoMultiRed ? '🌐' : '🚀'}
            </button>
          </div>

          <div className="input-hint">
            💡 {modoMultiRed 
              ? 'Click en los botones para agregar/quitar redes • Presiona Enter para publicar'
              : 'Presiona Enter para publicar • Shift+Enter para nueva línea'}
          </div>
        </div>
      </div>
      </>
      )}
    </div>
  );
}

export default App;