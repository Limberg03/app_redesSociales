"""
Pruebas unitarias para la integración con Instagram
"""
import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import social_services


class TestInstagramIntegration:
    """Pruebas para la publicación en Instagram"""
    
    def test_post_to_instagram_exitoso(self, mocker):
        """
        Prueba el flujo completo de publicación en Instagram (2 pasos).
        """
        # Mock del contenedor (paso 1)
        mock_container_response = Mock()
        mock_container_response.json.return_value = {"id": "container_12345"}
        mock_container_response.raise_for_status = Mock()
        
        # Mock de publicación (paso 2)
        mock_publish_response = Mock()
        mock_publish_response.json.return_value = {"id": "media_67890"}
        mock_publish_response.raise_for_status = Mock()
        
        # Mock de permalink (paso 3)
        mock_permalink_response = Mock()
        mock_permalink_response.json.return_value = {
            "id": "media_67890",
            "permalink": "https://www.instagram.com/p/ABC123/"
        }
        mock_permalink_response.raise_for_status = Mock()
        
        # Simular las 3 llamadas HTTP
        mock_post = mocker.patch("social_services.httpx.post")
        mock_get = mocker.patch("social_services.httpx.get")
        
        mock_post.side_effect = [mock_container_response, mock_publish_response]
        mock_get.return_value = mock_permalink_response
        
        # Ejecutar
        resultado = social_services.post_to_instagram(
            text="Nuevo post académico #UAGRM",
            image_url="https://example.com/image.jpg"
        )
        
        # Verificaciones
        assert resultado["id"] == "media_67890"
        assert resultado["permalink"] == "https://www.instagram.com/p/ABC123/"
        assert mock_post.call_count == 2  # Crear contenedor + publicar
        assert mock_get.call_count == 1   # Obtener permalink
    
    
    def test_post_to_instagram_sin_imagen(self, mocker):
        """
        Prueba que Instagram rechace publicaciones sin imagen.
        """
        resultado = social_services.post_to_instagram(
            text="Solo texto",
            image_url=None
        )
        
        # Instagram requiere imagen
        assert "error" in resultado
        assert "imagen" in resultado["error"].lower()
    
    
    def test_post_to_instagram_sin_account_id(self, mocker):
        """
        Prueba que maneje correctamente la falta de INSTAGRAM_ACCOUNT_ID.
        """
        # Simular que no hay IG_ACCOUNT_ID configurado
        mocker.patch("social_services.IG_ACCOUNT_ID", None)
        
        resultado = social_services.post_to_instagram(
            text="Test",
            image_url="https://example.com/test.jpg"
        )
        
        # Debe retornar error
        assert "error" in resultado
        assert "Account ID" in resultado["error"]
    
    
    def test_post_to_instagram_error_en_contenedor(self, mocker):
        """
        Prueba que maneje errores en la creación del contenedor (paso 1).
        """
        from httpx import HTTPStatusError, Request, Response
        
        mock_request = Mock(spec=Request)
        mock_error_response = Mock(spec=Response)
        mock_error_response.json.return_value = {
            "error": {
                "message": "Invalid image URL",
                "code": 100
            }
        }
        
        http_error = HTTPStatusError(
            "Error",
            request=mock_request,
            response=mock_error_response
        )
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_post.side_effect = http_error
        
        resultado = social_services.post_to_instagram(
            text="Test",
            image_url="https://invalid.com/image.jpg"
        )
        
        # Verificar error
        assert "error" in resultado
    
    
    def test_post_to_instagram_error_en_publicacion(self, mocker):
        """
        Prueba que maneje errores en el paso de publicación (paso 2).
        """
        from httpx import HTTPStatusError, Request, Response
        
        # Paso 1 exitoso
        mock_container_response = Mock()
        mock_container_response.json.return_value = {"id": "container_12345"}
        mock_container_response.raise_for_status = Mock()
        
        # Paso 2 con error
        mock_request = Mock(spec=Request)
        mock_error_response = Mock(spec=Response)
        mock_error_response.json.return_value = {
            "error": {
                "message": "Container not ready",
                "code": 9004
            }
        }
        
        http_error = HTTPStatusError(
            "Error",
            request=mock_request,
            response=mock_error_response
        )
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_post.side_effect = [mock_container_response, http_error]
        
        resultado = social_services.post_to_instagram(
            text="Test",
            image_url="https://example.com/image.jpg"
        )
        
        # Verificar error
        assert "error" in resultado            


if __name__ == "__main__":
    pytest.main([__file__, "-v"])