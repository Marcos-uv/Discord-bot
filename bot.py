import discord
from discord.ext import commands
import ast
import operator as op
import os
from dotenv import load_dotenv
from database import conectar, salvar_usuario, salvar_mensagem, buscar_historico
from ia import gerar_resposta

# ================= CONFIG =================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    TOKEN = TOKEN.strip().strip("'\"")

# ================= INTENTS =================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= HANDLERS =================

async def handle_bate_papo(message, user_id, texto):
    historico = await buscar_historico(user_id)

    print("Chamando IA")
    
    resposta = await gerar_resposta(texto, historico)

    await message.channel.send(resposta)

# ================= EVENTO =================

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    user_id = message.author.id
    texto_original = message.content.strip()
    texto = texto_original.lower()

    # salvar no banco
    await salvar_usuario(user_id, message.author.display_name)
    await salvar_mensagem(user_id, texto_original)

    # ===== Chama a ia =====
    await handle_bate_papo(message, user_id, texto)

# ================= CALCULADORA =================

OPERADORES = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def calcular_expressao(exp):
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            return OPERADORES[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return OPERADORES[type(node.op)](_eval(node.operand))
        raise ValueError("Expressão inválida")

    return _eval(ast.parse(exp, mode="eval").body)


@bot.command()
async def calc(ctx, *, expressao: str):
    try:
        resultado = calcular_expressao(expressao)
        await ctx.send(f"Resultado: `{resultado}`")
    except:
        await ctx.send("Expressão inválida.")


@bot.command()
async def falar(ctx, *, texto=None):
    if texto:
        await ctx.send(texto)


# ================= INICIALIZAÇÃO =================
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    await conectar()


# ================= START =================

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN não definido")

bot.run(TOKEN)