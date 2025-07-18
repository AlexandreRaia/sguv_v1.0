# SGUV - Sistema de Gerenciamento de Utilização de Veículos

Sistema completo para digitalização e automatização do controle de utilização de veículos, substituindo formulários físicos por uma solução moderna e eficiente.

## 📋 Visão Geral

O SGUV é um sistema que oferece:
- **API REST** desenvolvida em FastAPI para backend
- **Aplicativo móvel/desktop** desenvolvido em Flet para motoristas
- **Interface web** para administradores e gestores
- **Controle completo** de usuários, veículos, rotas e utilizações
- **Integração** com Google Maps para geolocalização
- **Relatórios** e análises de utilização

## 🚀 Funcionalidades Principais

### Para Motoristas
- ✅ Login/logout seguro
- ✅ Iniciar controle de utilização de veículo
- ✅ Adicionar rotas com geolocalização automática
- ✅ Finalizar controle com assinatura eletrônica
- ✅ Visualizar histórico de utilizações
- 🔄 Funcionamento offline (sincronização automática)

### Para Administradores
- ✅ Gerenciamento completo de usuários
- ✅ Gerenciamento de veículos
- ✅ Aprovação de novos usuários
- ✅ Visualização de todos os controles
- ✅ Relatórios e análises
- 📊 Dashboard com estatísticas

### Para Gestores/Operadores
- ✅ Visualização de controles e relatórios
- ✅ Consulta de informações
- 📋 Conferência de relatórios

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Flet (Python)
- **Autenticação**: JWT + bcrypt
- **Geolocalização**: Google Maps Geocoding API
- **Banco de Dados**: SQLite (portável e simples)

## 📦 Instalação

### 1. Clonar o Repositório
```bash
cd /home/alexandre/Documentos/Projetos/sguv
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Edite o arquivo `.env` e configure:
```env
# Configurações do JWT
SECRET_KEY=sua_chave_secreta_muito_forte_aqui_123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Maps API Key (opcional para geolocalização)
GOOGLE_MAPS_API_KEY=sua_chave_do_google_maps_api_aqui

# Configurações do Banco de Dados
DATABASE_URL=sqlite:///./sguv.db

# Configurações da Aplicação
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True
```

### 4. Executar a API
```bash
cd app
python main.py
```

A API estará disponível em: http://127.0.0.1:8000
Documentação: http://127.0.0.1:8000/docs

### 5. Executar o Aplicativo Flet
Em outro terminal:
```bash
cd flet_app
python main.py
```

## 👤 Usuário Padrão

O sistema cria automaticamente um usuário administrador:
- **Email**: admin@sguv.com
- **Senha**: admin123
- **Perfil**: Administrador

⚠️ **IMPORTANTE**: Altere a senha padrão após o primeiro login!

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

#### usuarios
- Informações dos usuários (motoristas, admins, gestores, operadores)
- Status de aprovação e perfis de acesso
- Autenticação segura com hash bcrypt

#### veiculos
- Cadastro completo da frota
- Status de disponibilidade
- Informações técnicas dos veículos

#### controles_utilizacao_veiculo
- Controle diário de utilização
- Associação motorista-veículo
- Status do controle (aberto/finalizado/cancelado)

#### rotas
- Detalhes de cada trecho percorrido
- Coordenadas GPS e endereços
- Integração com Google Maps

## 🔑 Perfis de Usuário

### Motorista
- Criar e gerenciar próprios controles
- Adicionar rotas
- Finalizar utilizações
- Visualizar histórico pessoal

### Operador
- Consultar informações
- Visualizar controles finalizados
- Acesso somente leitura

### Gestor
- Todas as funções do operador
- Acesso a relatórios
- Conferência de controles

### Administrador
- Acesso total ao sistema
- Gerenciar usuários e veículos
- Aprovar novos usuários
- Configurações do sistema

## 🌐 API Endpoints

### Autenticação
- `POST /api/users/register` - Registrar usuário
- `POST /api/users/login` - Login
- `GET /api/users/me` - Dados do usuário atual

### Usuários
- `GET /api/users/` - Listar usuários
- `PUT /api/users/{id}` - Atualizar usuário
- `PUT /api/users/{id}/activate` - Ativar usuário
- `DELETE /api/users/{id}` - Excluir usuário

### Veículos
- `GET /api/vehicles/` - Listar veículos
- `GET /api/vehicles/disponiveis` - Listar disponíveis
- `POST /api/vehicles/` - Criar veículo
- `PUT /api/vehicles/{id}` - Atualizar veículo

### Controles
- `GET /api/usage-control/` - Listar controles
- `POST /api/usage-control/` - Criar controle
- `PUT /api/usage-control/{id}/finalizar` - Finalizar

### Rotas
- `GET /api/routes/controle/{id}` - Rotas por controle
- `POST /api/routes/` - Criar rota
- `POST /api/routes/{id}/geocode-saida` - Geocodificar saída

## 🔧 Configuração do Google Maps

Para habilitar a geolocalização automática:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou selecione um existente
3. Habilite a **Geocoding API**
4. Crie uma chave de API
5. Configure a chave no arquivo `.env`:
   ```env
   GOOGLE_MAPS_API_KEY=sua_chave_aqui
   ```

## 📱 Usando o Aplicativo

### Primeiro Acesso
1. Execute a API (`python app/main.py`)
2. Execute o aplicativo (`python flet_app/main.py`)
3. Faça login com admin@sguv.com / admin123
4. Cadastre veículos e aprove usuários

### Para Motoristas
1. Registre-se no aplicativo
2. Aguarde aprovação do administrador
3. Faça login e comece a usar:
   - Iniciar novo controle
   - Adicionar rotas durante o dia
   - Finalizar ao término

## 🔄 Funcionalidade Offline

O aplicativo suporta operação offline:
- Dados são armazenados localmente
- Sincronização automática quando conectar
- Notificações de status de conexão

## 📈 Relatórios Disponíveis

- Utilização por veículo
- Utilização por motorista
- Análise de rotas
- Relatórios de desempenho
- Comparativo de quilometragem
- Exportação em CSV/PDF

## 🐛 Solução de Problemas

### API não inicia
- Verifique se a porta 8000 está livre
- Confirme as dependências instaladas
- Verifique o arquivo `.env`

### Aplicativo não conecta
- Confirme que a API está rodando
- Verifique a URL no `api_client.py`
- Teste a conectividade: http://127.0.0.1:8000/api/health

### Erro de autenticação
- Verifique email/senha
- Confirme se usuário está ativo
- Teste com usuário admin padrão

## 🚀 Próximos Passos

### Funcionalidades Planejadas
- [ ] Dashboard administrativo completo
- [ ] Relatórios avançados com gráficos
- [ ] Notificações push
- [ ] Backup automático
- [ ] API de integração externa
- [ ] App mobile nativo
- [ ] Mapa interativo de rotas

### Melhorias Técnicas
- [ ] Testes automatizados
- [ ] Docker containerization
- [ ] Deploy em produção
- [ ] Banco de dados PostgreSQL
- [ ] Cache com Redis
- [ ] Monitoramento e logs

## 📝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte:
- Abra uma issue no GitHub
- Entre em contato com a equipe de desenvolvimento

---

**SGUV - Transformando o controle de veículos para a era digital! 🚗💻**
