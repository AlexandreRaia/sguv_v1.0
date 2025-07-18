from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matricula = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    celular = Column(String)
    unidade = Column(String)
    avatar_link = Column(String)
    status = Column(String, nullable=False, default="pendente")  # pendente, ativo, inativo
    perfil = Column(String, nullable=False, default="motorista")  # admin, gestor, operador, motorista
    senha_hash = Column(String, nullable=False)
    
    # Relacionamentos
    controles = relationship("ControleUtilizacaoVeiculo", back_populates="motorista")

class Veiculo(Base):
    __tablename__ = "veiculos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    marca = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    placa = Column(String, unique=True, nullable=False, index=True)
    ano = Column(Integer)
    motor = Column(String)
    tipo = Column(String)  # Carro, Moto, Caminhão
    status = Column(String, nullable=False, default="disponivel")  # disponivel, em_uso, manutencao, inativo
    imagem_link = Column(String)
    
    # Relacionamentos
    controles = relationship("ControleUtilizacaoVeiculo", back_populates="veiculo")

class ControleUtilizacaoVeiculo(Base):
    __tablename__ = "controles_utilizacao_veiculo"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    motorista_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), nullable=False)
    data_inicio = Column(String, nullable=False)  # YYYY-MM-DD HH:MM:SS
    km_inicial = Column(Float, nullable=False)
    km_final = Column(Float)
    data_fim = Column(String)  # YYYY-MM-DD HH:MM:SS
    assinatura_eletronica = Column(String)
    status = Column(String, nullable=False, default="aberto")  # aberto, finalizado, cancelado
    
    # Relacionamentos
    motorista = relationship("Usuario", back_populates="controles")
    veiculo = relationship("Veiculo", back_populates="controles")
    rotas = relationship("Rota", back_populates="controle")

class Rota(Base):
    __tablename__ = "rotas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    controle_utilizacao_id = Column(Integer, ForeignKey("controles_utilizacao_veiculo.id"), nullable=False)
    data_hora_saida = Column(String, nullable=False)  # YYYY-MM-DD HH:MM:SS
    km_saida = Column(Float, nullable=False)
    logradouro_saida = Column(String)
    latitude_saida = Column(Float)
    longitude_saida = Column(Float)
    data_hora_chegada = Column(String)  # YYYY-MM-DD HH:MM:SS
    km_chegada = Column(Float)
    logradouro_chegada = Column(String)
    latitude_chegada = Column(Float)
    longitude_chegada = Column(Float)
    
    # Relacionamentos
    controle = relationship("ControleUtilizacaoVeiculo", back_populates="rotas")
