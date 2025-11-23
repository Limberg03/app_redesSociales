from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Captura el callback de TikTok"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/callback':
            params = parse_qs(parsed_path.query)
            code = params.get('code', [''])[0]
            
            if code:
                # Guardar el code
                with open('tiktok_code.txt', 'w') as f:
                    f.write(code)
                
                # Responder al navegador
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                response = f"""
                <html>
                <head>
                    <title>Autorización Exitosa</title>
                    <style>
                        body {{
                            font-family: Arial;
                            text-align: center;
                            padding: 50px;
                            background: #667eea;
                            color: white;
                        }}
                        .box {{
                            background: white;
                            color: #333;
                            padding: 40px;
                            border-radius: 10px;
                            max-width: 500px;
                            margin: 0 auto;
                        }}
                        h1 {{ color: #28a745; }}
                    </style>
                </head>
                <body>
                    <div class="box">
                        <h1>✅ ¡Autorización Exitosa!</h1>
                        <p>Code capturado: {code[:30]}...</p>
                        <p>Puedes cerrar esta ventana</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(response.encode())
                print(f"\n✅ Code capturado: {code[:20]}...")
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('', 3000), CallbackHandler)
    print("🚀 Servidor iniciado en puerto 3000")
    print("⏳ Esperando callback de TikTok...\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")