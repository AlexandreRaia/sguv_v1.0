import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import SGUVApiClient

class LoginView:
    def __init__(self, page: ft.Page, api_client: SGUVApiClient, on_login_success):
        self.page = page
        self.api_client = api_client
        self.on_login_success = on_login_success
        
        # Campos de entrada
        self.email_field = ft.TextField(
            label="Email",
            width=300,
            prefix_icon=ft.icons.EMAIL,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Senha",
            width=300,
            prefix_icon=ft.icons.LOCK,
            password=True,
            can_reveal_password=True
        )
        
        # Botões
        self.login_button = ft.ElevatedButton(
            text="Entrar",
            width=300,
            on_click=self.handle_login,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE
            )
        )
        
        self.register_button = ft.TextButton(
            text="Não tem conta? Cadastre-se",
            on_click=self.show_register_form
        )
        
        # Mensagem de erro
        self.error_message = ft.Text(
            color=ft.colors.RED,
            visible=False
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Container de registro
        self.register_container = ft.Container(visible=False)
        self.create_register_form()
    
    def create_register_form(self):
        """Cria o formulário de registro"""
        self.reg_matricula = ft.TextField(label="Matrícula", width=300)
        self.reg_nome = ft.TextField(label="Nome Completo", width=300)
        self.reg_email = ft.TextField(label="Email", width=300)
        self.reg_celular = ft.TextField(label="Celular", width=300)
        self.reg_unidade = ft.TextField(label="Unidade", width=300)
        self.reg_senha = ft.TextField(label="Senha", password=True, width=300)
        self.reg_confirm_senha = ft.TextField(label="Confirmar Senha", password=True, width=300)
        
        self.register_submit_button = ft.ElevatedButton(
            text="Cadastrar",
            width=300,
            on_click=self.handle_register,
            style=ft.ButtonStyle(bgcolor=ft.colors.GREEN, color=ft.colors.WHITE)
        )
        
        self.back_to_login_button = ft.TextButton(
            text="Voltar para Login",
            on_click=self.show_login_form
        )
        
        self.register_error = ft.Text(color=ft.colors.RED, visible=False)
        
        self.register_container.content = ft.Column([
            ft.Text("Cadastro de Usuário", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.reg_matricula,
            self.reg_nome,
            self.reg_email,
            self.reg_celular,
            self.reg_unidade,
            self.reg_senha,
            self.reg_confirm_senha,
            self.register_error,
            self.register_submit_button,
            self.back_to_login_button
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def build(self):
        """Constrói a interface de login"""
        login_form = ft.Column([
            ft.Text("SGUV - Sistema de Gerenciamento de Utilização de Veículos", 
                   size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Divider(),
            ft.Text("Login", size=24, weight=ft.FontWeight.BOLD),
            self.email_field,
            self.password_field,
            self.error_message,
            self.loading,
            self.login_button,
            self.register_button
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        return ft.Container(
            content=ft.Stack([
                ft.Container(
                    content=login_form,
                    visible=True
                ),
                self.register_container
            ]),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def show_error(self, message: str):
        """Mostra mensagem de erro"""
        self.error_message.value = message
        self.error_message.visible = True
        self.page.update()
    
    def show_register_error(self, message: str):
        """Mostra mensagem de erro no registro"""
        self.register_error.value = message
        self.register_error.visible = True
        self.page.update()
    
    def clear_errors(self):
        """Limpa mensagens de erro"""
        self.error_message.visible = False
        self.register_error.visible = False
        self.page.update()
    
    def show_loading(self, show: bool):
        """Mostra/oculta loading"""
        self.loading.visible = show
        self.login_button.disabled = show
        self.page.update()
    
    def show_register_form(self, e):
        """Mostra formulário de registro"""
        self.clear_errors()
        self.register_container.visible = True
        self.page.controls[0].content.controls[0].visible = False
        self.page.update()
    
    def show_login_form(self, e):
        """Mostra formulário de login"""
        self.clear_errors()
        self.register_container.visible = False
        self.page.controls[0].content.controls[0].visible = True
        self.page.update()
    
    def handle_login(self, e):
        """Processa login do usuário"""
        self.clear_errors()
        
        if not self.email_field.value or not self.password_field.value:
            self.show_error("Por favor, preencha todos os campos")
            return
            
        self.show_loading(True)
        
        try:
            success = self.api_client.login(self.email_field.value, self.password_field.value)
            if success:
                self.on_login_success(self.api_client.current_user)
            else:
                self.show_error("Email ou senha incorretos")
        except Exception as ex:
            self.show_error(f"Erro ao fazer login: {str(ex)}")
        finally:
            self.show_loading(False)
    
    def handle_register(self, e):
        """Processa registro do usuário"""
        self.clear_errors()
        
        # Validações
        if not all([
            self.reg_matricula.value,
            self.reg_nome.value,
            self.reg_email.value,
            self.reg_senha.value,
            self.reg_confirm_senha.value
        ]):
            self.show_register_error("Por favor, preencha todos os campos obrigatórios")
            return
        
        if self.reg_senha.value != self.reg_confirm_senha.value:
            self.show_register_error("As senhas não coincidem")
            return
        
        if len(self.reg_senha.value) < 6:
            self.show_register_error("A senha deve ter pelo menos 6 caracteres")
            return
        
        try:
            result = self.api_client.register(
                matricula=self.reg_matricula.value,
                nome=self.reg_nome.value,
                email=self.reg_email.value,
                senha=self.reg_senha.value,
                celular=self.reg_celular.value or "",
                unidade=self.reg_unidade.value or ""
            )
            
            # Mostrar mensagem de sucesso e voltar para login
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Cadastro realizado com sucesso! Aguarde aprovação do administrador."),
                    bgcolor=ft.colors.GREEN
                )
            )
            self.show_login_form(None)
            
        except Exception as ex:
            self.show_register_error(f"Erro ao cadastrar: {str(ex)}")
