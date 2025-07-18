import requests
import json
from typing import Optional, Dict, List, Any
from datetime import datetime

class SGUVApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.current_user = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers com token de autenticação se disponível"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Faz requisição HTTP para a API"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            # Retornar formato padronizado
            if isinstance(result, list):
                return {"success": True, "data": result}
            elif isinstance(result, dict):
                return {"success": True, "data": result}
            else:
                return {"success": True, "data": result}
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_message = error_detail.get('detail', str(e))
                except:
                    error_message = f"Erro HTTP {e.response.status_code}"
            
            return {"success": False, "message": error_message, "data": None}
    
    # Métodos de Autenticação
    def register(self, matricula: str, nome: str, email: str, senha: str, celular: str = "", unidade: str = "") -> Dict[str, Any]:
        """Registra um novo usuário"""
        data = {
            "matricula": matricula,
            "nome": nome,
            "email": email,
            "senha": senha,
            "celular": celular,
            "unidade": unidade
        }
        return self._make_request("POST", "/api/users/register", data)
    
    def login(self, email: str, senha: str) -> bool:
        """Faz login do usuário"""
        data = {"email": email, "senha": senha}
        result = self._make_request("POST", "/api/users/login", data)
        
        # A API retorna diretamente o token, o _make_request envolve em data
        if result.get("success"):
            token_data = result.get("data", {})
            self.token = token_data.get("access_token")
            if self.token:
                # Obter dados do usuário atual
                user_result = self.get_current_user()
                if user_result and user_result.get("success"):
                    self.current_user = user_result.get("data")
                    return True
        return False
    
    def logout(self):
        """Faz logout do usuário"""
        self.token = None
        self.current_user = None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Obtém dados do usuário atual"""
        if not self.token:
            return None
        return self._make_request("GET", "/api/users/me")
    
    # Métodos de Usuários
    def get_users(self) -> List[Dict[str, Any]]:
        """Lista todos os usuários"""
        return self._make_request("GET", "/api/users/")
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Obtém dados de um usuário específico"""
        return self._make_request("GET", f"/api/users/{user_id}")
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza dados de um usuário"""
        return self._make_request("PUT", f"/api/users/{user_id}", data)
    
    def activate_user(self, user_id: int) -> Dict[str, Any]:
        """Ativa um usuário"""
        return self._make_request("PUT", f"/api/users/{user_id}/activate")
    
    def deactivate_user(self, user_id: int) -> Dict[str, Any]:
        """Desativa um usuário"""
        return self._make_request("PUT", f"/api/users/{user_id}/deactivate")
    
    # Métodos de Veículos
    def get_vehicles(self) -> List[Dict[str, Any]]:
        """Lista todos os veículos"""
        return self._make_request("GET", "/api/vehicles/")
    
    def get_available_vehicles(self) -> List[Dict[str, Any]]:
        """Lista veículos disponíveis"""
        return self._make_request("GET", "/api/vehicles/disponiveis")
    
    def get_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        """Obtém dados de um veículo específico"""
        return self._make_request("GET", f"/api/vehicles/{vehicle_id}")
    
    def create_vehicle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo veículo"""
        return self._make_request("POST", "/api/vehicles/", data)
    
    def update_vehicle(self, vehicle_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza dados de um veículo"""
        return self._make_request("PUT", f"/api/vehicles/{vehicle_id}", data)
    
    # Métodos de Controle de Utilização
    def get_usage_controls(self) -> List[Dict[str, Any]]:
        """Lista controles de utilização"""
        return self._make_request("GET", "/api/usage-control/")
    
    def get_my_usage_controls(self) -> List[Dict[str, Any]]:
        """Lista meus controles de utilização"""
        return self._make_request("GET", "/api/usage-control/meus")
    
    def get_open_usage_controls(self) -> List[Dict[str, Any]]:
        """Lista controles de utilização em aberto"""
        return self._make_request("GET", "/api/usage-control/abertos")
    
    def create_usage_control(self, veiculo_id: int, km_inicial: float) -> Dict[str, Any]:
        """Cria um novo controle de utilização"""
        data = {
            "veiculo_id": veiculo_id,
            "data_inicio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "km_inicial": km_inicial
        }
        return self._make_request("POST", "/api/usage-control/", data)
    
    def finalize_usage_control(self, control_id: int, km_final: float, assinatura: str = "") -> Dict[str, Any]:
        """Finaliza um controle de utilização"""
        data = {
            "km_final": km_final,
            "data_fim": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "assinatura_eletronica": assinatura
        }
        return self._make_request("PUT", f"/api/usage-control/{control_id}/finalizar", data)
    
    # Métodos de Rotas
    def get_routes_by_control(self, control_id: int) -> List[Dict[str, Any]]:
        """Lista rotas de um controle de utilização"""
        return self._make_request("GET", f"/api/routes/controle/{control_id}")
    
    def create_route(self, control_id: int, km_saida: float, latitude_saida: float = None, longitude_saida: float = None, logradouro_saida: str = "") -> Dict[str, Any]:
        """Cria uma nova rota"""
        data = {
            "controle_utilizacao_id": control_id,
            "data_hora_saida": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "km_saida": km_saida,
            "latitude_saida": latitude_saida,
            "longitude_saida": longitude_saida,
            "logradouro_saida": logradouro_saida
        }
        return self._make_request("POST", "/api/routes/", data)
    
    def update_route_arrival(self, route_id: int, km_chegada: float, latitude_chegada: float = None, longitude_chegada: float = None, logradouro_chegada: str = "") -> Dict[str, Any]:
        """Atualiza dados de chegada de uma rota"""
        data = {
            "data_hora_chegada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "km_chegada": km_chegada,
            "latitude_chegada": latitude_chegada,
            "longitude_chegada": longitude_chegada,
            "logradouro_chegada": logradouro_chegada
        }
        return self._make_request("PUT", f"/api/routes/{route_id}", data)
    
    def geocode_departure(self, route_id: int, latitude: float, longitude: float) -> Dict[str, Any]:
        """Obtém endereço a partir das coordenadas de saída"""
        return self._make_request("POST", f"/api/routes/{route_id}/geocode-saida", {
            "latitude": latitude,
            "longitude": longitude
        })
    
    def geocode_arrival(self, route_id: int, latitude: float, longitude: float) -> Dict[str, Any]:
        """Obtém endereço a partir das coordenadas de chegada"""
        return self._make_request("POST", f"/api/routes/{route_id}/geocode-chegada", {
            "latitude": latitude,
            "longitude": longitude
        })
    
    # Verificação de conectividade
    def check_connection(self) -> bool:
        """Verifica se a API está acessível"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    # Métodos administrativos adicionais
    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo usuário (admin only)"""
        return self._make_request("POST", "/api/users/register", data)
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Exclui um usuário (admin only)"""
        return self._make_request("DELETE", f"/api/users/{user_id}")
    
    def delete_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        """Exclui um veículo (admin only)"""
        return self._make_request("DELETE", f"/api/vehicles/{vehicle_id}")
    
    def get_usage_records(self) -> List[Dict[str, Any]]:
        """Lista todos os registros de utilização"""
        return self._make_request("GET", "/api/usage-control/")
    
    def create_usage_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo registro de utilização"""
        return self._make_request("POST", "/api/usage-control/", data)
    
    def get_usage_controls(self) -> List[Dict[str, Any]]:
        """Lista todos os controles de utilização"""
        return self._make_request("GET", "/api/usage/")
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Lista todas as rotas"""
        return self._make_request("GET", "/api/routes/")
    
    def upload_avatar(self, user_id: int, file_path: str) -> Dict[str, Any]:
        """Faz upload do avatar do usuário"""
        import os
        from pathlib import Path
        
        print(f"[DEBUG] upload_avatar chamado - user_id: {user_id}, file_path: {file_path}")
        
        # Verificar se file_path não é None
        if file_path is None:
            print("[DEBUG] file_path é None")
            return {"success": False, "message": "Caminho do arquivo não fornecido"}
        
        if not os.path.exists(file_path):
            print(f"[DEBUG] Arquivo não encontrado: {file_path}")
            return {"success": False, "message": "Arquivo não encontrado"}
        
        # Verificar se é uma imagem válida
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        file_extension = Path(file_path).suffix.lower()
        print(f"[DEBUG] Extensão do arquivo: {file_extension}")
        if file_extension not in valid_extensions:
            print(f"[DEBUG] Extensão inválida: {file_extension}")
            return {"success": False, "message": "Formato de arquivo não suportado"}
        
        try:
            url = f"{self.base_url}/api/users/{user_id}/avatar"
            print(f"[DEBUG] URL do upload: {url}")
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
                print("[DEBUG] Token de autorização adicionado")
            else:
                print("[DEBUG] AVISO: Nenhum token de autorização")
            
            print(f"[DEBUG] Abrindo arquivo: {file_path}")
            
            # Determinar Content-Type correto baseado na extensão
            content_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp'
            }
            content_type = content_type_map.get(file_extension, 'image/png')
            print(f"[DEBUG] Content-Type definido: {content_type}")
            
            with open(file_path, 'rb') as file:
                files = {'avatar': (os.path.basename(file_path), file, content_type)}
                print(f"[DEBUG] Fazendo requisição POST para {url}")
                response = requests.post(url, headers=headers, files=files)
            
            print(f"[DEBUG] Status da resposta: {response.status_code}")
            print(f"[DEBUG] Headers da resposta: {response.headers}")
            
            response.raise_for_status()
            result = response.json()
            print(f"[DEBUG] Resposta JSON: {result}")
            
            # Verificar se é a estrutura esperada do backend
            if isinstance(result, dict) and result.get('success'):
                print(f"[DEBUG] Upload bem sucedido - dados: {result.get('data')}")
                return {"success": True, "data": result.get('data')}
            else:
                print(f"[DEBUG] Resposta inesperada: {result}")
                return {"success": True, "data": result}
            
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Erro na requisição: {e}")
            print(f"[DEBUG] Tipo do erro: {type(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[DEBUG] Status da resposta de erro: {e.response.status_code}")
                print(f"[DEBUG] Texto da resposta de erro: {e.response.text}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            print(f"[DEBUG] Erro inesperado: {e}")
            print(f"[DEBUG] Tipo do erro: {type(e)}")
            return {"success": False, "message": str(e)}
    
    def delete_avatar(self, user_id: int) -> Dict[str, Any]:
        """Remove o avatar do usuário"""
        try:
            url = f"{self.base_url}/api/users/{user_id}/avatar"
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            return {"success": True, "data": result}
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao deletar avatar: {e}")
            return {"success": False, "message": str(e)}
