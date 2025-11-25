"""
Pruebas unitarias para la integración con WhatsApp
"""
import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import social_services


class TestWhatsAppIntegration:
    """Pruebas para la publicación de estados en WhatsApp"""
    
    def test_post_whatsapp_status_con_imagen_base64_exitoso(self, mocker):
        """
        Prueba publicación de estado con imagen en base64.
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "status_12345",
            "sent": True
        }
        mock_response.status_code = 200
        mock_response.text = '{"id": "status_12345"}'
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        
        # Ejecutar con imagen base64
        resultado = social_services.post_whatsapp_status(
            text="Estado de prueba FICCT",
            image_url="data:image/jpeg;base64,/9j/4AAQSkZJRg..."
        )
        
        # Verificaciones
        assert resultado["id"] == "status_12345"
        assert resultado["status"] == "publicado"
        assert mock_post.called
        
        # Verificar payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "media" in payload
        assert payload["caption"] == "Estado de prueba FICCT"
    
    
    def test_post_whatsapp_status_solo_texto_exitoso(self, mocker):
        """
        Prueba publicación de estado solo con texto (sin imagen).
        """
        mock_response = Mock()
        mock_response.json.return_value = {"id": "status_67890"}
        mock_response.status_code = 200
        mock_response.text = '{"id": "status_67890"}'
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        
        # Ejecutar sin imagen
        resultado = social_services.post_whatsapp_status(
            text="Anuncio importante UAGRM",
            image_url=None
        )
        
        # Verificaciones
        assert "id" in resultado
        assert mock_post.called
        
        # Verificar que se usó fondo de color
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "background_color" in payload
        assert "caption" in payload
        assert payload["caption"] == "Anuncio importante UAGRM"
    
    
    def test_post_whatsapp_status_sin_token(self, mocker):
        """
        Prueba que maneje correctamente la falta de WHAPI_TOKEN.
        """
        mocker.patch("social_services.WHAPI_TOKEN", None)
        
        resultado = social_services.post_whatsapp_status(
            text="Test",
            image_url=None
        )
        
        # Debe retornar error
        assert "error" in resultado
        assert "WHAPI_TOKEN" in resultado["error"] or "configurado" in resultado["error"].lower()
    
    
    def test_post_whatsapp_status_error_api(self, mocker):
        """
        Prueba manejo de errores de la API de Whapi.Cloud.
        """
        from httpx import HTTPStatusError, Request, Response
        
        mock_request = Mock(spec=Request)
        mock_error_response = Mock(spec=Response)
        mock_error_response.json.return_value = {
            "error": "Invalid media format"
        }
        mock_error_response.text = '{"error": "Invalid media format"}'
        
        http_error = HTTPStatusError(
            "Error",
            request=mock_request,
            response=mock_error_response
        )
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_post.side_effect = http_error
        
        resultado = social_services.post_whatsapp_status(
            text="Test",
            image_url="invalid_data"
        )
        
        # Verificar error
        assert "error" in resultado
    
    
    def test_post_whatsapp_status_verifica_headers(self, mocker):
        """
        Prueba que WhatsApp envíe los headers correctos.
        """
        mock_response = Mock()
        mock_response.json.return_value = {"id": "test_status"}
        mock_response.status_code = 200
        mock_response.text = '{"id": "test_status"}'
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        mocker.patch("social_services.WHAPI_TOKEN", "test_whapi_token_123")
        
        resultado = social_services.post_whatsapp_status("Test")
        
        # Verificar headers
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]
        
        assert headers["Authorization"] == "Bearer test_whapi_token_123"
        assert headers["Content-Type"] == "application/json"
    
    
    def test_post_whatsapp_status_verifica_endpoint(self, mocker):
        """
        Prueba que use el endpoint correcto de Whapi.Cloud.
        """
        mock_response = Mock()
        mock_response.json.return_value = {"id": "test"}
        mock_response.status_code = 200
        mock_response.text = '{"id": "test"}'
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        mocker.patch("social_services.WHAPI_BASE_URL", "https://gate.whapi.cloud")
        
        resultado = social_services.post_whatsapp_status("Test")
        
        # Verificar URL
        call_args = mock_post.call_args
        url = call_args[0][0]
        assert "https://gate.whapi.cloud/stories" in url
    
    
    def test_post_whatsapp_status_parametros_texto(self, mocker):
        """
        Prueba los parámetros correctos para estado de solo texto.
        """
        mock_response = Mock()
        mock_response.json.return_value = {"id": "text_status"}
        mock_response.status_code = 200
        mock_response.text = '{"id": "text_status"}'
        mock_response.raise_for_status = Mock()
        
        mock_post = mocker.patch("social_services.httpx.post", return_value=mock_response)
        
        resultado = social_services.post_whatsapp_status(
            text="Mensaje de prueba",
            image_url=None
        )
        
        # Verificar parámetros
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        
        assert payload["background_color"] == "#1F2937"
        assert payload["caption"] == "Mensaje de prueba"
        assert payload["caption_color"] == "#FFFFFF"
        assert payload["font_type"] == "SYSTEM"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])