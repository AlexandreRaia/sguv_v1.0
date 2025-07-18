from sqlalchemy.orm import Session
from models import Usuario, Veiculo, ControleUtilizacaoVeiculo, Rota
from schemas import (
    UsuarioCreate, UsuarioUpdate, VeiculoCreate, VeiculoUpdate,
    ControleUtilizacaoVeiculoCreate, ControleUtilizacaoVeiculoUpdate,
    RotaCreate, RotaUpdate
)
from auth import get_password_hash
from typing import List, Optional

# CRUD para Usuario
def get_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def get_usuario_by_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.email == email).first()

def get_usuario_by_matricula(db: Session, matricula: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.matricula == matricula).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    hashed_password = get_password_hash(usuario.senha)
    db_usuario = Usuario(
        matricula=usuario.matricula,
        nome=usuario.nome,
        email=usuario.email,
        celular=usuario.celular,
        unidade=usuario.unidade,
        avatar_link=usuario.avatar_link,
        status=usuario.status,
        perfil=usuario.perfil,
        senha_hash=hashed_password
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(db: Session, usuario_id: int, usuario_update: UsuarioUpdate) -> Optional[Usuario]:
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario:
        update_data = usuario_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_usuario, field, value)
        db.commit()
        db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, usuario_id: int) -> bool:
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario:
        db.delete(db_usuario)
        db.commit()
        return True
    return False

# CRUD para Veiculo
def get_veiculo(db: Session, veiculo_id: int) -> Optional[Veiculo]:
    return db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()

def get_veiculo_by_placa(db: Session, placa: str) -> Optional[Veiculo]:
    return db.query(Veiculo).filter(Veiculo.placa == placa).first()

def get_veiculos(db: Session, skip: int = 0, limit: int = 100) -> List[Veiculo]:
    return db.query(Veiculo).offset(skip).limit(limit).all()

def get_veiculos_disponiveis(db: Session) -> List[Veiculo]:
    return db.query(Veiculo).filter(Veiculo.status == "disponivel").all()

def create_veiculo(db: Session, veiculo: VeiculoCreate) -> Veiculo:
    db_veiculo = Veiculo(**veiculo.dict())
    db.add(db_veiculo)
    db.commit()
    db.refresh(db_veiculo)
    return db_veiculo

def update_veiculo(db: Session, veiculo_id: int, veiculo_update: VeiculoUpdate) -> Optional[Veiculo]:
    db_veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if db_veiculo:
        update_data = veiculo_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_veiculo, field, value)
        db.commit()
        db.refresh(db_veiculo)
    return db_veiculo

def delete_veiculo(db: Session, veiculo_id: int) -> bool:
    db_veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if db_veiculo:
        db.delete(db_veiculo)
        db.commit()
        return True
    return False

# CRUD para ControleUtilizacaoVeiculo
def get_controle(db: Session, controle_id: int) -> Optional[ControleUtilizacaoVeiculo]:
    return db.query(ControleUtilizacaoVeiculo).filter(ControleUtilizacaoVeiculo.id == controle_id).first()

def get_controles(db: Session, skip: int = 0, limit: int = 100) -> List[ControleUtilizacaoVeiculo]:
    return db.query(ControleUtilizacaoVeiculo).offset(skip).limit(limit).all()

def get_controles_by_motorista(db: Session, motorista_id: int) -> List[ControleUtilizacaoVeiculo]:
    return db.query(ControleUtilizacaoVeiculo).filter(ControleUtilizacaoVeiculo.motorista_id == motorista_id).all()

def get_controles_abertos(db: Session, motorista_id: int) -> List[ControleUtilizacaoVeiculo]:
    return db.query(ControleUtilizacaoVeiculo).filter(
        ControleUtilizacaoVeiculo.motorista_id == motorista_id,
        ControleUtilizacaoVeiculo.status == "aberto"
    ).all()

def create_controle(db: Session, controle: ControleUtilizacaoVeiculoCreate, motorista_id: int) -> ControleUtilizacaoVeiculo:
    db_controle = ControleUtilizacaoVeiculo(
        motorista_id=motorista_id,
        **controle.dict()
    )
    db.add(db_controle)
    
    # Atualizar status do veículo para "em_uso"
    veiculo = db.query(Veiculo).filter(Veiculo.id == controle.veiculo_id).first()
    if veiculo:
        veiculo.status = "em_uso"
    
    db.commit()
    db.refresh(db_controle)
    return db_controle

def update_controle(db: Session, controle_id: int, controle_update: ControleUtilizacaoVeiculoUpdate) -> Optional[ControleUtilizacaoVeiculo]:
    db_controle = db.query(ControleUtilizacaoVeiculo).filter(ControleUtilizacaoVeiculo.id == controle_id).first()
    if db_controle:
        update_data = controle_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_controle, field, value)
        
        # Se o status foi alterado para "finalizado", liberar o veículo
        if controle_update.status == "finalizado":
            veiculo = db.query(Veiculo).filter(Veiculo.id == db_controle.veiculo_id).first()
            if veiculo:
                veiculo.status = "disponivel"
        
        db.commit()
        db.refresh(db_controle)
    return db_controle

# CRUD para Rota
def get_rota(db: Session, rota_id: int) -> Optional[Rota]:
    return db.query(Rota).filter(Rota.id == rota_id).first()

def get_rotas_by_controle(db: Session, controle_id: int) -> List[Rota]:
    return db.query(Rota).filter(Rota.controle_utilizacao_id == controle_id).all()

def create_rota(db: Session, rota: RotaCreate) -> Rota:
    db_rota = Rota(**rota.dict())
    db.add(db_rota)
    db.commit()
    db.refresh(db_rota)
    return db_rota

def update_rota(db: Session, rota_id: int, rota_update: RotaUpdate) -> Optional[Rota]:
    db_rota = db.query(Rota).filter(Rota.id == rota_id).first()
    if db_rota:
        update_data = rota_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rota, field, value)
        db.commit()
        db.refresh(db_rota)
    return db_rota

def delete_rota(db: Session, rota_id: int) -> bool:
    db_rota = db.query(Rota).filter(Rota.id == rota_id).first()
    if db_rota:
        db.delete(db_rota)
        db.commit()
        return True
    return False
