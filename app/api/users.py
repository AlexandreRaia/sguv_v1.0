from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud, schemas
from auth import verify_password, create_access_token, verify_token
from datetime import timedelta
import os
import uuid
from pathlib import Path

router = APIRouter()
security = HTTPBearer()

# Dependência para obter o usuário atual autenticado
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = verify_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_usuario_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Dependência para verificar se o usuário é admin
def get_admin_user(current_user: schemas.UsuarioResponse = Depends(get_current_user)):
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem realizar esta ação."
        )
    return current_user

@router.post("/register", response_model=schemas.UsuarioResponse)
def register_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar se email já existe
    db_user = crud.get_usuario_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Verificar se matrícula já existe
    db_user = crud.get_usuario_by_matricula(db, matricula=user.matricula)
    if db_user:
        raise HTTPException(status_code=400, detail="Matrícula já cadastrada")
    
    return crud.create_usuario(db=db, usuario=user)

@router.post("/login", response_model=schemas.Token)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_usuario_by_email(db, email=user_credentials.email)
    if not user or not verify_password(user_credentials.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "ativo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não ativado. Aguarde aprovação do administrador.",
        )
    
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UsuarioResponse)
def read_current_user(current_user: schemas.UsuarioResponse = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[schemas.UsuarioResponse])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Apenas admin e gestor podem listar usuários
    if current_user.perfil not in ["admin", "gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    return crud.get_usuarios(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.UsuarioResponse)
def read_user(
    user_id: int, 
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Usuário pode ver próprio perfil ou admin/gestor podem ver qualquer usuário
    if current_user.id != user_id and current_user.perfil not in ["admin", "gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    db_user = crud.get_usuario(db, usuario_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

@router.put("/{user_id}", response_model=schemas.UsuarioResponse)
def update_user(
    user_id: int,
    user_update: schemas.UsuarioUpdate,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Apenas admin pode editar usuários
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem editar usuários."
        )
    
    db_user = crud.update_usuario(db, usuario_id=user_id, usuario_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    admin_user: schemas.UsuarioResponse = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    success = crud.delete_usuario(db, usuario_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário excluído com sucesso"}

@router.put("/{user_id}/activate")
def activate_user(
    user_id: int,
    admin_user: schemas.UsuarioResponse = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    user_update = schemas.UsuarioUpdate(status="ativo")
    db_user = crud.update_usuario(db, usuario_id=user_id, usuario_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário ativado com sucesso"}

@router.put("/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    admin_user: schemas.UsuarioResponse = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    user_update = schemas.UsuarioUpdate(status="inativo")
    db_user = crud.update_usuario(db, usuario_id=user_id, usuario_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário desativado com sucesso"}

@router.post("/{user_id}/avatar")
async def upload_avatar(
    user_id: int,
    avatar: UploadFile = File(...),
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar se o usuário existe
    db_user = crud.get_usuario(db, usuario_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se o usuário atual pode alterar este avatar
    if current_user.id != user_id and current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar seu próprio avatar"
        )
    
    # Verificar se é uma imagem válida
    valid_content_types = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"]
    if avatar.content_type not in valid_content_types:
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo não suportado. Use: JPEG, PNG, GIF, BMP ou WebP"
        )
    
    # Verificar tamanho do arquivo (máximo 5MB)
    if avatar.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 5MB")
    
    try:
        # Criar diretório se não existir - usar caminho absoluto
        project_root = Path(__file__).parent.parent.parent  # Vai para a raiz do projeto (3 níveis acima)
        avatar_dir = project_root / "public" / "avatar"
        avatar_dir.mkdir(parents=True, exist_ok=True)
        
        # Deletar avatar anterior se existir
        if db_user.avatar_link:
            if db_user.avatar_link.startswith('public/'):
                old_avatar_path = project_root / db_user.avatar_link
            else:
                old_avatar_path = Path(db_user.avatar_link)
            if old_avatar_path.exists():
                old_avatar_path.unlink()
        
        # Gerar nome único para o arquivo
        file_extension = Path(avatar.filename).suffix
        unique_filename = f"{user_id}_{uuid.uuid4()}{file_extension}"
        avatar_path = avatar_dir / unique_filename
        
        # Salvar arquivo
        with open(avatar_path, "wb") as buffer:
            content = await avatar.read()
            buffer.write(content)
        
        # Atualizar banco de dados - salvar caminho relativo
        relative_path = f"public/avatar/{unique_filename}"
        user_update = schemas.UsuarioUpdate(avatar_link=relative_path)
        updated_user = crud.update_usuario(db, usuario_id=user_id, usuario_update=user_update)
        
        return {
            "success": True,
            "message": "Avatar atualizado com sucesso",
            "data": {
                "avatar_link": relative_path
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload do avatar: {str(e)}")

@router.delete("/{user_id}/avatar")
async def delete_avatar(
    user_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar se o usuário existe
    db_user = crud.get_usuario(db, usuario_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar permissões
    if current_user.id != user_id and current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode remover seu próprio avatar"
        )
    
    try:
        # Deletar arquivo do sistema
        if db_user.avatar_link:
            project_root = Path(__file__).parent.parent.parent
            if db_user.avatar_link.startswith('public/'):
                avatar_path = project_root / db_user.avatar_link
            else:
                avatar_path = Path(db_user.avatar_link)
            if avatar_path.exists():
                avatar_path.unlink()
        
        # Atualizar banco de dados
        user_update = schemas.UsuarioUpdate(avatar_link=None)
        crud.update_usuario(db, usuario_id=user_id, usuario_update=user_update)
        
        return {
            "success": True,
            "message": "Avatar removido com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover avatar: {str(e)}")
