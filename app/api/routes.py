from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud, schemas
from api.users import get_current_user
from services.google_maps import google_maps_service
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=schemas.RotaResponse)
def create_route(
    route: schemas.RotaCreate,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar se o controle de utilização existe e pertence ao usuário
    db_control = crud.get_controle(db, controle_id=route.controle_utilizacao_id)
    if not db_control:
        raise HTTPException(status_code=404, detail="Controle de utilização não encontrado")
    
    # Apenas o motorista responsável pode adicionar rotas ao seu controle
    if db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o motorista responsável pode adicionar rotas"
        )
    
    if db_control.status != "aberto":
        raise HTTPException(status_code=400, detail="Não é possível adicionar rotas a um controle finalizado ou cancelado")
    
    return crud.create_rota(db=db, rota=route)

@router.get("/controle/{control_id}", response_model=List[schemas.RotaResponse])
def read_routes_by_control(
    control_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar se o controle existe
    db_control = crud.get_controle(db, controle_id=control_id)
    if not db_control:
        raise HTTPException(status_code=404, detail="Controle de utilização não encontrado")
    
    # Motoristas só podem ver rotas de seus próprios controles
    if current_user.perfil == "motorista" and db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    return crud.get_rotas_by_controle(db, controle_id=control_id)

@router.get("/{route_id}", response_model=schemas.RotaResponse)
def read_route(
    route_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_route = crud.get_rota(db, rota_id=route_id)
    if db_route is None:
        raise HTTPException(status_code=404, detail="Rota não encontrada")
    
    # Verificar permissões através do controle
    db_control = crud.get_controle(db, controle_id=db_route.controle_utilizacao_id)
    if current_user.perfil == "motorista" and db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    return db_route

@router.put("/{route_id}", response_model=schemas.RotaResponse)
def update_route(
    route_id: int,
    route_update: schemas.RotaUpdate,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_route = crud.get_rota(db, rota_id=route_id)
    if db_route is None:
        raise HTTPException(status_code=404, detail="Rota não encontrada")
    
    # Verificar permissões através do controle
    db_control = crud.get_controle(db, controle_id=db_route.controle_utilizacao_id)
    if db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o motorista responsável pode editar a rota"
        )
    
    if db_control.status != "aberto":
        raise HTTPException(status_code=400, detail="Não é possível editar rotas de um controle finalizado ou cancelado")
    
    return crud.update_rota(db, rota_id=route_id, rota_update=route_update)

@router.delete("/{route_id}")
def delete_route(
    route_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_route = crud.get_rota(db, rota_id=route_id)
    if db_route is None:
        raise HTTPException(status_code=404, detail="Rota não encontrada")
    
    # Verificar permissões através do controle
    db_control = crud.get_controle(db, controle_id=db_route.controle_utilizacao_id)
    if current_user.perfil != "admin" and db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    if db_control.status != "aberto" and current_user.perfil != "admin":
        raise HTTPException(status_code=400, detail="Não é possível excluir rotas de um controle finalizado ou cancelado")
    
    success = crud.delete_rota(db, rota_id=route_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rota não encontrada")
    return {"message": "Rota excluída com sucesso"}

@router.post("/{route_id}/geocode-saida")
def geocode_departure(
    route_id: int,
    latitude: float,
    longitude: float,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter endereço a partir das coordenadas de saída"""
    db_route = crud.get_rota(db, rota_id=route_id)
    if db_route is None:
        raise HTTPException(status_code=404, detail="Rota não encontrada")
    
    # Verificar permissões
    db_control = crud.get_controle(db, controle_id=db_route.controle_utilizacao_id)
    if db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Obter endereço usando Google Maps
    address = google_maps_service.get_address_from_coordinates(latitude, longitude)
    
    if address:
        # Atualizar rota com os dados de geolocalização
        route_update = schemas.RotaUpdate(
            latitude_saida=latitude,
            longitude_saida=longitude,
            logradouro_saida=address
        )
        crud.update_rota(db, rota_id=route_id, rota_update=route_update)
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "address": address
        }
    else:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "address": None,
            "error": "Não foi possível obter o endereço para as coordenadas fornecidas"
        }

@router.post("/{route_id}/geocode-chegada")
def geocode_arrival(
    route_id: int,
    latitude: float,
    longitude: float,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter endereço a partir das coordenadas de chegada"""
    db_route = crud.get_rota(db, rota_id=route_id)
    if db_route is None:
        raise HTTPException(status_code=404, detail="Rota não encontrada")
    
    # Verificar permissões
    db_control = crud.get_controle(db, controle_id=db_route.controle_utilizacao_id)
    if db_control.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Obter endereço usando Google Maps
    address = google_maps_service.get_address_from_coordinates(latitude, longitude)
    
    if address:
        # Atualizar rota com os dados de geolocalização
        route_update = schemas.RotaUpdate(
            latitude_chegada=latitude,
            longitude_chegada=longitude,
            logradouro_chegada=address
        )
        crud.update_rota(db, rota_id=route_id, rota_update=route_update)
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "address": address
        }
    else:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "address": None,
            "error": "Não foi possível obter o endereço para as coordenadas fornecidas"
        }
