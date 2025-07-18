from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud, schemas
from api.users import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=schemas.ControleUtilizacaoVeiculoResponse)
def create_usage_control(
    control: schemas.ControleUtilizacaoVeiculoCreate,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar se o veículo existe e está disponível
    vehicle = crud.get_veiculo(db, veiculo_id=control.veiculo_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    if vehicle.status != "disponivel":
        raise HTTPException(status_code=400, detail="Veículo não está disponível")
    
    # Verificar se o motorista não tem controles em aberto
    controles_abertos = crud.get_controles_abertos(db, motorista_id=current_user.id)
    if controles_abertos:
        raise HTTPException(
            status_code=400, 
            detail="Você já possui um controle de utilização em aberto. Finalize-o antes de iniciar outro."
        )
    
    return crud.create_controle(db=db, controle=control, motorista_id=current_user.id)

@router.get("/", response_model=List[schemas.ControleUtilizacaoVeiculoResponse])
def read_usage_controls(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Motoristas só veem seus próprios controles
    if current_user.perfil == "motorista":
        return crud.get_controles_by_motorista(db, motorista_id=current_user.id)
    
    # Admin, gestor e operador veem todos
    return crud.get_controles(db, skip=skip, limit=limit)

@router.get("/meus", response_model=List[schemas.ControleUtilizacaoVeiculoResponse])
def read_my_usage_controls(
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_controles_by_motorista(db, motorista_id=current_user.id)

@router.get("/abertos", response_model=List[schemas.ControleUtilizacaoVeiculoResponse])
def read_open_usage_controls(
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Motoristas só veem seus próprios controles abertos
    if current_user.perfil == "motorista":
        return crud.get_controles_abertos(db, motorista_id=current_user.id)
    
    # Admin, gestor e operador veem todos os controles abertos
    # (implementar função no CRUD se necessário)
    return crud.get_controles_abertos(db, motorista_id=None)

@router.get("/{control_id}", response_model=schemas.ControleUtilizacaoVeiculoResponse)
def read_usage_control(
    control_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_control = crud.get_controle(db, controle_id=control_id)
    if db_control is None:
        raise HTTPException(status_code=404, detail="Controle de utilização não encontrado")
    
    # Motoristas só podem ver seus próprios controles
    if current_user.perfil == "motorista" and db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    return db_control

@router.put("/{control_id}/finalizar", response_model=schemas.ControleUtilizacaoVeiculoResponse)
def finalize_usage_control(
    control_id: int,
    finalization_data: schemas.ControleUtilizacaoVeiculoUpdate,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_control = crud.get_controle(db, controle_id=control_id)
    if db_control is None:
        raise HTTPException(status_code=404, detail="Controle de utilização não encontrado")
    
    # Apenas o próprio motorista pode finalizar seu controle
    if db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o motorista responsável pode finalizar o controle"
        )
    
    if db_control.status != "aberto":
        raise HTTPException(status_code=400, detail="Controle já foi finalizado ou cancelado")
    
    # Validar dados de finalização
    if not finalization_data.km_final:
        raise HTTPException(status_code=400, detail="Quilometragem final é obrigatória")
    
    if finalization_data.km_final <= db_control.km_inicial:
        raise HTTPException(status_code=400, detail="Quilometragem final deve ser maior que a inicial")
    
    # Adicionar data/hora de finalização se não fornecida
    if not finalization_data.data_fim:
        finalization_data.data_fim = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Marcar como finalizado
    finalization_data.status = "finalizado"
    
    return crud.update_controle(db, controle_id=control_id, controle_update=finalization_data)

@router.put("/{control_id}/cancelar")
def cancel_usage_control(
    control_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_control = crud.get_controle(db, controle_id=control_id)
    if db_control is None:
        raise HTTPException(status_code=404, detail="Controle de utilização não encontrado")
    
    # Apenas o próprio motorista ou admin pode cancelar
    if current_user.perfil != "admin" and db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    if db_control.status != "aberto":
        raise HTTPException(status_code=400, detail="Apenas controles em aberto podem ser cancelados")
    
    # Cancelar controle
    control_update = schemas.ControleUtilizacaoVeiculoUpdate(status="cancelado")
    crud.update_controle(db, controle_id=control_id, controle_update=control_update)
    
    return {"message": "Controle de utilização cancelado com sucesso"}
