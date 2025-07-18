#!/usr/bin/env python3
import sqlite3
import sys

def check_database():
    try:
        # Conectar ao banco
        conn = sqlite3.connect('app/sguv.db')
        cursor = conn.cursor()
        
        print("=== VERIFICANDO BANCO DE DADOS ===")
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tabelas encontradas: {[t[0] for t in tables]}")
        
        # Verificar estrutura da tabela usuarios
        cursor.execute("PRAGMA table_info(usuarios);")
        columns = cursor.fetchall()
        print("\n=== ESTRUTURA DA TABELA USUARIOS ===")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - Nullable: {not col[3]}")
        
        # Verificar dados do usuário ID 1
        cursor.execute("SELECT id, nome, email, avatar_link FROM usuarios WHERE id = 1;")
        user = cursor.fetchone()
        print(f"\n=== DADOS DO USUÁRIO ID 1 ===")
        if user:
            print(f"ID: {user[0]}")
            print(f"Nome: {user[1]}")
            print(f"Email: {user[2]}")
            print(f"Avatar Link: {user[3]}")
        else:
            print("Usuário ID 1 não encontrado")
        
        # Verificar todos os usuários com avatar_link
        cursor.execute("SELECT id, nome, avatar_link FROM usuarios WHERE avatar_link IS NOT NULL;")
        users_with_avatar = cursor.fetchall()
        print(f"\n=== USUÁRIOS COM AVATAR ===")
        for user in users_with_avatar:
            print(f"ID: {user[0]}, Nome: {user[1]}, Avatar: {user[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar banco: {e}")

if __name__ == "__main__":
    check_database()
