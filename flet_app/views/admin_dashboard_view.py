import flet as ft
import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import SGUVApiClient
from datetime import datetime
from typing import Dict, Any, List

class AdminDashboardView:
    def __init__(self, page: ft.Page, api_client: SGUVApiClient, user_data: dict, on_logout_callback=None):
        self.page = page
        self.api_client = api_client
        self.user_data = user_data
        self.on_logout_callback = on_logout_callback
        
        # Estado da aplicação
        self.current_view = "dashboard"
        self.users_data = []
        self.vehicles_data = []
        self.usage_data = []
        
        # Estado do menu lateral (True = expandido, False = retraído)
        self.sidebar_expanded = True
        
        # Componentes principais
        self.main_container = ft.Container()
        self.content_area = ft.Container(expand=True)
        self.sidebar = None  # Será criado após carregar dados
        
        # Inicializar dados primeiro
        self.load_initial_data()
        
        # Criar sidebar após ter dados carregados
        self.sidebar = self.create_sidebar()
        
        # Criar sidebar após carregar dados
        self.sidebar = self.create_sidebar()
    
    def load_initial_data(self):
        """Carrega dados iniciais do sistema"""
        try:
            print("Carregando dados iniciais...")
            
            # Inicializar com dados vazios para evitar erros
            self.users_data = []
            self.vehicles_data = []
            self.usage_data = []
            
            # Tentar carregar usuários
            try:
                users_response = self.api_client.get_users()
                if users_response and users_response.get('success'):
                    self.users_data = users_response.get('data', [])
                    print(f"Usuários carregados: {len(self.users_data)}")
                else:
                    print("Erro ao carregar usuários, usando dados mock")
                    self.users_data = [{"nome": "Admin", "email": "admin@sguv.com", "perfil": "admin", "status": "ativo"}]
            except Exception as e:
                print(f"Erro ao carregar usuários: {e}")
                self.users_data = [{"nome": "Admin", "email": "admin@sguv.com", "perfil": "admin", "status": "ativo"}]
            
            # Tentar carregar veículos
            try:
                vehicles_response = self.api_client.get_vehicles()
                if vehicles_response and vehicles_response.get('success'):
                    self.vehicles_data = vehicles_response.get('data', [])
                    print(f"Veículos carregados: {len(self.vehicles_data)}")
                else:
                    print("Erro ao carregar veículos")
                    self.vehicles_data = []
            except Exception as e:
                print(f"Erro ao carregar veículos: {e}")
                self.vehicles_data = []
            
            # Tentar carregar dados de utilização
            try:
                usage_response = self.api_client.get_usage_records()
                if usage_response and usage_response.get('success'):
                    self.usage_data = usage_response.get('data', [])
                    print(f"Registros de uso carregados: {len(self.usage_data)}")
                else:
                    print("Erro ao carregar registros de uso")
                    self.usage_data = []
            except Exception as e:
                print(f"Erro ao carregar registros de uso: {e}")
                self.usage_data = []
                
            print("Dados carregados com sucesso!")
                
        except Exception as e:
            print(f"Erro geral ao carregar dados iniciais: {e}")
            self.users_data = [{"nome": "Admin", "email": "admin@sguv.com", "perfil": "admin", "status": "ativo"}]
            self.vehicles_data = []
            self.usage_data = []
    
    def create_sidebar(self):
        """Cria a barra lateral de navegação extensível"""
        print("[DEBUG] === CRIANDO SIDEBAR ===")
        
        # Largura dinâmica baseada no estado
        sidebar_width = 250 if self.sidebar_expanded else 70
        print(f"[DEBUG] Largura do sidebar: {sidebar_width}")
        
        # Botão para expandir/retrair
        toggle_button = ft.IconButton(
            icon=ft.icons.MENU_OPEN if self.sidebar_expanded else ft.icons.MENU,
            icon_color=ft.colors.BLUE_800,
            icon_size=24,
            on_click=self.toggle_sidebar,
            tooltip="Expandir/Retrair Menu"
        )
        
        # Menu de navegação - criação direta e simples
        print("[DEBUG] Criando itens do menu de forma direta...")
        
        if self.sidebar_expanded:
            menu_items = [
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.DASHBOARD, size=18, color=ft.colors.BLUE_800),
                        ft.Text("Dashboard", size=13, color=ft.colors.BLUE_800)
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "dashboard" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("dashboard"),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.PEOPLE, size=18, color=ft.colors.BLACK),
                        ft.Text("Usuários", size=13, color=ft.colors.BLACK)
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "users" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("users"),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.DIRECTIONS_CAR, size=18, color=ft.colors.BLACK),
                        ft.Text("Veículos", size=13, color=ft.colors.BLACK)
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "vehicles" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("vehicles"),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.ASSIGNMENT, size=18, color=ft.colors.BLACK),
                        ft.Text("Controle de Uso", size=13, color=ft.colors.BLACK)
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "usage" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("usage"),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.MAP, size=18, color=ft.colors.BLACK),
                        ft.Text("Rotas", size=13, color=ft.colors.BLACK)
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "routes" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("routes"),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.BAR_CHART, size=18, color=ft.colors.BLACK),
                        ft.Text("Relatórios", size=13, color=ft.colors.BLACK)
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "reports" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("reports"),
                ),
            ]
        else:
            menu_items = [
                ft.Container(
                    content=ft.Icon(ft.icons.DASHBOARD, size=18, color=ft.colors.BLUE_800),
                    padding=ft.padding.all(10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "dashboard" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("dashboard"),
                    tooltip="Dashboard"
                ),
                ft.Container(
                    content=ft.Icon(ft.icons.PEOPLE, size=18, color=ft.colors.BLACK),
                    padding=ft.padding.all(10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "users" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("users"),
                    tooltip="Usuários"
                ),
                ft.Container(
                    content=ft.Icon(ft.icons.DIRECTIONS_CAR, size=18, color=ft.colors.BLACK),
                    padding=ft.padding.all(10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "vehicles" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("vehicles"),
                    tooltip="Veículos"
                ),
                ft.Container(
                    content=ft.Icon(ft.icons.ASSIGNMENT, size=18, color=ft.colors.BLACK),
                    padding=ft.padding.all(10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "usage" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("usage"),
                    tooltip="Controle de Uso"
                ),
                ft.Container(
                    content=ft.Icon(ft.icons.MAP, size=18, color=ft.colors.BLACK),
                    padding=ft.padding.all(10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "routes" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("routes"),
                    tooltip="Rotas"
                ),
                ft.Container(
                    content=ft.Icon(ft.icons.BAR_CHART, size=18, color=ft.colors.BLACK),
                    padding=ft.padding.all(10),
                    bgcolor=ft.colors.BLUE_100 if self.current_view == "reports" else ft.colors.TRANSPARENT,
                    border_radius=8,
                    on_click=lambda e: self.change_view("reports"),
                    tooltip="Relatórios"
                ),
            ]
        
        print(f"[DEBUG] Criados {len(menu_items)} itens de menu")
        
        # Estrutura simplificada do sidebar
        sidebar_content = []
        
        # Botão toggle
        sidebar_content.append(ft.Container(
            content=toggle_button,
            alignment=ft.alignment.center,
            padding=ft.padding.all(5)
        ))
        
        # Divisor
        sidebar_content.append(ft.Divider(height=1))
        
        # Header do usuário (centralizado com upload de avatar)
        if self.sidebar_expanded:
            avatar_content = self.create_avatar_section(expanded=True)
            sidebar_content.append(ft.Container(
                content=avatar_content,
                alignment=ft.alignment.center,
                padding=ft.padding.all(10)
            ))
        else:
            avatar_content = self.create_avatar_section(expanded=False)
            sidebar_content.append(ft.Container(
                content=avatar_content,
                alignment=ft.alignment.center,
                padding=ft.padding.all(8)
            ))
        
        # Divisor
        sidebar_content.append(ft.Divider(height=1))
        
        # Adicionar itens do menu
        for item in menu_items:
            sidebar_content.append(item)
        
        # Divisor
        sidebar_content.append(ft.Divider(height=1))
        
        # Botão de logout
        if self.sidebar_expanded:
            logout_btn = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.icons.LOGOUT, color=ft.colors.RED, size=16),
                    ft.Text("Sair", color=ft.colors.RED, size=12)
                ], spacing=5),
                bgcolor=ft.colors.RED_50,
                height=35,
                on_click=self.logout,
            )
        else:
            logout_btn = ft.IconButton(
                icon=ft.icons.LOGOUT,
                icon_color=ft.colors.RED,
                icon_size=18,
                tooltip="Sair",
                on_click=self.logout,
            )
        
        sidebar_content.append(ft.Container(
            content=logout_btn,
            padding=ft.padding.all(5)
        ))
        
        # Container principal do sidebar
        sidebar_container = ft.Container(
            width=sidebar_width,
            bgcolor=ft.colors.BLUE_GREY_50,
            padding=ft.padding.all(8),
            content=ft.Column(
                controls=sidebar_content,
                spacing=5,
                scroll=ft.ScrollMode.AUTO
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
        
        print(f"[DEBUG] Sidebar criado - Largura: {sidebar_width}, Expandido: {self.sidebar_expanded}")
        print(f"[DEBUG] Total de controles no sidebar: {len(sidebar_content)}")
        return sidebar_container
    
    def toggle_sidebar(self, e):
        """Alterna o estado do menu lateral"""
        self.sidebar_expanded = not self.sidebar_expanded
        print(f"[DEBUG] Menu lateral {'expandido' if self.sidebar_expanded else 'retraído'}")
        
        # Recriar o menu lateral com o novo estado
        self.sidebar = self.create_sidebar()
        
        # Atualizar o container principal
        if hasattr(self, 'main_container') and self.main_container.controls:
            self.main_container.controls[0] = self.sidebar
        
        # Atualizar a página
        self.page.update()
    
    def create_avatar_section(self, expanded: bool = True):
        """Cria a seção do avatar com funcionalidade de upload"""
        # Obter dados do usuário atual
        user_name = self.user_data.get('nome', 'Usuário')
        user_initial = user_name[0].upper() if user_name else 'U'
        avatar_link = self.user_data.get('avatar_link')
        
        print(f"[DEBUG] create_avatar_section - avatar_link: {avatar_link}")
        
        # Converter caminho local para URL do servidor se necessário
        avatar_url = None
        if avatar_link:
            if avatar_link.startswith('public/'):
                avatar_url = f"http://127.0.0.1:8000/{avatar_link}"
            elif not avatar_link.startswith('http'):
                avatar_url = f"http://127.0.0.1:8000/public/avatar/{os.path.basename(avatar_link)}"
            else:
                avatar_url = avatar_link
            print(f"[DEBUG] create_avatar_section - avatar_url: {avatar_url}")
        else:
            print("[DEBUG] create_avatar_section - sem avatar_link")
        
        if expanded:
            # Avatar com nome e botão de upload (modo expandido)
            if avatar_url:
                # Mostrar imagem do avatar
                avatar = ft.Container(
                    content=ft.Image(
                        src=avatar_url,
                        width=120,
                        height=120,
                        fit=ft.ImageFit.COVER,
                        border_radius=ft.border_radius.all(60)
                    ),
                    width=120,
                    height=120,
                    border_radius=ft.border_radius.all(60),
                    bgcolor=ft.colors.BLUE,
                    border=ft.border.all(3, ft.colors.WHITE),
                    shadow=ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=8,
                        color=ft.colors.with_opacity(0.4, ft.colors.BLACK),
                        offset=ft.Offset(0, 4)
                    ),
                    on_click=self.show_avatar_options,
                    tooltip="Clique para alterar avatar"
                )
            else:
                # Mostrar avatar padrão com inicial
                avatar = ft.Container(
                    content=ft.CircleAvatar(
                        content=ft.Text(user_initial, size=40, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                        radius=60
                    ),
                    border=ft.border.all(3, ft.colors.WHITE),
                    shadow=ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=8,
                        color=ft.colors.with_opacity(0.4, ft.colors.BLACK),
                        offset=ft.Offset(0, 4)
                    ),
                    on_click=self.show_avatar_options,
                    tooltip="Clique para adicionar avatar"
                )
            
            return ft.Column([
                avatar,
                ft.Container(height=12),
                ft.Text(user_name, size=18, text_align=ft.TextAlign.CENTER, max_lines=2, weight=ft.FontWeight.BOLD),
                ft.Text("Clique no avatar", size=13, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
        else:
            # Avatar compacto (modo retraído)
            if avatar_url:
                return ft.Container(
                    content=ft.Image(
                        src=avatar_url,
                        width=70,
                        height=70,
                        fit=ft.ImageFit.COVER,
                        border_radius=ft.border_radius.all(35)
                    ),
                    width=70,
                    height=70,
                    border_radius=ft.border_radius.all(35),
                    bgcolor=ft.colors.BLUE,
                    border=ft.border.all(2, ft.colors.WHITE),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=6,
                        color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                        offset=ft.Offset(0, 2)
                    ),
                    on_click=self.show_avatar_options,
                    tooltip=f"Avatar de {user_name} - Clique para alterar"
                )
            else:
                return ft.Container(
                    content=ft.CircleAvatar(
                        content=ft.Text(user_initial, size=28),
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                        radius=35
                    ),
                    border=ft.border.all(2, ft.colors.WHITE),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=6,
                        color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                        offset=ft.Offset(0, 2)
                    ),
                    on_click=self.show_avatar_options,
                    tooltip=f"Avatar de {user_name} - Clique para adicionar"
                )
    
    def show_avatar_options(self, e):
        """Mostra opções de avatar (upload/remover)"""
        avatar_link = self.user_data.get('avatar_link')
        
        # Botões de ação
        upload_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.UPLOAD_FILE),
                ft.Text("Fazer Upload")
            ], spacing=5),
            on_click=self.upload_avatar,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        remove_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.DELETE),
                ft.Text("Remover Avatar")
            ], spacing=5),
            on_click=self.remove_avatar,
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            disabled=not avatar_link
        )
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Opções de Avatar"),
            content=ft.Column([
                ft.Text("Escolha uma ação para seu avatar:"),
                ft.Container(height=10),
                upload_btn,
                ft.Container(height=5),
                remove_btn
            ], spacing=5, height=150),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def upload_avatar(self, e):
        """Inicia o processo de upload de avatar"""
        print("[DEBUG] upload_avatar chamado")
        # Fechar dialog de opções
        self.page.dialog.open = False
        self.page.update()
        
        # Criar campo para inserir caminho do arquivo
        file_path_field = ft.TextField(
            label="Caminho completo para o arquivo de imagem",
            hint_text="Ex: /home/usuario/imagem.png ou C:\\Usuarios\\imagem.png",
            width=500,
            value="/home/alexandre/Documentos/Projetos/sguv/001.png"  # Valor padrão para teste
        )
        
        def upload_from_path(e):
            file_path = file_path_field.value
            print(f"[DEBUG] upload_from_path chamado com: '{file_path}'")
            print(f"[DEBUG] Tipo do file_path: {type(file_path)}")
            if file_path:
                self.process_avatar_upload(file_path)
            else:
                print("[DEBUG] file_path está vazio!")
            self.page.dialog.open = False
            self.page.update()
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        def browse_file(e):
            print("[DEBUG] browse_file chamado")
            # Criar file picker
            def on_result(e: ft.FilePickerResultEvent):
                print(f"[DEBUG] file picker callback - e: {e}")
                print(f"[DEBUG] file picker callback - e.files: {e.files}")
                if e.files and len(e.files) > 0:
                    file_info = e.files[0]
                    print(f"[DEBUG] file info: {file_info}")
                    print(f"[DEBUG] file info.path: {file_info.path}")
                    print(f"[DEBUG] file info.name: {file_info.name}")
                    
                    file_path = file_info.path
                    if file_path is None:
                        print("[DEBUG] file_path é None, tentando construir caminho baseado no nome")
                        # Tentar construir caminho baseado no nome do arquivo
                        import os
                        filename = file_info.name
                        
                        # Possíveis localizações
                        possible_paths = [
                            f"/home/alexandre/Documentos/Projetos/sguv/{filename}",  # Raiz do projeto
                            f"/home/alexandre/{filename}",  # Home do usuário
                            f"/home/alexandre/Downloads/{filename}",  # Downloads
                            f"/home/alexandre/Desktop/{filename}",  # Desktop
                            filename  # Caminho atual
                        ]
                        
                        for path in possible_paths:
                            if os.path.exists(path):
                                file_path = path
                                print(f"[DEBUG] Arquivo encontrado em: {file_path}")
                                break
                        else:
                            file_path = f"/home/alexandre/Documentos/Projetos/sguv/{filename}"
                            print(f"[DEBUG] Nenhum arquivo encontrado, usando caminho padrão: {file_path}")
                    
                    if file_path:
                        file_path_field.value = file_path
                        file_path_field.update()
                        print(f"[DEBUG] Campo atualizado com: {file_path}")
                    else:
                        print("[DEBUG] file_path ainda é None após todas as tentativas")
                else:
                    print("[DEBUG] file picker - nenhum arquivo selecionado ou lista vazia")
            
            print("[DEBUG] Criando file picker")
            file_picker = ft.FilePicker(on_result=on_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            print("[DEBUG] Abrindo file picker")
            # Abrir file picker
            file_picker.pick_files(
                dialog_title="Selecionar Avatar",
                file_type=ft.FilePickerFileType.IMAGE,
                allow_multiple=False
            )
        
        # Dialog com campo de texto e instruções
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Upload de Avatar"),
            content=ft.Column([
                ft.Text("⚠️ IMPORTANTE: Use o caminho já preenchido ou digite o caminho COMPLETO:"),
                ft.Text("• Linux/Mac: /home/usuario/imagem.png", size=12, color=ft.colors.GREY_700),
                ft.Text("• Windows: C:\\Users\\usuario\\imagem.png", size=12, color=ft.colors.GREY_700),
                ft.Container(height=10),
                file_path_field,
                ft.Container(height=10),
                ft.Text("✅ TESTE: Clique em 'Fazer Upload' para testar com o arquivo 001.png", 
                       size=12, color=ft.colors.GREEN),
                ft.Row([
                    ft.ElevatedButton(
                        "Procurar Arquivo (limitado na web)",
                        on_click=browse_file,
                        bgcolor=ft.colors.BLUE_50
                    )
                ])
            ], height=300),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Fazer Upload", on_click=upload_from_path, bgcolor=ft.colors.GREEN)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def process_avatar_upload(self, file_path: str):
        """Processa o upload do avatar"""
        try:
            print(f"[DEBUG] process_avatar_upload chamado com file_path: '{file_path}'")
            print(f"[DEBUG] user_data: {self.user_data}")
            
            # Validar se o file_path não é None
            if not file_path:
                print("[DEBUG] file_path é None ou vazio")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Nenhum arquivo selecionado"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Limpar espaços em branco
            file_path = file_path.strip()
            print(f"[DEBUG] file_path após strip: '{file_path}'")
            
            # Verificar se o arquivo existe
            import os
            file_exists = os.path.exists(file_path)
            print(f"[DEBUG] os.path.exists('{file_path}'): {file_exists}")
            
            if not file_exists:
                # Tentar alguns caminhos alternativos
                print(f"[DEBUG] Arquivo não encontrado, tentando caminhos alternativos...")
                
                alternative_paths = []
                filename = os.path.basename(file_path)
                
                # Se é apenas um nome de arquivo, tentar em locais comuns
                if file_path == filename:
                    alternative_paths = [
                        f"/home/alexandre/Documentos/Projetos/sguv/{filename}",  # Raiz do projeto
                        f"/home/alexandre/{filename}",  # Home do usuário
                        f"/home/alexandre/Downloads/{filename}",  # Downloads
                        f"/home/alexandre/Desktop/{filename}",  # Desktop
                        os.path.abspath(filename)  # Diretório atual
                    ]
                else:
                    # Se é um caminho, tentar variações
                    if not os.path.isabs(file_path):
                        alternative_paths.append(os.path.abspath(file_path))
                    
                    # Tentar no diretório atual
                    current_dir = os.getcwd()
                    alternative_paths.append(os.path.join(current_dir, filename))
                    
                    # Tentar na raiz do projeto
                    alternative_paths.append(f"/home/alexandre/Documentos/Projetos/sguv/{filename}")
                
                print(f"[DEBUG] Tentando caminhos alternativos: {alternative_paths}")
                
                for alt_path in alternative_paths:
                    print(f"[DEBUG] Verificando: {alt_path}")
                    if os.path.exists(alt_path):
                        file_path = alt_path
                        file_exists = True
                        print(f"[DEBUG] Arquivo encontrado em: {file_path}")
                        break
                
                if not file_exists:
                    print(f"[DEBUG] Arquivo definitivamente não encontrado")
                    print(f"[DEBUG] Diretório atual: {os.getcwd()}")
                    print(f"[DEBUG] Listando diretório atual:")
                    try:
                        files = os.listdir('.')
                        for f in files[:10]:  # Primeiros 10 arquivos
                            print(f"[DEBUG]   - {f}")
                    except Exception as e:
                        print(f"[DEBUG] Erro ao listar diretório: {e}")
                        
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Arquivo não encontrado: {os.path.basename(file_path)}"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
            
            print(f"[DEBUG] Arquivo encontrado! Caminho final: '{file_path}'")
            
            # Verificar tamanho do arquivo
            try:
                file_size = os.path.getsize(file_path)
                print(f"[DEBUG] Tamanho do arquivo: {file_size} bytes")
            except Exception as e:
                print(f"[DEBUG] Erro ao obter tamanho do arquivo: {e}")
            
            # Fazer upload via API
            user_id = self.user_data.get('id')
            print(f"[DEBUG] Fazendo upload para user_id: {user_id}")
            response = self.api_client.upload_avatar(user_id, file_path)
            print(f"[DEBUG] Resposta da API: {response}")
            
            if response.get('success'):
                print("[DEBUG] Upload bem sucedido")
                # Verificar se a resposta tem os dados esperados
                response_data = response.get('data', {})
                print(f"[DEBUG] Dados da resposta: {response_data}")
                
                # Extrair avatar_link da resposta
                if isinstance(response_data, dict):
                    avatar_link = response_data.get('avatar_link')
                    if not avatar_link and 'data' in response_data:
                        # Caso esteja aninhado em outro 'data'
                        avatar_link = response_data['data'].get('avatar_link')
                else:
                    avatar_link = None
                
                print(f"[DEBUG] Avatar link extraído: {avatar_link}")
                
                if avatar_link:
                    # Atualizar dados do usuário localmente
                    self.user_data['avatar_link'] = avatar_link
                    print(f"[DEBUG] Avatar link atualizado localmente: {self.user_data['avatar_link']}")
                    
                    # Recarregar dados do usuário do servidor para garantir sincronização
                    try:
                        user_response = self.api_client.get_current_user()
                        if user_response and user_response.get('success'):
                            server_user_data = user_response.get('data', {})
                            if server_user_data.get('avatar_link'):
                                self.user_data['avatar_link'] = server_user_data['avatar_link']
                                print(f"[DEBUG] Avatar link atualizado do servidor: {self.user_data['avatar_link']}")
                    except Exception as e:
                        print(f"[DEBUG] Erro ao recarregar dados do usuário: {e}")
                    
                    # Recarregar dados iniciais para atualizar a lista de usuários
                    print("[DEBUG] Recarregando dados iniciais para atualizar lista de usuários...")
                    self.load_initial_data()
                    
                    # Recriar sidebar para refletir mudanças
                    self.sidebar = self.create_sidebar()
                    self.main_container.controls[0] = self.sidebar
                    
                    # Atualizar conteúdo se estivermos na view de usuários
                    if self.current_view == "users":
                        print("[DEBUG] Atualizando view de usuários...")
                        self.update_content()
                    
                    # Mostrar mensagem de sucesso
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Avatar atualizado com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                    self.page.snack_bar.open = True
                else:
                    print("[DEBUG] ERRO: Avatar link não encontrado na resposta")
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Erro: Link do avatar não retornado pelo servidor"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
            else:
                print(f"[DEBUG] Upload falhou: {response}")
                # Mostrar erro
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao fazer upload: {response.get('message', 'Erro desconhecido')}"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
                
        except Exception as error:
            print(f"[DEBUG] Exceção capturada: {str(error)}")
            print(f"[DEBUG] Tipo da exceção: {type(error)}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erro ao processar upload: {str(error)}"),
                bgcolor=ft.colors.RED
            )
            self.page.snack_bar.open = True
        
        self.page.update()
    
    def remove_avatar(self, e):
        """Remove o avatar do usuário"""
        # Fechar dialog de opções
        self.page.dialog.open = False
        self.page.update()
        
        def confirm_remove(e):
            try:
                user_id = self.user_data.get('id')
                response = self.api_client.delete_avatar(user_id)
                
                if response.get('success'):
                    # Atualizar dados do usuário
                    self.user_data['avatar_link'] = None
                    
                    # Recarregar dados iniciais para atualizar a lista de usuários
                    print("[DEBUG] Recarregando dados iniciais após remoção do avatar...")
                    self.load_initial_data()
                    
                    # Recriar sidebar
                    self.sidebar = self.create_sidebar()
                    self.main_container.controls[0] = self.sidebar
                    
                    # Atualizar conteúdo se estivermos na view de usuários
                    if self.current_view == "users":
                        print("[DEBUG] Atualizando view de usuários após remoção...")
                        self.update_content()
                    
                    # Mostrar mensagem de sucesso
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Avatar removido com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                    self.page.snack_bar.open = True
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Erro ao remover avatar: {response.get('message', 'Erro desconhecido')}"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
                    
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao remover avatar: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
            
            # Fechar dialog de confirmação
            self.page.dialog.open = False
            self.page.update()
        
        def close_confirm_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Dialog de confirmação
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Remoção"),
            content=ft.Text("Tem certeza que deseja remover seu avatar?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_confirm_dialog),
                ft.ElevatedButton(
                    "Remover",
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE,
                    on_click=confirm_remove
                )
            ]
        )
        
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()
    
    def create_menu_item(self, icon, title: str, view_id: str):
        """Cria um item do menu lateral"""
        print(f"[DEBUG] Criando item do menu: {title} (view: {view_id})")
        is_active = self.current_view == view_id
        
        # Cores baseadas no estado ativo
        bg_color = ft.colors.BLUE_100 if is_active else ft.colors.TRANSPARENT
        icon_color = ft.colors.BLUE_800 if is_active else ft.colors.BLACK
        text_color = ft.colors.BLUE_800 if is_active else ft.colors.BLACK
        text_weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL
        
        if self.sidebar_expanded:
            # Menu expandido - mostrar ícone e texto
            content = ft.Row([
                ft.Icon(icon, size=18, color=icon_color),
                ft.Text(title, size=13, weight=text_weight, color=text_color)
            ], spacing=10)
            padding = ft.padding.symmetric(horizontal=15, vertical=10)
            print(f"[DEBUG] Item {title} criado no modo expandido")
        else:
            # Menu retraído - mostrar apenas ícone
            content = ft.Icon(icon, size=18, color=icon_color)
            padding = ft.padding.all(10)
            print(f"[DEBUG] Item {title} criado no modo retraído")
        
        menu_item = ft.Container(
            content=content,
            padding=padding,
            bgcolor=bg_color,
            border_radius=8,
            border=ft.border.all(2, ft.colors.BLUE_300) if is_active else None,
            on_click=lambda e, view=view_id: self.change_view(view),
            tooltip=title if not self.sidebar_expanded else None,
            # Adicionar efeito visual
            ink=True,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
        
        print(f"[DEBUG] Item {title} criado com sucesso")
        return menu_item
    
    def change_view(self, view_id: str):
        """Muda a view atual"""
        print(f"[DEBUG] Mudando para view: {view_id}")
        self.current_view = view_id
        
        # Recriar o menu lateral para atualizar estados visuais
        self.sidebar = self.create_sidebar()
        
        # Atualizar conteúdo
        self.update_content()
        
        # Atualizar o container principal completamente
        self.main_container.controls = [
            self.sidebar,
            self.content_area
        ]
        
        # Atualizar página
        self.page.update()
        print(f"[DEBUG] View alterada para: {view_id}")
    
    def create_dashboard_view(self):
        """Cria a view do dashboard principal"""
        # Cards de estatísticas
        stats_cards = ft.Row([
            self.create_stat_card("👥", "Usuários", len(self.users_data), ft.colors.BLUE),
            self.create_stat_card("🚗", "Veículos", len(self.vehicles_data), ft.colors.GREEN),
            self.create_stat_card("📋", "Utilizações Ativas", 
                                len([u for u in self.usage_data if u.get('status') == 'em_uso']), 
                                ft.colors.ORANGE),
            self.create_stat_card("✅", "Concluídas Hoje", 
                                len([u for u in self.usage_data if u.get('status') == 'concluido']), 
                                ft.colors.PURPLE),
        ], spacing=20)
        
        # Gráfico de atividades recentes (placeholder)
        recent_activity = ft.Container(
            content=ft.Column([
                ft.Text("Atividades Recentes", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                *[self.create_activity_item(activity) for activity in self.get_recent_activities()[:5]]
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300)
        )
        
        return ft.Column([
            ft.Text("Dashboard Administrativo", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                   size=12, color=ft.colors.GREY_600),
            ft.Container(height=20),
            stats_cards,
            ft.Container(height=20),
            recent_activity
        ], scroll=ft.ScrollMode.AUTO)
    
    def create_stat_card(self, icon: str, title: str, value: int, color):
        """Cria um card de estatística"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(icon, size=32),
                    ft.Column([
                        ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(title, size=14, color=ft.colors.GREY_600)
                    ], spacing=0)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            width=200,
            height=100
        )
    
    def get_recent_activities(self):
        """Retorna atividades recentes do sistema"""
        activities = []
        
        # Atividades de usuários
        for user in self.users_data[-3:]:
            activities.append({
                'type': 'user',
                'icon': '👤',
                'description': f"Usuário {user.get('nome', 'N/A')} cadastrado",
                'time': user.get('data_criacao', datetime.now().isoformat())
            })
        
        # Atividades de veículos
        for vehicle in self.vehicles_data[-3:]:
            activities.append({
                'type': 'vehicle',
                'icon': '🚗',
                'description': f"Veículo {vehicle.get('modelo', 'N/A')} cadastrado",
                'time': vehicle.get('data_criacao', datetime.now().isoformat())
            })
        
        # Atividades de utilização
        for usage in self.usage_data[-3:]:
            activities.append({
                'type': 'usage',
                'icon': '📋',
                'description': f"Nova utilização registrada",
                'time': usage.get('data_inicio', datetime.now().isoformat())
            })
        
        # Ordenar por tempo (mais recentes primeiro)
        activities.sort(key=lambda x: x['time'], reverse=True)
        return activities
    
    def create_activity_item(self, activity):
        """Cria um item de atividade recente"""
        try:
            time_str = datetime.fromisoformat(activity['time'].replace('Z', '+00:00')).strftime('%d/%m %H:%M')
        except:
            time_str = "Agora"
            
        return ft.Container(
            content=ft.Row([
                ft.Text(activity['icon'], size=20),
                ft.Column([
                    ft.Text(activity['description'], size=14),
                    ft.Text(time_str, size=12, color=ft.colors.GREY_600)
                ], spacing=2),
            ], spacing=15),
            padding=ft.padding.symmetric(vertical=8)
        )
    
    def create_users_view(self):
        """Cria a view de gerenciamento de usuários"""
        # Header com botão de adicionar
        header = ft.Row([
            ft.Text("Gerenciamento de Usuários", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.icons.ADD),
                    ft.Text("Novo Usuário")
                ]),
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                on_click=self.show_add_user_dialog
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Tabela de usuários
        users_table = self.create_users_table()
        
        return ft.Column([
            header,
            ft.Container(height=20),
            users_table
        ], scroll=ft.ScrollMode.AUTO)
    
    def create_users_table(self):
        """Cria tabela de usuários"""
        if not self.users_data:
            return ft.Container(
                content=ft.Text("Nenhum usuário encontrado", text_align=ft.TextAlign.CENTER),
                padding=ft.padding.all(50)
            )
        
        # Header da tabela
        header = ft.Row([
            ft.Text("Avatar", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text("Nome", size=14, weight=ft.FontWeight.BOLD, expand=2),
            ft.Text("Email", size=14, weight=ft.FontWeight.BOLD, expand=2),
            ft.Text("Perfil", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text("Status", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text("Ações", size=14, weight=ft.FontWeight.BOLD, expand=1),
        ])
        
        # Linhas da tabela
        rows = []
        for user in self.users_data:
            status_color = ft.colors.GREEN if user.get('status') == 'ativo' else ft.colors.RED
            
            # Criar avatar para a tabela
            user_name = user.get('nome', 'U')
            user_initial = user_name[0].upper() if user_name else 'U'
            avatar_link = user.get('avatar_link')
            
            # Converter caminho para URL se necessário
            avatar_url = None
            if avatar_link:
                if avatar_link.startswith('public/'):
                    avatar_url = f"http://127.0.0.1:8000/{avatar_link}"
                elif not avatar_link.startswith('http'):
                    avatar_url = f"http://127.0.0.1:8000/public/avatar/{os.path.basename(avatar_link)}"
                else:
                    avatar_url = avatar_link
            
            # Criar componente de avatar para tabela
            if avatar_url:
                table_avatar = ft.Container(
                    content=ft.Image(
                        src=avatar_url,
                        width=45,
                        height=45,
                        fit=ft.ImageFit.COVER,
                        border_radius=ft.border_radius.all(22)
                    ),
                    width=45,
                    height=45,
                    border_radius=ft.border_radius.all(22),
                    bgcolor=ft.colors.BLUE,
                    border=ft.border.all(2, ft.colors.GREY_300),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=3,
                        color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                        offset=ft.Offset(0, 1)
                    )
                )
            else:
                table_avatar = ft.Container(
                    content=ft.CircleAvatar(
                        content=ft.Text(user_initial, size=18, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                        radius=22
                    ),
                    border=ft.border.all(2, ft.colors.GREY_300),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=3,
                        color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                        offset=ft.Offset(0, 1)
                    )
                )
            
            rows.append(
                ft.Row([
                    ft.Container(content=table_avatar, expand=1, alignment=ft.alignment.center),
                    ft.Text(user.get('nome', 'N/A'), expand=2),
                    ft.Text(user.get('email', 'N/A'), expand=2),
                    ft.Text(user.get('perfil', 'N/A').upper(), expand=1),
                    ft.Container(
                        content=ft.Text(user.get('status', 'N/A').upper(), color=ft.colors.WHITE, size=12),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=4,
                        expand=1
                    ),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.VISIBILITY,
                            tooltip="Ver Detalhes",
                            on_click=lambda e, u=user: self.view_user_details(u)
                        ),
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Editar",
                            on_click=lambda e, u=user: self.edit_user(u)
                        ),
                        ft.IconButton(
                            icon=ft.icons.POWER_SETTINGS_NEW,
                            tooltip="Ativar/Desativar",
                            icon_color=ft.colors.GREEN if user.get('status') == 'ativo' else ft.colors.ORANGE,
                            on_click=lambda e, u=user: self.toggle_user_status(u)
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            tooltip="Excluir",
                            icon_color=ft.colors.RED,
                            on_click=lambda e, u=user: self.delete_user(u)
                        )
                    ], expand=1)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                *rows
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300)
        )
    
    def show_add_user_dialog(self, e):
        """Mostra dialog para adicionar usuário"""
        # Campos do formulário
        nome_field = ft.TextField(label="Nome Completo", width=300)
        email_field = ft.TextField(label="Email", width=300)
        matricula_field = ft.TextField(label="Matrícula", width=300)
        perfil_dropdown = ft.Dropdown(
            label="Perfil",
            width=300,
            options=[
                ft.dropdown.Option("admin", "Administrador"),
                ft.dropdown.Option("gestor", "Gestor"),
                ft.dropdown.Option("motorista", "Motorista")
            ]
        )
        senha_field = ft.TextField(label="Senha", password=True, width=300)
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        def save_user(e):
            user_data = {
                "nome": nome_field.value,
                "email": email_field.value,
                "matricula": matricula_field.value,
                "perfil": perfil_dropdown.value,
                "senha": senha_field.value
            }
            
            try:
                response = self.api_client.create_user(user_data)
                if response and response.get('success'):
                    self.load_initial_data()
                    self.update_content()
                    self.page.dialog.open = False
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Usuário criado com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                    self.page.snack_bar.open = True
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Erro ao criar usuário: {response.get('message', 'Erro desconhecido')}"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao criar usuário: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Novo Usuário"),
            content=ft.Column([
                nome_field,
                email_field,
                matricula_field,
                perfil_dropdown,
                senha_field
            ], height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar", on_click=save_user)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def view_user_details(self, user):
        """Visualiza detalhes do usuário"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        details_content = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.CircleAvatar(
                        content=ft.Text(user.get('nome', 'U')[0].upper(), size=20, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                        radius=25
                    ),
                    ft.Column([
                        ft.Text(user.get('nome', 'N/A'), size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"ID: {user.get('id', 'N/A')}", size=12, color=ft.colors.GREY_600)
                    ], spacing=2)
                ], spacing=15),
                padding=ft.padding.only(bottom=20)
            ),
            
            ft.Container(
                content=ft.Column([
                    self.create_detail_row("📧", "Email", user.get('email', 'N/A')),
                    self.create_detail_row("🆔", "Matrícula", user.get('matricula', 'N/A')),
                    self.create_detail_row("👤", "Perfil", user.get('perfil', 'N/A').upper()),
                    self.create_detail_row("🏢", "Unidade", user.get('unidade', 'N/A')),
                    self.create_detail_row("📱", "Celular", user.get('celular', 'N/A')),
                    self.create_detail_row("⚡", "Status", user.get('status', 'N/A').upper()),
                    self.create_detail_row("📅", "Criado em", user.get('data_criacao', 'N/A')),
                ], spacing=10),
                padding=ft.padding.all(10),
                bgcolor=ft.colors.GREY_50,
                border_radius=8
            )
        ], spacing=15)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Detalhes do Usuário"),
            content=details_content,
            actions=[
                ft.ElevatedButton("Fechar", on_click=close_dialog)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def create_detail_row(self, icon, label, value):
        """Cria uma linha de detalhe"""
        return ft.Row([
            ft.Text(icon, size=16),
            ft.Text(f"{label}:", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text(str(value), size=14, expand=2)
        ])

    def edit_user(self, user):
        """Edita um usuário"""
        # Campos do formulário preenchidos
        nome_field = ft.TextField(label="Nome Completo", width=300, value=user.get('nome', ''))
        email_field = ft.TextField(label="Email", width=300, value=user.get('email', ''))
        matricula_field = ft.TextField(label="Matrícula", width=300, value=user.get('matricula', ''))
        perfil_dropdown = ft.Dropdown(
            label="Perfil",
            width=300,
            value=user.get('perfil', ''),
            options=[
                ft.dropdown.Option("admin", "Administrador"),
                ft.dropdown.Option("gestor", "Gestor"),
                ft.dropdown.Option("motorista", "Motorista")
            ]
        )
        unidade_field = ft.TextField(label="Unidade", width=300, value=user.get('unidade', ''))
        celular_field = ft.TextField(label="Celular", width=300, value=user.get('celular', ''))
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        def save_changes(e):
            user_data = {
                "nome": nome_field.value,
                "email": email_field.value,
                "matricula": matricula_field.value,
                "perfil": perfil_dropdown.value,
                "unidade": unidade_field.value,
                "celular": celular_field.value
            }
            
            try:
                response = self.api_client.update_user(user['id'], user_data)
                if response and response.get('success'):
                    self.load_initial_data()
                    self.update_content()
                    self.page.dialog.open = False
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Usuário atualizado com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                    self.page.snack_bar.open = True
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Erro ao atualizar usuário: {response.get('message', 'Erro desconhecido')}"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao atualizar usuário: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Usuário - {user.get('nome', 'N/A')}"),
            content=ft.Column([
                nome_field,
                email_field,
                matricula_field,
                perfil_dropdown,
                unidade_field,
                celular_field
            ], height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar Alterações", on_click=save_changes)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def toggle_user_status(self, user):
        """Alterna status do usuário (ativo/inativo)"""
        current_status = user.get('status', 'ativo')
        new_status = 'inativo' if current_status == 'ativo' else 'ativo'
        action = 'ativar' if new_status == 'ativo' else 'desativar'
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        def confirm_toggle(e):
            try:
                if new_status == 'ativo':
                    response = self.api_client.activate_user(user['id'])
                else:
                    response = self.api_client.deactivate_user(user['id'])
                
                if response and response.get('success'):
                    self.load_initial_data()
                    self.update_content()
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Usuário {action}do com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Erro ao {action} usuário!"),
                        bgcolor=ft.colors.RED
                    )
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao {action} usuário: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
            
            self.page.dialog.open = False
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Confirmar {action.title()}ação"),
            content=ft.Text(f"Deseja realmente {action} o usuário {user.get('nome', 'N/A')}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton(
                    f"{action.title()}",
                    bgcolor=ft.colors.GREEN if new_status == 'ativo' else ft.colors.ORANGE,
                    color=ft.colors.WHITE,
                    on_click=confirm_toggle
                )
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_user(self, user):
        """Exclui um usuário"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        def confirm_delete(e):
            try:
                response = self.api_client.delete_user(user['id'])
                if response and response.get('success'):
                    self.load_initial_data()
                    self.update_content()
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Usuário excluído com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Erro ao excluir usuário!"),
                        bgcolor=ft.colors.RED
                    )
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao excluir usuário: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
            self.page.dialog.open = False
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(f"Deseja realmente excluir o usuário {user.get('nome', 'N/A')}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Excluir", bgcolor=ft.colors.RED, color=ft.colors.WHITE, on_click=confirm_delete)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def create_vehicles_view(self):
        """Cria a view de gerenciamento de veículos"""
        # Header com botão de adicionar
        header = ft.Row([
            ft.Text("Gerenciamento de Veículos", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.icons.ADD),
                    ft.Text("Novo Veículo")
                ]),
                bgcolor=ft.colors.GREEN,
                color=ft.colors.WHITE,
                on_click=self.show_add_vehicle_dialog
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Tabela de veículos
        vehicles_table = self.create_vehicles_table()
        
        return ft.Column([
            header,
            ft.Container(height=20),
            vehicles_table
        ], scroll=ft.ScrollMode.AUTO)
    
    def create_vehicles_table(self):
        """Cria tabela de veículos"""
        if not self.vehicles_data:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.DIRECTIONS_CAR, size=64, color=ft.colors.GREY_400),
                    ft.Text("Nenhum veículo cadastrado", size=18, color=ft.colors.GREY_600),
                    ft.Text("Clique em 'Novo Veículo' para começar", size=14, color=ft.colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(50),
                alignment=ft.alignment.center
            )
        
        # Header da tabela
        header = ft.Row([
            ft.Text("Modelo", size=14, weight=ft.FontWeight.BOLD, expand=2),
            ft.Text("Placa", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text("Tipo", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text("Ano", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text("Status", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text("Ações", size=14, weight=ft.FontWeight.BOLD, expand=1),
        ])
        
        # Linhas da tabela
        rows = []
        for vehicle in self.vehicles_data:
            status_color = ft.colors.GREEN if vehicle.get('status') == 'disponivel' else ft.colors.RED
            
            # Corrigir problema com campos None
            tipo_text = vehicle.get('tipo') or 'N/A'
            status_text = vehicle.get('status') or 'N/A'
            
            rows.append(
                ft.Row([
                    ft.Text(f"{vehicle.get('marca', 'N/A')} {vehicle.get('modelo', 'N/A')}", expand=2),
                    ft.Text(vehicle.get('placa', 'N/A'), expand=1),
                    ft.Text(tipo_text.upper() if tipo_text != 'N/A' else 'N/A', expand=1),
                    ft.Text(str(vehicle.get('ano', 'N/A')), expand=1),
                    ft.Container(
                        content=ft.Text(status_text.upper() if status_text != 'N/A' else 'N/A', color=ft.colors.WHITE, size=12),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=4,
                        expand=1
                    ),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.VISIBILITY,
                            tooltip="Ver Detalhes",
                            on_click=lambda e, v=vehicle: self.view_vehicle_details(v)
                        ),
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Editar",
                            on_click=lambda e, v=vehicle: self.edit_vehicle(v)
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            tooltip="Excluir",
                            icon_color=ft.colors.RED,
                            on_click=lambda e, v=vehicle: self.delete_vehicle(v)
                        )
                    ], expand=1)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                *rows
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300)
        )
    
    def show_add_vehicle_dialog(self, e):
        """Mostra dialog para adicionar veículo"""
        # Campos do formulário
        marca_field = ft.TextField(label="Marca", width=300)
        modelo_field = ft.TextField(label="Modelo", width=300)
        placa_field = ft.TextField(label="Placa", width=300)
        tipo_dropdown = ft.Dropdown(
            label="Tipo do Veículo",
            width=300,
            options=[
                ft.dropdown.Option("carro", "Carro"),
                ft.dropdown.Option("moto", "Moto"),
                ft.dropdown.Option("caminhao", "Caminhão"),
                ft.dropdown.Option("van", "Van"),
                ft.dropdown.Option("onibus", "Ônibus"),
                ft.dropdown.Option("utilitario", "Utilitário"),
                ft.dropdown.Option("pickup", "Pickup")
            ]
        )
        ano_field = ft.TextField(label="Ano", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        combustivel_dropdown = ft.Dropdown(
            label="Combustível",
            width=300,
            options=[
                ft.dropdown.Option("gasolina", "Gasolina"),
                ft.dropdown.Option("etanol", "Etanol"),
                ft.dropdown.Option("flex", "Flex"),
                ft.dropdown.Option("diesel", "Diesel"),
                ft.dropdown.Option("gnv", "GNV"),
                ft.dropdown.Option("eletrico", "Elétrico"),
                ft.dropdown.Option("hibrido", "Híbrido")
            ]
        )
        cor_field = ft.TextField(label="Cor", width=300)
        quilometragem_field = ft.TextField(label="Quilometragem Atual", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        status_dropdown = ft.Dropdown(
            label="Status",
            width=300,
            value="disponivel",
            options=[
                ft.dropdown.Option("disponivel", "Disponível"),
                ft.dropdown.Option("em_uso", "Em Uso"),
                ft.dropdown.Option("manutencao", "Em Manutenção"),
                ft.dropdown.Option("inativo", "Inativo")
            ]
        )
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        def save_vehicle(e):
            vehicle_data = {
                "marca": marca_field.value,
                "modelo": modelo_field.value,
                "placa": placa_field.value,
                "tipo": tipo_dropdown.value,
                "ano": int(ano_field.value) if ano_field.value else None,
                "combustivel": combustivel_dropdown.value,
                "cor": cor_field.value,
                "quilometragem_atual": float(quilometragem_field.value) if quilometragem_field.value else 0,
                "status": status_dropdown.value
            }
            
            try:
                response = self.api_client.create_vehicle(vehicle_data)
                if response and response.get('success'):
                    self.load_initial_data()
                    self.update_content()
                    self.page.dialog.open = False
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Veículo criado com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                    self.page.snack_bar.open = True
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Erro ao criar veículo: {response.get('message', 'Erro desconhecido')}"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao criar veículo: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Novo Veículo"),
            content=ft.Column([
                marca_field,
                modelo_field,
                placa_field,
                tipo_dropdown,
                ano_field,
                combustivel_dropdown,
                cor_field,
                quilometragem_field,
                status_dropdown
            ], height=500, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar", on_click=save_vehicle)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def view_vehicle_details(self, vehicle):
        """Visualiza detalhes do veículo"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Determinar cor do status
        status_colors = {
            'disponivel': ft.colors.GREEN,
            'em_uso': ft.colors.BLUE,
            'manutencao': ft.colors.ORANGE,
            'inativo': ft.colors.RED
        }
        status_color = status_colors.get(vehicle.get('status', 'disponivel'), ft.colors.GREY)
        
        details_content = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.DIRECTIONS_CAR, size=40, color=ft.colors.BLUE),
                    ft.Column([
                        ft.Text(f"{vehicle.get('marca', 'N/A')} {vehicle.get('modelo', 'N/A')}", 
                               size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"ID: {vehicle.get('id', 'N/A')}", size=12, color=ft.colors.GREY_600)
                    ], spacing=2)
                ], spacing=15),
                padding=ft.padding.only(bottom=20)
            ),
            
            ft.Container(
                content=ft.Column([
                    self.create_detail_row("🚗", "Marca", vehicle.get('marca', 'N/A')),
                    self.create_detail_row("📝", "Modelo", vehicle.get('modelo', 'N/A')),
                    self.create_detail_row("🆔", "Placa", vehicle.get('placa', 'N/A')),
                    self.create_detail_row("🚙", "Tipo", vehicle.get('tipo', 'N/A').title()),
                    self.create_detail_row("📅", "Ano", str(vehicle.get('ano', 'N/A'))),
                    self.create_detail_row("⛽", "Combustível", vehicle.get('combustivel', 'N/A').title()),
                    self.create_detail_row("🎨", "Cor", vehicle.get('cor', 'N/A')),
                    self.create_detail_row("📏", "Quilometragem", f"{vehicle.get('quilometragem_atual', 'N/A')} km"),
                    ft.Row([
                        ft.Text("⚡", size=16),
                        ft.Text("Status:", size=14, weight=ft.FontWeight.BOLD, expand=1),
                        ft.Container(
                            content=ft.Text(vehicle.get('status', 'N/A').upper(), 
                                           color=ft.colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=4
                        )
                    ]),
                    self.create_detail_row("📅", "Criado em", vehicle.get('data_criacao', 'N/A')),
                ], spacing=12),
                padding=ft.padding.all(15),
                bgcolor=ft.colors.GREY_50,
                border_radius=8
            )
        ], spacing=15)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Detalhes do Veículo"),
            content=details_content,
            actions=[
                ft.ElevatedButton("Fechar", on_click=close_dialog)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def edit_vehicle(self, vehicle):
        """Edita um veículo"""
        # Campos do formulário preenchidos
        marca_field = ft.TextField(label="Marca", width=300, value=vehicle.get('marca', ''))
        modelo_field = ft.TextField(label="Modelo", width=300, value=vehicle.get('modelo', ''))
        placa_field = ft.TextField(label="Placa", width=300, value=vehicle.get('placa', ''))
        tipo_dropdown = ft.Dropdown(
            label="Tipo do Veículo",
            width=300,
            value=vehicle.get('tipo', ''),
            options=[
                ft.dropdown.Option("carro", "Carro"),
                ft.dropdown.Option("moto", "Moto"),
                ft.dropdown.Option("caminhao", "Caminhão"),
                ft.dropdown.Option("van", "Van"),
                ft.dropdown.Option("onibus", "Ônibus"),
                ft.dropdown.Option("utilitario", "Utilitário"),
                ft.dropdown.Option("pickup", "Pickup")
            ]
        )
        ano_field = ft.TextField(label="Ano", width=300, value=str(vehicle.get('ano', '')), keyboard_type=ft.KeyboardType.NUMBER)
        combustivel_dropdown = ft.Dropdown(
            label="Combustível",
            width=300,
            value=vehicle.get('combustivel', ''),
            options=[
                ft.dropdown.Option("gasolina", "Gasolina"),
                ft.dropdown.Option("etanol", "Etanol"),
                ft.dropdown.Option("flex", "Flex"),
                ft.dropdown.Option("diesel", "Diesel"),
                ft.dropdown.Option("gnv", "GNV"),
                ft.dropdown.Option("eletrico", "Elétrico"),
                ft.dropdown.Option("hibrido", "Híbrido")
            ]
        )
        cor_field = ft.TextField(label="Cor", width=300, value=vehicle.get('cor', ''))
        quilometragem_field = ft.TextField(label="Quilometragem Atual", width=300, 
                                         value=str(vehicle.get('quilometragem_atual', '')), 
                                         keyboard_type=ft.KeyboardType.NUMBER)
        status_dropdown = ft.Dropdown(
            label="Status",
            width=300,
            value=vehicle.get('status', 'disponivel'),
            options=[
                ft.dropdown.Option("disponivel", "Disponível"),
                ft.dropdown.Option("em_uso", "Em Uso"),
                ft.dropdown.Option("manutencao", "Em Manutenção"),
                ft.dropdown.Option("inativo", "Inativo")
            ]
        )
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        def save_changes(e):
            vehicle_data = {
                "marca": marca_field.value,
                "modelo": modelo_field.value,
                "placa": placa_field.value,
                "tipo": tipo_dropdown.value,
                "ano": int(ano_field.value) if ano_field.value else None,
                "combustivel": combustivel_dropdown.value,
                "cor": cor_field.value,
                "quilometragem_atual": float(quilometragem_field.value) if quilometragem_field.value else 0,
                "status": status_dropdown.value
            }
            
            try:
                response = self.api_client.update_vehicle(vehicle['id'], vehicle_data)
                if response and response.get('success'):
                    self.load_initial_data()
                    self.update_content()
                    self.page.dialog.open = False
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Veículo atualizado com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                    self.page.snack_bar.open = True
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Erro ao atualizar veículo: {response.get('message', 'Erro desconhecido')}"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao atualizar veículo: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Veículo - {vehicle.get('marca', 'N/A')} {vehicle.get('modelo', 'N/A')}"),
            content=ft.Column([
                marca_field,
                modelo_field,
                placa_field,
                tipo_dropdown,
                ano_field,
                combustivel_dropdown,
                cor_field,
                quilometragem_field,
                status_dropdown
            ], height=500, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar Alterações", on_click=save_changes)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def delete_vehicle(self, vehicle):
        """Exclui um veículo"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        def confirm_delete(e):
            try:
                response = self.api_client.delete_vehicle(vehicle['id'])
                if response and response.get('success'):
                    self.load_initial_data()
                    self.update_content()
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Veículo excluído com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Erro ao excluir veículo!"),
                        bgcolor=ft.colors.RED
                    )
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao excluir veículo: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
            self.page.dialog.open = False
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(f"Deseja realmente excluir o veículo {vehicle.get('marca', 'N/A')} {vehicle.get('modelo', 'N/A')}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Excluir", bgcolor=ft.colors.RED, color=ft.colors.WHITE, on_click=confirm_delete)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def create_usage_view(self):
        """Cria a view de controle de uso"""
        # Header com botão de nova utilização
        header = ft.Row([
            ft.Text("Controle de Utilização de Veículos", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.icons.ADD),
                    ft.Text("Nova Utilização")
                ]),
                bgcolor=ft.colors.ORANGE,
                color=ft.colors.WHITE,
                on_click=self.show_add_usage_dialog
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Filtros
        filters = ft.Row([
            ft.Dropdown(
                label="Status",
                width=150,
                options=[
                    ft.dropdown.Option("todos", "Todos"),
                    ft.dropdown.Option("em_uso", "Em Uso"),
                    ft.dropdown.Option("concluido", "Concluído"),
                    ft.dropdown.Option("cancelado", "Cancelado")
                ],
                value="todos"
            ),
            ft.DatePicker(),
            ft.ElevatedButton("Filtrar", on_click=self.filter_usage_records)
        ], spacing=20)
        
        # Tabela de utilizações
        usage_table = self.create_usage_table()
        
        return ft.Column([
            header,
            ft.Container(height=10),
            filters,
            ft.Container(height=20),
            usage_table
        ], scroll=ft.ScrollMode.AUTO)
    
    def create_usage_table(self):
        """Cria tabela de utilizações"""
        if not self.usage_data:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ASSIGNMENT, size=64, color=ft.colors.GREY_400),
                    ft.Text("Nenhuma utilização registrada", size=18, color=ft.colors.GREY_600),
                    ft.Text("Clique em 'Nova Utilização' para começar", size=14, color=ft.colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(50),
                alignment=ft.alignment.center
            )
        
        # Header da tabela
        header = ft.Row([
            ft.Text("Motorista", size=14, weight=ft.FontWeight.BOLD, expand=2),
            ft.Text("Veículo", size=14, weight=ft.FontWeight.BOLD, expand=2),
            ft.Text("Destino", size=14, weight=ft.FontWeight.BOLD, expand=2),
            ft.Text("Data/Hora", size=14, weight=ft.FontWeight.BOLD, expand=2),
            ft.Text("Status", size=14, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text("Ações", size=14, weight=ft.FontWeight.BOLD, expand=1),
        ])
        
        # Linhas da tabela
        rows = []
        for usage in self.usage_data:
            status_colors = {
                'em_uso': ft.colors.BLUE,
                'concluido': ft.colors.GREEN,
                'cancelado': ft.colors.RED
            }
            status_color = status_colors.get(usage.get('status'), ft.colors.GREY)
            
            try:
                data_inicio = datetime.fromisoformat(usage.get('data_inicio', '')).strftime('%d/%m/%Y %H:%M')
            except:
                data_inicio = 'N/A'
            
            rows.append(
                ft.Row([
                    ft.Text(usage.get('motorista_nome', 'N/A'), expand=2),
                    ft.Text(f"{usage.get('veiculo_marca', 'N/A')} {usage.get('veiculo_modelo', 'N/A')}", expand=2),
                    ft.Text(usage.get('destino', 'N/A'), expand=2),
                    ft.Text(data_inicio, expand=2),
                    ft.Container(
                        content=ft.Text(usage.get('status', 'N/A').upper(), color=ft.colors.WHITE, size=12),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=4,
                        expand=1
                    ),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.VISIBILITY,
                            tooltip="Ver Detalhes",
                            on_click=lambda e, u=usage: self.view_usage_details(u)
                        ),
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Editar",
                            on_click=lambda e, u=usage: self.edit_usage(u)
                        ) if usage.get('status') == 'em_uso' else ft.Container()
                    ], expand=1)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                *rows
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300)
        )
    
    def show_add_usage_dialog(self, e):
        """Mostra dialog para nova utilização"""
        # Carregar dados necessários
        users_options = [ft.dropdown.Option(str(u.get('id')), u.get('nome', 'N/A')) for u in self.users_data if u.get('perfil') in ['motorista', 'gestor']]
        vehicles_options = [ft.dropdown.Option(str(v.get('id')), f"{v.get('marca', 'N/A')} {v.get('modelo', 'N/A')} - {v.get('placa', 'N/A')}") for v in self.vehicles_data if v.get('status') == 'disponivel']
        
        # Campos do formulário
        motorista_dropdown = ft.Dropdown(
            label="Motorista",
            width=300,
            options=users_options
        )
        veiculo_dropdown = ft.Dropdown(
            label="Veículo",
            width=300,
            options=vehicles_options
        )
        destino_field = ft.TextField(label="Destino", width=300)
        finalidade_field = ft.TextField(label="Finalidade da Viagem", width=300, multiline=True, max_lines=3)
        quilometragem_saida_field = ft.TextField(label="Quilometragem de Saída", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        
        def save_usage(e):
            usage_data = {
                "motorista_id": int(motorista_dropdown.value) if motorista_dropdown.value else None,
                "veiculo_id": int(veiculo_dropdown.value) if veiculo_dropdown.value else None,
                "destino": destino_field.value,
                "finalidade": finalidade_field.value,
                "quilometragem_saida": float(quilometragem_saida_field.value) if quilometragem_saida_field.value else None,
                "data_inicio": datetime.now().isoformat(),
                "status": "em_uso"
            }
            
            try:
                response = self.api_client.create_usage_record(usage_data)
                if response and response.get('success'):
                    self.load_initial_data()
                    self.update_content()
                    self.page.dialog.open = False
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Utilização registrada com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                    self.page.snack_bar.open = True
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Erro ao registrar utilização: {response.get('message', 'Erro desconhecido')}"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
            except Exception as error:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao registrar utilização: {str(error)}"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nova Utilização de Veículo"),
            content=ft.Column([
                motorista_dropdown,
                veiculo_dropdown,
                destino_field,
                finalidade_field,
                quilometragem_saida_field,
                ft.Text("Obs: A data/hora de início será registrada automaticamente", size=12, color=ft.colors.GREY_600)
            ], height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(self.page.dialog, 'open', False)),
                ft.ElevatedButton("Registrar", on_click=save_usage)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def view_usage_details(self, usage):
        """Visualiza detalhes da utilização"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Detalhes da utilização - Em desenvolvimento"),
            bgcolor=ft.colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def edit_usage(self, usage):
        """Edita uma utilização"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Edição de utilização - Em desenvolvimento"),
            bgcolor=ft.colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def filter_usage_records(self, e):
        """Filtra registros de utilização"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Filtros de utilização - Em desenvolvimento"),
            bgcolor=ft.colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def create_routes_view(self):
        """Cria a view de rotas"""
        return ft.Container(
            content=ft.Text("Gerenciamento de Rotas - Em desenvolvimento"),
            padding=ft.padding.all(50)
        )
    
    def create_reports_view(self):
        """Cria a view de relatórios"""
        # Header
        header = ft.Text("Relatórios e Estatísticas", size=20, weight=ft.FontWeight.BOLD)
        
        # Cards de relatórios disponíveis
        reports_grid = ft.Row([
            # Relatório de Utilização
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ASSIGNMENT, size=48, color=ft.colors.BLUE),
                    ft.Text("Relatório de Utilização", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text("Histórico de utilização dos veículos", size=12, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Gerar Relatório",
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                        on_click=lambda e: self.generate_usage_report()
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.BLUE_50,
                border_radius=10,
                width=250,
                height=200
            ),
            
            # Relatório de Veículos
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.DIRECTIONS_CAR, size=48, color=ft.colors.GREEN),
                    ft.Text("Relatório de Veículos", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text("Status e informações da frota", size=12, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Gerar Relatório",
                        bgcolor=ft.colors.GREEN,
                        color=ft.colors.WHITE,
                        on_click=lambda e: self.generate_vehicles_report()
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.GREEN_50,
                border_radius=10,
                width=250,
                height=200
            ),
            
            # Relatório de Motoristas
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.PERSON, size=48, color=ft.colors.ORANGE),
                    ft.Text("Relatório de Motoristas", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text("Atividades dos motoristas", size=12, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Gerar Relatório",
                        bgcolor=ft.colors.ORANGE,
                        color=ft.colors.WHITE,
                        on_click=lambda e: self.generate_drivers_report()
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.ORANGE_50,
                border_radius=10,
                width=250,
                height=200
            ),
            
            # Relatório Estatístico
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.BAR_CHART, size=48, color=ft.colors.PURPLE),
                    ft.Text("Estatísticas Gerais", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text("Métricas e indicadores", size=12, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Gerar Relatório",
                        bgcolor=ft.colors.PURPLE,
                        color=ft.colors.WHITE,
                        on_click=lambda e: self.generate_statistics_report()
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.PURPLE_50,
                border_radius=10,
                width=250,
                height=200
            )
        ], spacing=20, wrap=True)
        
        # Estatísticas rápidas
        quick_stats = ft.Container(
            content=ft.Column([
                ft.Text("Estatísticas Rápidas", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([
                    ft.Column([
                        ft.Text("Total de Viagens", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(str(len(self.usage_data)), size=24, color=ft.colors.BLUE)
                    ]),
                    ft.Column([
                        ft.Text("Veículos Ativos", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(str(len([v for v in self.vehicles_data if v.get('status') == 'disponivel'])), size=24, color=ft.colors.GREEN)
                    ]),
                    ft.Column([
                        ft.Text("Utilizações em Andamento", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(str(len([u for u in self.usage_data if u.get('status') == 'em_uso'])), size=24, color=ft.colors.ORANGE)
                    ]),
                    ft.Column([
                        ft.Text("Motoristas Cadastrados", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(str(len([u for u in self.users_data if u.get('perfil') in ['motorista', 'gestor']])), size=24, color=ft.colors.PURPLE)
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300)
        )
        
        return ft.Column([
            header,
            ft.Container(height=20),
            reports_grid,
            ft.Container(height=30),
            quick_stats
        ], scroll=ft.ScrollMode.AUTO)
    
    def generate_usage_report(self):
        """Gera relatório de utilização"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Relatório de utilização - Em desenvolvimento"),
            bgcolor=ft.colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def generate_vehicles_report(self):
        """Gera relatório de veículos"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Relatório de veículos - Em desenvolvimento"),
            bgcolor=ft.colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def generate_drivers_report(self):
        """Gera relatório de motoristas"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Relatório de motoristas - Em desenvolvimento"),
            bgcolor=ft.colors.ORANGE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def generate_statistics_report(self):
        """Gera relatório estatístico"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Estatísticas gerais - Em desenvolvimento"),
            bgcolor=ft.colors.PURPLE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def update_content(self):
        """Atualiza o conteúdo baseado na view atual"""
        # Recriar sidebar para atualizar item ativo
        self.sidebar = self.create_sidebar()
        
        # Determinar qual view mostrar
        if self.current_view == "dashboard":
            content = self.create_dashboard_view()
        elif self.current_view == "users":
            content = self.create_users_view()
        elif self.current_view == "vehicles":
            content = self.create_vehicles_view()
        elif self.current_view == "usage":
            content = self.create_usage_view()
        elif self.current_view == "routes":
            content = self.create_routes_view()
        elif self.current_view == "reports":
            content = self.create_reports_view()
        else:
            content = self.create_dashboard_view()
        
        self.content_area.content = ft.Container(
            content=content,
            padding=ft.padding.all(30),
            expand=True
        )
    
    def logout(self, e):
        """Faz logout do sistema"""
        try:
            self.api_client.logout()
            if self.on_logout_callback:
                self.on_logout_callback()
            else:
                # Fallback: limpar página e mostrar mensagem
                self.page.clean()
                self.page.add(ft.Text("Logout realizado com sucesso. Recarregue a página.", size=18))
                self.page.update()
        except Exception as error:
            print(f"Erro no logout: {error}")
            # Mesmo com erro, tentar fazer logout
            if self.on_logout_callback:
                self.on_logout_callback()
    
    def get_view(self):
        """Retorna a view principal"""
        print("[DEBUG] get_view chamado - criando layout principal")
        
        # Sempre recriar sidebar para garantir que existe
        print(f"[DEBUG] Estado do sidebar expandido: {self.sidebar_expanded}")
        self.sidebar = self.create_sidebar()
        print(f"[DEBUG] Sidebar criado com largura: {getattr(self.sidebar, 'width', 'N/A')}")
        
        # Atualizar conteúdo
        self.update_content()
        print("[DEBUG] Conteúdo atualizado")
        
        # Criar layout principal
        self.main_container = ft.Row([
            self.sidebar,
            ft.VerticalDivider(width=1, color=ft.colors.GREY_300),
            self.content_area
        ], expand=True, spacing=0)
        
        print(f"[DEBUG] Layout principal criado com {len(self.main_container.controls)} controles")
        return self.main_container
