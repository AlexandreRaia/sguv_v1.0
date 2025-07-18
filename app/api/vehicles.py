from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud, schemas
from api.users import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.VeiculoResponse)
def create_vehicle(
    vehicle: schemas.VeiculoCreate,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Apenas admin pode criar veículos
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem criar veículos."
        )
    
    # Verificar se placa já existe
    db_vehicle = crud.get_veiculo_by_placa(db, placa=vehicle.placa)
    if db_vehicle:
        raise HTTPException(status_code=400, detail="Placa já cadastrada")
    
    return crud.create_veiculo(db=db, veiculo=vehicle)

@router.get("/", response_model=List[schemas.VeiculoResponse])
def read_vehicles(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_veiculos(db, skip=skip, limit=limit)

@router.get("/disponiveis", response_model=List[schemas.VeiculoResponse])
def read_available_vehicles(
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_veiculos_disponiveis(db)

@router.get("/{vehicle_id}", response_model=schemas.VeiculoResponse)
def read_vehicle(
    vehicle_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_vehicle = crud.get_veiculo(db, veiculo_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return db_vehicle

@router.put("/{vehicle_id}", response_model=schemas.VeiculoResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_update: schemas.VeiculoUpdate,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Apenas admin pode editar veículos
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem editar veículos."
        )
    
    db_vehicle = crud.update_veiculo(db, veiculo_id=vehicle_id, veiculo_update=vehicle_update)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return db_vehicle

@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Apenas admin pode excluir veículos
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem excluir veículos."
        )
    
    success = crud.delete_veiculo(db, veiculo_id=vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return {"message": "Veículo excluído com sucesso"}
