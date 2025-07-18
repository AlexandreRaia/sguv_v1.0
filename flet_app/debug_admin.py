import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import SGUVApiClient
from datetime import datetime

class DebugAdminDashboardView:
    def __init__(self, page: ft.Page, api_client: SGUVApiClient, user_data: dict, on_logout_callback=None):
        self.page = page
        self.api_client = api_client
        self.user_data = user_data
        self.on_logout_callback = on_logout_callback
        
        print(f"[DEBUG] Inicializando AdminDashboardView")
        print(f"[DEBUG] User data: {user_data}")
        
    def get_view(self):
        """Retorna uma view de teste simples"""
        try:
            print("[DEBUG] Criando view de teste...")
            
            # Teste com container simples
            test_content = ft.Container(
                content=ft.Column([
                    ft.Text("🎉 DASHBOARD FUNCIONANDO!", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN),
                    ft.Text(f"Usuário: {self.user_data.get('nome', 'N/A')}", size=16),
                    ft.Text(f"Email: {self.user_data.get('email', 'N/A')}", size=14),
                    ft.Text(f"Perfil: {self.user_data.get('perfil', 'N/A')}", size=14),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Voltar ao Login",
                        bgcolor=ft.colors.RED,
                        color=ft.colors.WHITE,
                        on_click=lambda e: self.logout(e)
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.BLUE_50,
                border_radius=10,
                expand=True
            )
            
            print("[DEBUG] View criada com sucesso!")
            return test_content
            
        except Exception as e:
            print(f"[DEBUG] ERRO ao criar view: {e}")
            import traceback
            traceback.print_exc()
            return ft.Container(
                content=ft.Text(f"ERRO: {str(e)}", color=ft.colors.RED, size=20),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.RED_50
            )
    
    def logout(self, e):
        """Faz logout do sistema"""
        try:
            print("[DEBUG] Fazendo logout...")
            self.api_client.logout()
            if self.on_logout_callback:
                self.on_logout_callback()
        except Exception as error:
            print(f"[DEBUG] Erro no logout: {error}")
