import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import SGUVApiClient
from datetime import datetime

class DriverDashboardView:
    def __init__(self, page: ft.Page, api_client: SGUVApiClient, user_data: dict):
        self.page = page
        self.api_client = api_client
        self.user_data = user_data
        
        # Estado atual
        self.current_control = None
        self.current_route = None
        self.vehicles = []
        
        # Componentes principais
        self.create_components()
        
    def create_components(self):
        """Cria os componentes da interface"""
        
        # Header com informações do usuário
        self.header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.PERSON, size=30),
                ft.Column([
                    ft.Text(f"Olá, {self.user_data['nome']}", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Matrícula: {self.user_data['matricula']} | Unidade: {self.user_data.get('unidade', 'N/A')}", size=12)
                ], spacing=2),
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    tooltip="Sair",
                    on_click=self.handle_logout
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=ft.colors.BLUE_50,
            padding=ft.padding.all(15),
            border_radius=10
        )
        
        # Cards de status
        self.status_cards = ft.Row([
            self.create_status_card("Controles Ativos", "0", ft.icons.PLAY_CIRCLE, ft.colors.GREEN),
            self.create_status_card("KM Total Hoje", "0", ft.icons.SPEED, ft.colors.BLUE),
            self.create_status_card("Rotas Hoje", "0", ft.icons.ROUTE, ft.colors.ORANGE)
        ], spacing=10)
        
        # Botões de ação principal
        self.action_buttons = ft.Column([
            ft.ElevatedButton(
                text="Iniciar Novo Controle",
                icon=ft.icons.ADD_CIRCLE,
                width=300,
                height=50,
                on_click=self.show_new_control_dialog,
                style=ft.ButtonStyle(bgcolor=ft.colors.GREEN, color=ft.colors.WHITE)
            ),
            ft.ElevatedButton(
                text="Adicionar Rota",
                icon=ft.icons.ADD_LOCATION,
                width=300,
                height=50,
                on_click=self.show_new_route_dialog,
                disabled=True,  # Habilitado apenas quando há controle ativo
                style=ft.ButtonStyle(bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
            ),
            ft.ElevatedButton(
                text="Finalizar Controle",
                icon=ft.icons.STOP_CIRCLE,
                width=300,
                height=50,
                on_click=self.show_finalize_control_dialog,
                disabled=True,  # Habilitado apenas quando há controle ativo
                style=ft.ButtonStyle(bgcolor=ft.colors.RED, color=ft.colors.WHITE)
            )
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Lista de controles recentes
        self.controls_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Container principal
        self.main_content = ft.Column([
            self.header,
            ft.Divider(),
            ft.Text("Status Atual", size=20, weight=ft.FontWeight.BOLD),
            self.status_cards,
            ft.Divider(),
            ft.Text("Ações", size=20, weight=ft.FontWeight.BOLD),
            self.action_buttons,
            ft.Divider(),
            ft.Text("Meus Controles", size=20, weight=ft.FontWeight.BOLD),
            self.controls_list
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def create_status_card(self, title: str, value: str, icon: str, color: str):
        """Cria um card de status"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=30, color=color),
                ft.Text(title, size=12, text_align=ft.TextAlign.CENTER),
                ft.Text(value, size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=150,
            height=100,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, color),
            border_radius=10,
            padding=ft.padding.all(10)
        )
    
    def build(self):
        """Constrói a interface principal"""
        self.refresh_data()
        return self.main_content
    
    def refresh_data(self):
        """Atualiza os dados da interface"""
        try:
            # Buscar controles do usuário
            my_controls = self.api_client.get_my_usage_controls()
            open_controls = self.api_client.get_open_usage_controls()
            
            # Atualizar controle atual
            if open_controls:
                self.current_control = open_controls[0]
                self.action_buttons.controls[1].disabled = False  # Adicionar Rota
                self.action_buttons.controls[2].disabled = False  # Finalizar Controle
                self.action_buttons.controls[0].disabled = True   # Iniciar Novo
            else:
                self.current_control = None
                self.action_buttons.controls[1].disabled = True   # Adicionar Rota
                self.action_buttons.controls[2].disabled = True   # Finalizar Controle
                self.action_buttons.controls[0].disabled = False  # Iniciar Novo
            
            # Atualizar cards de status
            active_controls = len(open_controls)
            total_km_today = sum(
                (control.get('km_final', control.get('km_inicial', 0)) - control.get('km_inicial', 0))
                for control in my_controls
                if control.get('data_inicio', '').startswith(datetime.now().strftime('%Y-%m-%d'))
            )
            total_routes_today = sum(
                len(self.api_client.get_routes_by_control(control['id']))
                for control in my_controls
                if control.get('data_inicio', '').startswith(datetime.now().strftime('%Y-%m-%d'))
            )
            
            self.status_cards.controls[0].content.controls[2].value = str(active_controls)
            self.status_cards.controls[1].content.controls[2].value = f"{total_km_today:.1f}"
            self.status_cards.controls[2].content.controls[2].value = str(total_routes_today)
            
            # Atualizar lista de controles
            self.update_controls_list(my_controls)
            
            self.page.update()
            
        except Exception as e:
            self.show_error(f"Erro ao carregar dados: {str(e)}")
    
    def update_controls_list(self, controls):
        """Atualiza a lista de controles"""
        self.controls_list.controls.clear()
        
        for control in controls[:10]:  # Mostrar apenas os 10 mais recentes
            status_color = {
                'aberto': ft.colors.GREEN,
                'finalizado': ft.colors.BLUE,
                'cancelado': ft.colors.RED
            }.get(control['status'], ft.colors.GREY)
            
            control_card = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(f"Veículo: {control.get('veiculo', {}).get('placa', 'N/A')}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Início: {control.get('data_inicio', 'N/A')}"),
                        ft.Text(f"KM Inicial: {control.get('km_inicial', 0)}"),
                        ft.Text(f"Status: {control.get('status', 'N/A').title()}", color=status_color)
                    ], expand=True),
                    ft.IconButton(
                        icon=ft.icons.VISIBILITY,
                        tooltip="Ver Detalhes",
                        on_click=lambda e, ctrl=control: self.show_control_details(ctrl)
                    )
                ]),
                bgcolor=ft.colors.GREY_50,
                padding=ft.padding.all(10),
                border_radius=5,
                margin=ft.margin.only(bottom=5)
            )
            
            self.controls_list.controls.append(control_card)
    
    def show_new_control_dialog(self, e):
        """Mostra diálogo para iniciar novo controle"""
        try:
            # Buscar veículos disponíveis
            self.vehicles = self.api_client.get_available_vehicles()
            
            if not self.vehicles:
                self.show_error("Não há veículos disponíveis no momento")
                return
            
            vehicle_dropdown = ft.Dropdown(
                label="Selecionar Veículo",
                options=[
                    ft.dropdown.Option(str(v['id']), f"{v['marca']} {v['modelo']} - {v['placa']}")
                    for v in self.vehicles
                ],
                width=300
            )
            
            km_field = ft.TextField(
                label="KM Inicial",
                width=300,
                keyboard_type=ft.KeyboardType.NUMBER
            )
            
            def create_control(e):
                if not vehicle_dropdown.value or not km_field.value:
                    self.show_error("Por favor, preencha todos os campos")
                    return
                
                try:
                    km_inicial = float(km_field.value)
                    result = self.api_client.create_usage_control(int(vehicle_dropdown.value), km_inicial)
                    
                    self.page.close_dialog()
                    self.show_success("Controle de utilização iniciado com sucesso!")
                    self.refresh_data()
                    
                except ValueError:
                    self.show_error("KM deve ser um número válido")
                except Exception as ex:
                    self.show_error(f"Erro ao criar controle: {str(ex)}")
            
            dialog = ft.AlertDialog(
                title=ft.Text("Iniciar Novo Controle"),
                content=ft.Column([
                    vehicle_dropdown,
                    km_field
                ], tight=True),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.page.close_dialog()),
                    ft.ElevatedButton("Iniciar", on_click=create_control)
                ]
            )
            
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
            
        except Exception as ex:
            self.show_error(f"Erro ao carregar veículos: {str(ex)}")
    
    def show_new_route_dialog(self, e):
        """Mostra diálogo para adicionar nova rota"""
        if not self.current_control:
            self.show_error("Não há controle ativo")
            return
        
        km_saida_field = ft.TextField(
            label="KM de Saída",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        local_saida_field = ft.TextField(
            label="Local de Saída (opcional)",
            width=300,
            multiline=True
        )
        
        def create_route(e):
            if not km_saida_field.value:
                self.show_error("KM de saída é obrigatório")
                return
            
            try:
                km_saida = float(km_saida_field.value)
                result = self.api_client.create_route(
                    self.current_control['id'],
                    km_saida,
                    logradouro_saida=local_saida_field.value or ""
                )
                
                self.page.close_dialog()
                self.show_success("Rota adicionada com sucesso!")
                self.refresh_data()
                
            except ValueError:
                self.show_error("KM deve ser um número válido")
            except Exception as ex:
                self.show_error(f"Erro ao criar rota: {str(ex)}")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Adicionar Nova Rota"),
            content=ft.Column([
                ft.Text(f"Controle: {self.current_control.get('veiculo', {}).get('placa', 'N/A')}"),
                km_saida_field,
                local_saida_field
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close_dialog()),
                ft.ElevatedButton("Adicionar", on_click=create_route)
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def show_finalize_control_dialog(self, e):
        """Mostra diálogo para finalizar controle"""
        if not self.current_control:
            self.show_error("Não há controle ativo")
            return
        
        km_final_field = ft.TextField(
            label="KM Final",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        assinatura_field = ft.TextField(
            label="Assinatura Eletrônica (seu nome completo)",
            width=300
        )
        
        def finalize_control(e):
            if not km_final_field.value or not assinatura_field.value:
                self.show_error("Todos os campos são obrigatórios")
                return
            
            try:
                km_final = float(km_final_field.value)
                if km_final <= self.current_control['km_inicial']:
                    self.show_error("KM final deve ser maior que o KM inicial")
                    return
                
                result = self.api_client.finalize_usage_control(
                    self.current_control['id'],
                    km_final,
                    assinatura_field.value
                )
                
                self.page.close_dialog()
                self.show_success("Controle finalizado com sucesso!")
                self.refresh_data()
                
            except ValueError:
                self.show_error("KM deve ser um número válido")
            except Exception as ex:
                self.show_error(f"Erro ao finalizar controle: {str(ex)}")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Finalizar Controle"),
            content=ft.Column([
                ft.Text(f"Veículo: {self.current_control.get('veiculo', {}).get('placa', 'N/A')}"),
                ft.Text(f"KM Inicial: {self.current_control['km_inicial']}"),
                km_final_field,
                assinatura_field
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close_dialog()),
                ft.ElevatedButton("Finalizar", on_click=finalize_control)
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def show_control_details(self, control):
        """Mostra detalhes de um controle"""
        try:
            routes = self.api_client.get_routes_by_control(control['id'])
            
            routes_info = []
            for route in routes:
                route_text = f"Saída: {route.get('data_hora_saida', 'N/A')} - KM {route.get('km_saida', 0)}"
                if route.get('data_hora_chegada'):
                    route_text += f"\nChegada: {route.get('data_hora_chegada')} - KM {route.get('km_chegada', 0)}"
                if route.get('logradouro_saida'):
                    route_text += f"\nDe: {route.get('logradouro_saida')}"
                if route.get('logradouro_chegada'):
                    route_text += f"\nPara: {route.get('logradouro_chegada')}"
                routes_info.append(ft.Text(route_text))
                routes_info.append(ft.Divider())
            
            if not routes_info:
                routes_info = [ft.Text("Nenhuma rota registrada")]
            
            dialog = ft.AlertDialog(
                title=ft.Text("Detalhes do Controle"),
                content=ft.Column([
                    ft.Text(f"Veículo: {control.get('veiculo', {}).get('placa', 'N/A')}"),
                    ft.Text(f"Início: {control.get('data_inicio', 'N/A')}"),
                    ft.Text(f"Fim: {control.get('data_fim', 'Em andamento')}"),
                    ft.Text(f"KM Inicial: {control.get('km_inicial', 0)}"),
                    ft.Text(f"KM Final: {control.get('km_final', 'N/A')}"),
                    ft.Text(f"Status: {control.get('status', 'N/A').title()}"),
                    ft.Divider(),
                    ft.Text("Rotas:", weight=ft.FontWeight.BOLD),
                    *routes_info
                ], tight=True, scroll=ft.ScrollMode.AUTO, height=400),
                actions=[
                    ft.TextButton("Fechar", on_click=lambda e: self.page.close_dialog())
                ]
            )
            
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
            
        except Exception as ex:
            self.show_error(f"Erro ao carregar detalhes: {str(ex)}")
    
    def show_error(self, message: str):
        """Mostra mensagem de erro"""
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.RED)
        )
    
    def show_success(self, message: str):
        """Mostra mensagem de sucesso"""
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.GREEN)
        )
    
    def handle_logout(self, e):
        """Processa logout do usuário"""
        self.api_client.logout()
        self.page.route = "/login"
        self.page.update()
