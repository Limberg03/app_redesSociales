import { useState } from 'react';
import './App.css';

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
  publicacion: Publicacion;
  mensaje: string;
}

interface ErrorDetail {
  mensaje?: string;
  error?: string;
}

function App() {
  const [texto, setTexto] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [redSocial, setRedSocial] = useState<'facebook' | 'instagram'>('facebook');

  const publicar = async () => {
    if (!texto.trim()) {
      setError('Por favor, ingresa un texto');
      return;
    }

    setLoading(true);
    setError(null);
    setResultado(null);

    try {
      const endpoint = redSocial === 'facebook' 
        ? 'http://127.0.0.1:8000/api/test/facebook'
        : 'http://127.0.0.1:8000/api/test/instagram';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: texto,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const errorDetail = data.detail as ErrorDetail | string;
        const errorMessage = typeof errorDetail === 'string' 
          ? errorDetail 
          : errorDetail?.mensaje || errorDetail?.error || 'Error al publicar';
        throw new Error(errorMessage);
      }

      setResultado(data as Resultado);
      setTexto(''); // Limpiar el campo después de publicar
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1> Sistema de Publicación Académica</h1>
        <p className="subtitle">UAGRM - Gestión de Redes Sociales</p>

        <div className="card">
          <div className="form-group">
            <label>Red Social:</label>
            <div className="radio-group">
              <label className="radio-label">
                <input
                  type="radio"
                  value="facebook"
                  checked={redSocial === 'facebook'}
                  onChange={(e) => setRedSocial(e.target.value as 'facebook')}
                />
                <span> Facebook</span>
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  value="instagram"
                  checked={redSocial === 'instagram'}
                  onChange={(e) => setRedSocial(e.target.value as 'instagram')}
                />
                <span> Instagram</span>
              </label>
            </div>
          </div>

          <div className="form-group">
            <label>Contenido Académico:</label>
            <textarea
              className="textarea"
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder="Ej: La UAGRM habilitó el retiro de materias hasta el 30 de noviembre"
              rows={5}
            />
          
          </div>

          <button
            className={`btn ${loading ? 'btn-loading' : ''}`}
            onClick={publicar}
            disabled={loading}
          >
            {loading ? '⏳ Publicando...' : '🚀 Publicar'}
          </button>
        </div>

        {error && (
          <div className="alert alert-error">
            <strong>❌ Error:</strong> {error}
          </div>
        )}

        {resultado && (
          <div className="card result-card">
            <h2>✅ Publicación Exitosa</h2>

            <div className="result-section">
              <h3>📝 Validación</h3>
              <p><strong>Es académico:</strong> {resultado.validacion.es_academico ? 'Sí' : 'No'}</p>
              <p><strong>Razón:</strong> {resultado.validacion.razon}</p>
            </div>

            <div className="result-section">
              <h3>✨ Texto Adaptado</h3>
              <div className="texto-adaptado">
                {resultado.adaptacion.text}
              </div>
              <div className="hashtags">
                {resultado.adaptacion.hashtags.map((tag, index) => (
                  <span key={index} className="hashtag">{tag}</span>
                ))}
              </div>
            </div>

            {resultado.imagen_generada && (
              <div className="result-section">
                <h3>🎨 Imagen Generada</h3>
                <img 
                  src={resultado.imagen_generada.url} 
                  alt="Imagen generada" 
                  className="imagen-preview"
                />
                <p className="image-prompt"><strong>Prompt:</strong> {resultado.imagen_generada.prompt}</p>
              </div>
            )}

            <div className="result-section">
              <h3>🔗 Publicación</h3>
              <p><strong>ID:</strong> {resultado.publicacion.id}</p>
              {resultado.publicacion.link && (
                <a 
                  href={resultado.publicacion.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="link-btn"
                >
                  Ver Publicación 🔗
                </a>
              )}
            </div>

            <p className="success-message">{resultado.mensaje}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;