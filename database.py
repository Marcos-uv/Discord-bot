import asyncpg
import os
from dotenv import load_dotenv

# ================= CONFIG =================

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

pool = None

async def conectar():
    global pool
    pool = await asyncpg.create_pool(DB_URL)

async def salvar_usuario(user_id, nome):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO usuarios (id, nome)
            VALUES ($1, $2)
            ON CONFLICT (id) DO UPDATE SET nome = $2
        """, user_id, nome)

async def salvar_mensagem(user_id, mensagem):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO mensagens (user_id, mensagem)
            VALUES ($1, $2)
        """, user_id, mensagem)

async def buscar_historico(user_id, limite=5):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT mensagem
            FROM mensagens
            WHERE user_id = $1
            ORDER BY criado_em DESC
            LIMIT $2
        """, user_id, limite)

        return [r["mensagem"] for r in rows]