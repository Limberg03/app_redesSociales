"""
Pruebas unitarias para la integración con TikTok
"""
import pytest
from unittest.mock import Mock, MagicMock, mock_open
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import social_services


class TestTikTokIntegration:
    """Pruebas para la publicación en TikTok"""
    
    def test_post_to_tiktok_exitoso(self, mocker):
        """
        Prueba el flujo completo de publicación en TikTok (Direct Post).
        """
        # Mock de archivo de video
        mock_file = mocker.mock_open(read_data=b"fake_video_content_12345")
        mocker.patch("builtins.open", mock_file)
        mocker.patch("os.path.exists", return_value=True)
        
        # Mock de respuesta de inicialización
        mock_init_response = Mock()
        mock_init_response.json.return_value = {
            "data": {
                "publish_id": "pub_12345",
                "upload_url": "https://upload.tiktok.com/test"
            }
        }
        mock_init_response.raise_for_status = Mock()
        mock_init_response.status_code = 200
        
        # Mock de respuesta de subida
        mock_upload_response = Mock()
        mock_upload_response.status_code = 200
        mock_upload_response.text = ""
        
        # Mock de respuesta de estado
        mock_status_response = Mock()
        mock_status_response.status_code = 200
        mock_status_response.json.return_value = {
            "data": {
                "status": "PUBLISHED",
                "publicaly_available_post_id_list": ["7123456789"]
            }
        }
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_put = mocker.patch("social_services.httpx.put")
        
        mock_post.side_effect = [mock_init_response, mock_status_response]
        mock_put.return_value = mock_upload_response
        
        # Mock de sleep para acelerar test
        mocker.patch("time.sleep")
        
        # Ejecutar
        resultado = social_services.post_to_tiktok(
            text="Video académico FICCT #UAGRM",
            video_path="/fake/path/video.mp4",
            privacy="SELF_ONLY"
        )
        
        # Verificaciones
        assert resultado["publish_id"] == "pub_12345"
        assert resultado["status"] == "published_private"
        assert resultado["privacy"] == "SELF_ONLY"
        assert mock_post.call_count >= 1
        assert mock_put.called
    
    
    def test_post_to_tiktok_sin_token(self, mocker):
        """
        Prueba que maneje la falta de TIKTOK_ACCESS_TOKEN.
        """
        mocker.patch("social_services.TIKTOK_TOKEN", None)
        
        resultado = social_services.post_to_tiktok(
            text="Test",
            video_path="/fake/video.mp4",
            privacy="SELF_ONLY"
        )
        
        # Debe retornar error
        assert "error" in resultado
        assert "configurado" in resultado["error"].lower()
    
    
    def test_post_to_tiktok_video_no_existe(self, mocker):
        """
        Prueba que maneje el caso cuando el video no existe.
        """
        mocker.patch("os.path.exists", return_value=False)
        mocker.patch("social_services.TIKTOK_TOKEN", "test_token")
        
        resultado = social_services.post_to_tiktok(
            text="Test",
            video_path="/nonexistent/video.mp4",
            privacy="SELF_ONLY"
        )
        
        # Debe retornar error
        assert "error" in resultado
        assert "no encontrado" in resultado["error"].lower()
    
    
    def test_post_to_tiktok_error_inicializacion(self, mocker):
        """
        Prueba manejo de errores en la inicialización.
        """
        from httpx import HTTPStatusError, Request, Response
        
        mocker.patch("os.path.exists", return_value=True)
        mock_file = mocker.mock_open(read_data=b"video_content")
        mocker.patch("builtins.open", mock_file)
        
        mock_request = Mock(spec=Request)
        mock_error_response = Mock(spec=Response)
        mock_error_response.json.return_value = {
            "error": {
                "code": "invalid_params",
                "message": "Invalid video parameters"
            }
        }
        
        http_error = HTTPStatusError(
            "Error",
            request=mock_request,
            response=mock_error_response
        )
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_post.side_effect = http_error
        
        resultado = social_services.post_to_tiktok(
            text="Test",
            video_path="/fake/video.mp4"
        )
        
        # Verificar error
        assert "error" in resultado
    
    
    def test_post_to_tiktok_error_subida_video(self, mocker):
        """
        Prueba manejo de errores en la subida del video.
        """
        mocker.patch("os.path.exists", return_value=True)
        mock_file = mocker.mock_open(read_data=b"video_data")
        mocker.patch("builtins.open", mock_file)
        
        # Inicialización exitosa
        mock_init_response = Mock()
        mock_init_response.json.return_value = {
            "data": {
                "publish_id": "pub_test",
                "upload_url": "https://upload.tiktok.com/test"
            }
        }
        mock_init_response.raise_for_status = Mock()
        
        # Subida con error
        mock_upload_response = Mock()
        mock_upload_response.status_code = 400
        mock_upload_response.text = "Upload failed"
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_put = mocker.patch("social_services.httpx.put")
        
        mock_post.return_value = mock_init_response
        mock_put.return_value = mock_upload_response
        
        resultado = social_services.post_to_tiktok(
            text="Test",
            video_path="/fake/video.mp4"
        )
        
        # Verificar error de subida
        assert "error" in resultado
        assert resultado["error"] == "upload_failed"
    
    
    def test_post_to_tiktok_verifica_payload_inicializacion(self, mocker):
        """
        Prueba que el payload de inicialización sea correcto.
        """
        mocker.patch("os.path.exists", return_value=True)
        mock_file = mocker.mock_open(read_data=b"video_content_test")
        mocker.patch("builtins.open", mock_file)
        
        mock_init_response = Mock()
        mock_init_response.json.return_value = {
            "data": {
                "publish_id": "pub_test",
                "upload_url": "https://test.com"
            }
        }
        mock_init_response.raise_for_status = Mock()
        
        mock_upload_response = Mock()
        mock_upload_response.status_code = 200
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_put = mocker.patch("social_services.httpx.put")
        
        mock_post.return_value = mock_init_response
        mock_put.return_value = mock_upload_response
        mocker.patch("time.sleep")
        
        resultado = social_services.post_to_tiktok(
            text="Video de prueba académico",
            video_path="/fake/video.mp4",
            privacy="SELF_ONLY"
        )
        
        # Verificar payload
        call_args = mock_post.call_args_list[0]
        payload = call_args[1]["json"]
        
        assert payload["post_info"]["title"] == "Video de prueba académico"
        assert payload["post_info"]["privacy_level"] == "SELF_ONLY"
        assert payload["post_info"]["disable_duet"] == False
        assert payload["post_info"]["disable_comment"] == False
        assert payload["source_info"]["source"] == "FILE_UPLOAD"
    
    
    def test_post_to_tiktok_verifica_headers_subida(self, mocker):
        """
        Prueba que los headers de subida sean correctos.
        """
        mocker.patch("os.path.exists", return_value=True)
        video_content = b"test_video_bytes"
        mock_file = mocker.mock_open(read_data=video_content)
        mocker.patch("builtins.open", mock_file)
        
        mock_init_response = Mock()
        mock_init_response.json.return_value = {
            "data": {
                "publish_id": "pub_test",
                "upload_url": "https://upload.test.com"
            }
        }
        mock_init_response.raise_for_status = Mock()
        
        mock_upload_response = Mock()
        mock_upload_response.status_code = 200
        
        mock_post = mocker.patch("social_services.httpx.post")
        mock_put = mocker.patch("social_services.httpx.put")
        
        mock_post.return_value = mock_init_response
        mock_put.return_value = mock_upload_response
        mocker.patch("time.sleep")
        
        resultado = social_services.post_to_tiktok(
            text="Test",
            video_path="/fake/video.mp4"
        )
        
        # Verificar headers de PUT
        put_call = mock_put.call_args
        headers = put_call[1]["headers"]
        
        assert headers["Content-Type"] == "video/mp4"
        assert "Content-Length" in headers
        assert "Content-Range" in headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])