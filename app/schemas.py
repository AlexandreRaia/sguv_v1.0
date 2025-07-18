from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Schemas para Usuario
class UsuarioBase(BaseModel):
    matricula: str
    nome: str
    email: str
    celular: Optional[str] = None
    unidade: Optional[str] = None
    avatar_link: Optional[str] = None
    status: str = "pendente"
    perfil: str = "motorista"

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioUpdate(BaseModel):
    matricula: Optional[str] = None
    nome: Optional[str] = None
    email: Optional[str] = None
    celular: Optional[str] = None
    unidade: Optional[str] = None
    avatar_link: Optional[str] = None
    status: Optional[str] = None
    perfil: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas para Veiculo
class VeiculoBase(BaseModel):
    marca: str
    modelo: str
    placa: str
    ano: Optional[int] = None
    motor: Optional[str] = None
    tipo: Optional[str] = None
    status: str = "disponivel"
    imagem_link: Optional[str] = None

class VeiculoCreate(VeiculoBase):
    pass

class VeiculoUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    placa: Optional[str] = None
    ano: Optional[int] = None
    motor: Optional[str] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    imagem_link: Optional[str] = None

class VeiculoResponse(VeiculoBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas para Rota
class RotaBase(BaseModel):
    data_hora_saida: str
    km_saida: float
    logradouro_saida: Optional[str] = None
    latitude_saida: Optional[float] = None
    longitude_saida: Optional[float] = None
    data_hora_chegada: Optional[str] = None
    km_chegada: Optional[float] = None
    logradouro_chegada: Optional[str] = None
    latitude_chegada: Optional[float] = None
    longitude_chegada: Optional[float] = None

class RotaCreate(RotaBase):
    controle_utilizacao_id: int

class RotaUpdate(BaseModel):
    data_hora_saida: Optional[str] = None
    km_saida: Optional[float] = None
    logradouro_saida: Optional[str] = None
    latitude_saida: Optional[float] = None
    longitude_saida: Optional[float] = None
    data_hora_chegada: Optional[str] = None
    km_chegada: Optional[float] = None
    logradouro_chegada: Optional[str] = None
    latitude_chegada: Optional[float] = None
    longitude_chegada: Optional[float] = None

class RotaResponse(RotaBase):
    id: int
    controle_utilizacao_id: int
    
    class Config:
        from_attributes = True

# Schemas para ControleUtilizacaoVeiculo
class ControleUtilizacaoVeiculoBase(BaseModel):
    veiculo_id: int
    data_inicio: str
    km_inicial: float
    km_final: Optional[float] = None
    data_fim: Optional[str] = None
    assinatura_eletronica: Optional[str] = None
    status: str = "aberto"

class ControleUtilizacaoVeiculoCreate(ControleUtilizacaoVeiculoBase):
    pass

class ControleUtilizacaoVeiculoUpdate(BaseModel):
    km_final: Optional[float] = None
    data_fim: Optional[str] = None
    assinatura_eletronica: Optional[str] = None
    status: Optional[str] = None

class ControleUtilizacaoVeiculoResponse(ControleUtilizacaoVeiculoBase):
    id: int
    motorista_id: int
    motorista: UsuarioResponse
    veiculo: VeiculoResponse
    rotas: List[RotaResponse] = []
    
    class Config:
        from_attributes = True

# Schemas para Autenticação
class UserLogin(BaseModel):
    email: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
