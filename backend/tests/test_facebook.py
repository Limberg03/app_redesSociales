"""
Pruebas unitarias para la integración con Facebook
"""
import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import social_services


class TestFacebookIntegration:
    """Pruebas para la publicación en Facebook"""
    
    def test_post_to_facebook_solo_texto_exitoso(self, mocker):
        """
        Prueba que post_to_facebook publique correctamente un mensaje de solo texto.
        """
        # 1. Preparar mock de respuesta exitosa
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123456789_987654321"
        }
        mock_response.raise_for_status = Mock()  # No lanza error
        
        # 2. Simular httpx.post
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        
        # 3. Ejecutar función
        resultado = social_services.post_to_facebook(
            text="La UAGRM anuncia nuevas inscripciones",
            image_url=None
        )
        
        # 4. Verificaciones
        assert resultado["id"] == "123456789_987654321"
        assert mock_post.called
        
        # Verificar que se llamó con los parámetros correctos
        call_args = mock_post.call_args[1]
        assert "message" in call_args["data"]
        assert call_args["data"]["message"] == "La UAGRM anuncia nuevas inscripciones"
        assert "access_token" in call_args["data"]
    
    
    def test_post_to_facebook_con_imagen_exitoso(self, mocker):
        """
        Prueba que post_to_facebook publique correctamente con imagen.
        """
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123456789_111111111",
            "post_id": "123456789_111111111"
        }
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        
        # Ejecutar con imagen
        resultado = social_services.post_to_facebook(
            text="Evento académico FICCT",
            image_url="https://example.com/imagen.jpg"
        )
        
        # Verificaciones
        assert "id" in resultado or "post_id" in resultado
        assert mock_post.called
        
        # Verificar que se usó el endpoint de photos
        call_args = mock_post.call_args
        assert "photos" in call_args[0][0]  # URL debe contener 'photos'
        assert "caption" in call_args[1]["data"]
        assert "url" in call_args[1]["data"]
    
    
    def test_post_to_facebook_error_de_api(self, mocker):
        """
        Prueba que post_to_facebook maneje correctamente errores de la API.
        """
        # Mock de respuesta con error
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid OAuth access token",
                "code": 190
            }
        }
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        
        # Simular httpx.HTTPStatusError
        from httpx import HTTPStatusError, Request, Response
        mock_request = Mock(spec=Request)
        mock_error_response = Mock(spec=Response)
        mock_error_response.json.return_value = {
            "error": {
                "message": "Invalid OAuth access token",
                "code": 190
            }
        }
        
        http_error = HTTPStatusError(
            "Error", 
            request=mock_request, 
            response=mock_error_response
        )
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_post.side_effect = http_error
        
        # Ejecutar
        resultado = social_services.post_to_facebook("Test")
        
        # Verificar que retorna error
        assert "error" in resultado
        assert mock_post.called
    
    
    def test_post_to_facebook_sin_texto(self, mocker):
        """
        Prueba que post_to_facebook maneje el caso de texto vacío.
        """
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123_456"}
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        
        # Ejecutar con texto vacío
        resultado = social_services.post_to_facebook(text="", image_url=None)
        
        # Debe llamar a la API incluso con texto vacío
        assert mock_post.called
    
    
    def test_post_to_facebook_verifica_variables_entorno(self, mocker):
        """
        Prueba que post_to_facebook use correctamente las variables de entorno.
        """
        mock_response = Mock()
        mock_response.json.return_value = {"id": "test_id"}
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        
        # Mock de variables de entorno
        mocker.patch("social_services.META_TOKEN", "test_token_12345")
        mocker.patch("social_services.PAGE_ID", "test_page_67890")
        
        resultado = social_services.post_to_facebook("Test message")
        
        # Verificar que se usaron las variables correctas
        call_args = mock_post.call_args
        assert "test_page_67890" in call_args[0][0]  # PAGE_ID en URL
        assert call_args[1]["data"]["access_token"] == "test_token_12345"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])