import flet as ft
from .api_client import SGUVApiClient
from .views.login_view import LoginView
from .views.driver_dashboard_view import DriverDashboardView
from .views.admin_dashboard_view import AdminDashboardView

class SGUVApp:
    def __init__(self):
        self.api_client = SGUVApiClient()
        self.current_user = None
        
    def main(self, page: ft.Page):
        """Função principal do aplicativo"""
        self.page = page
        
        # Configurações da página
        page.title = "SGUV - Sistema de Gerenciamento de Utilização de Veículos"
        page.window_width = 400
        page.window_height = 600
        page.window_resizable = True
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        
        # Mostrar tela de login diretamente (removendo verificação de conexão que estava falhando)
        self.show_login()
    
    def show_connection_error(self):
        """Mostra erro de conexão com a API"""
        error_view = ft.Column([
            ft.Icon(ft.icons.ERROR, size=64, color=ft.colors.RED),
            ft.Text("Erro de Conexão", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Não foi possível conectar com o servidor.\nVerifique se a API está rodando em http://127.0.0.1:8000",
                text_align=ft.TextAlign.CENTER
            ),
            ft.ElevatedButton(
                text="Tentar Novamente",
                on_click=lambda e: self.retry_connection(),
                style=ft.ButtonStyle(bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
            )
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True)
        
        self.page.add(error_view)
        self.page.update()
    
    def retry_connection(self):
        """Tenta reconectar com a API"""
        if self.api_client.check_connection():
            self.page.clean()
            self.show_login()
        else:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Ainda não foi possível conectar. Verifique se a API está rodando."),
                    bgcolor=ft.colors.RED
                )
            )
    
    def show_login(self):
        """Mostra a tela de login"""
        self.page.clean()
        login_view = LoginView(self.page, self.api_client, self.on_login_success)
        self.page.add(login_view.build())
        self.page.update()
    
    def on_login_success(self, user_data):
        """Callback executado quando login é bem-sucedido"""
        self.current_user = user_data
        
        # Armazenar dados do usuário atual
        self.current_user = user_data
        
        # Redirecionar baseado no perfil
        if user_data['perfil'] == 'motorista':
            self.show_driver_dashboard()
        elif user_data['perfil'] in ['admin', 'gestor', 'operador']:
            self.show_admin_dashboard(user_data)
        else:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Perfil de usuário não reconhecido"),
                    bgcolor=ft.colors.RED
                )
            )
    
    def show_driver_dashboard(self):
        """Mostra o dashboard do motorista"""
        self.page.clean()
        
        # Ajustar tamanho da janela para o dashboard
        self.page.window_width = 800
        self.page.window_height = 700
        
        driver_view = DriverDashboardView(self.page, self.api_client, self.current_user)
        self.page.add(driver_view.build())
        self.page.update()
    
    def show_admin_dashboard(self, user_data):
        """Mostra o dashboard administrativo"""
        print(f"[DEBUG] show_admin_dashboard chamado com: {user_data}")
        self.page.clean()
        
        # Configurar página para dashboard admin
        self.page.title = "SGUV - Dashboard Administrativo"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_resizable = True
        self.page.padding = 0  # Remove padding para layout completo
        
        try:
            # Criar view administrativa com callback de logout
            print("[DEBUG] Criando AdminDashboardView...")
            admin_view = AdminDashboardView(self.page, self.api_client, user_data, self.show_login)
            view_content = admin_view.get_view()
            print("[DEBUG] Adicionando view à página...")
            self.page.add(view_content)
            print("[DEBUG] Atualizando página...")
            self.page.update()
            print("[DEBUG] Dashboard administrativo carregado com sucesso!")
        except Exception as e:
            print(f"[DEBUG] ERRO no show_admin_dashboard: {e}")
            import traceback
            traceback.print_exc()
            self.page.add(ft.Text(f"ERRO: {str(e)}", color=ft.colors.RED))
            self.page.update()
    
    def handle_logout(self, e):
        """Processa logout do usuário"""
        self.api_client.logout()
        self.current_user = None
        
        # Voltar ao tamanho original da janela
        self.page.window_width = 400
        self.page.window_height = 600
        
        self.show_login()

def main(page: ft.Page):
    """Função principal para execução do Flet"""
    app = SGUVApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
