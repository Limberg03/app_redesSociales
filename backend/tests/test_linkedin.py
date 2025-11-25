"""
Pruebas unitarias para la integración con LinkedIn
"""
import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import social_services


class TestLinkedInIntegration:
    """Pruebas para la publicación en LinkedIn"""
    
    def test_get_linkedin_user_info_exitoso(self, mocker):
        """
        Prueba que get_linkedin_user_info obtenga correctamente el 'sub'.
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "sub": "user_12345",
            "name": "Test User",
            "email": "test@example.com"
        }
        mock_response.raise_for_status = Mock()
        
        mock_get = mocker.patch("social_services.httpx.get", return_value=mock_response)
        
        # Ejecutar
        user_sub = social_services.get_linkedin_user_info()
        
        # Verificaciones
        assert user_sub == "user_12345"
        assert mock_get.called
        
        # Verificar que se llamó al endpoint correcto
        call_args = mock_get.call_args
        assert "/v2/userinfo" in call_args[0][0]
    
    
    def test_get_linkedin_user_info_error_token(self, mocker):
        """
        Prueba que maneje errores de token inválido.
        """
        from httpx import HTTPStatusError, Request, Response
        
        mock_request = Mock(spec=Request)
        mock_error_response = Mock(spec=Response)
        mock_error_response.json.return_value = {
            "error": "invalid_token",
            "error_description": "The access token is invalid"
        }
        
        http_error = HTTPStatusError(
            "Error",
            request=mock_request,
            response=mock_error_response
        )
        
        mock_get = mocker.patch("social_services.httpx.get")
        mock_get.side_effect = http_error
        
        # Ejecutar
        user_sub = social_services.get_linkedin_user_info()
        
        # Debe retornar None en caso de error
        assert user_sub is None
    
    
    def test_post_to_linkedin_exitoso(self, mocker):
        """
        Prueba publicación exitosa en LinkedIn.
        """
        # Mock de get_linkedin_user_info
        mocker.patch("social_services.get_linkedin_user_info", return_value="user_test_123")
        
        # Mock de la publicación
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "urn:li:share:7123456789"
        }
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        
        # Ejecutar
        resultado = social_services.post_to_linkedin(
            text="Artículo profesional sobre educación superior"
        )
        
        # Verificaciones
        assert resultado["id"] == "urn:li:share:7123456789"
        assert mock_post.called
    
    
    def test_post_to_linkedin_sin_user_sub(self, mocker):
        """
        Prueba que maneje el caso cuando no se puede obtener el user sub.
        """
        # Mock que retorna None
        mocker.patch("social_services.get_linkedin_user_info", return_value=None)
        
        # Ejecutar
        resultado = social_services.post_to_linkedin("Test")
        
        # Debe retornar error
        assert "error" in resultado
        assert "identificador" in resultado["error"].lower()
    
                   
    
    def test_post_to_linkedin_error_api(self, mocker):
        """
        Prueba manejo de errores de la API de LinkedIn.
        """
        from httpx import HTTPStatusError, Request, Response
        
        mocker.patch("social_services.get_linkedin_user_info", return_value="sub_456")
        
        mock_request = Mock(spec=Request)
        mock_error_response = Mock(spec=Response)
        mock_error_response.json.return_value = {
            "status": 401,
            "message": "Unauthorized"
        }
        
        http_error = HTTPStatusError(
            "Error",
            request=mock_request,
            response=mock_error_response
        )
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_post.side_effect = http_error
        
        resultado = social_services.post_to_linkedin("Test")
        
        # Verificar error
        assert "error" in resultado


if __name__ == "__main__":
    pytest.main([__file__, "-v"])