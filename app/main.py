from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import create_tables, get_db
from api import users, vehicles, usage_control, routes
import crud, schemas
from auth import get_password_hash
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Criar as tabelas do banco de dados
create_tables()

app = FastAPI(
    title="Sistema de Gerenciamento de Utilização de Veículos (SGUV)",
    description="API para gerenciamento de utilização de veículos com controle de rotas e usuários",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(users.router, prefix="/api/users", tags=["Usuários"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Veículos"])
app.include_router(usage_control.router, prefix="/api/usage-control", tags=["Controle de Utilização"])
app.include_router(routes.router, prefix="/api/routes", tags=["Rotas"])

# Servir arquivos estáticos (avatares e imagens)
project_root = Path(__file__).parent.parent  # Vai para a raiz do projeto
public_dir = project_root / "public"
if not public_dir.exists():
    public_dir.mkdir(parents=True)

app.mount("/public", StaticFiles(directory=str(public_dir)), name="public")

@app.get("/")
def read_root():
    return {
        "message": "Sistema de Gerenciamento de Utilização de Veículos (SGUV)",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "SGUV API"}

@app.on_event("startup")
async def startup_event():
    """Executado quando a aplicação inicia"""
    print("🚀 SGUV API iniciada!")
    print("📖 Documentação disponível em: http://localhost:8000/docs")
    
    # Criar usuário admin padrão se não existir
    db = next(get_db())
    try:
        admin_user = crud.get_usuario_by_email(db, email="admin@sguv.com")
        if not admin_user:
            admin_data = schemas.UsuarioCreate(
                matricula="ADMIN001",
                nome="Administrador do Sistema",
                email="admin@sguv.com",
                senha="admin123",
                unidade="TI",
                status="ativo",
                perfil="admin"
            )
            crud.create_usuario(db, admin_data)
            print("👤 Usuário administrador criado:")
            print("   Email: admin@sguv.com")
            print("   Senha: admin123")
            print("   ⚠️  ALTERE A SENHA PADRÃO!")
        else:
            print("👤 Usuário administrador já existe")
            
    except Exception as e:
        print(f"❌ Erro ao criar usuário administrador: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
