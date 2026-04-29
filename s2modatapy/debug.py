"""
Módulo de Debug para S2MOdataPy
Author: Christopher N. S. M. Mauricio
"""

from datetime import datetime
import json
import requests


class DebugMonitor:
    """Monitor de debug para requisições OData"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
    
    def log_request(self, method: str, url: str, params: dict = None, 
                    data: dict = None):
        """Loga detalhes da requisição"""
        if not self.enabled:
            return
        
        print("\n" + "="*70)
        print(f"🔍 [S2MOdataPy DEBUG] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print("="*70)
        print(f"📡 Método: {method}")
        print(f"📍 URL: {url}")
        
        if params:
            print(f"\n📊 Parâmetros Query String:")
            for key, value in params.items():
                print(f"   {key} = {value}")
        
        if data:
            print(f"\n📦 Payload:")
            print(f"   {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    def log_response(self, response: requests.Response):
        """Loga detalhes da resposta"""
        if not self.enabled:
            return
        
        print(f"\n📥 Resposta Recebida:")
        print(f"   Status: {response.status_code} {response.reason}")
        print(f"   Tempo: {response.elapsed.total_seconds():.3f} segundos")
        
        # Tenta mostrar parte do conteúdo da resposta
        try:
            content_type = response.headers.get('content-type', '')
            if 'json' in content_type:
                data = response.json()
                if 'value' in data:
                    print(f"   Registros retornados: {len(data['value'])}")
                    if '@odata.count' in data:
                        print(f"   Total disponível: {data['@odata.count']}")
        except:
            pass
        
        print("="*70 + "\n")