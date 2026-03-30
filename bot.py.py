import discord
from discord.ext import commands
import ast
import operator as op
import random
import os

token = os.getenv("DISCORD_TOKEN")


ESTADO_DEFAULT = "default"
ESTADO_AGUARDANDO_NOME = "aguardando_nome"
ESTADO_BATE_PAPO = "bate_papo"
ESTADO_DESABAFO = "desabafo"

# operadores suportados para avaliação segura
OPERADORES = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg
}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

@bot.command()
async def oi(ctx):
    await ctx.send(f"Olá!, {ctx.author.mention}! Como posso ajudar?")

@bot.command()
async def falar(ctx, *, texto=None):
    if texto is None:
        await ctx.send("Por favor, forneça uma mensagem para eu falar.")
    else:
        await ctx.send(texto)

def detectar_intencoes(texto):
    intecao = {
        "cumprimento": [
            "oi", "olá", "ola", "e aí", "eai", "fala", "bom dia", "boa tarde", "boa noite"
        ],
        "ajuda": [
            "ajuda", "me ajuda", "o que você faz", "comandos", "help"
        ],
        "conversa": [
            "conversar", "bater um papo", "trocar ideia", "falar com você"
        ]
    }

    for intencao, palavras in intecao.items():
        for palavra in palavras:
            if palavra in texto:
                return intencao
    return None


RESPOSTAS_SIM = ["sim", "claro", "com certeza", "claro que sim", "é claro,", "afirmativo", "ok", "quero", "pode ser", "vamos", "de acordo"]
RESPOSTAS_NAO = ["não", "de jeito nenhum", "de forma alguma", "negativo", "jamais", "nem pensar", "de jeito nenhum", "não quero", "recuso","nao", "agora não", "depois"]
usuarios = {}
conversas = {}
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    user_id = message.author.id
    texto = message.content.lower().strip()

    if user_id not in conversas:
        conversas[user_id] = ESTADO_DEFAULT

    estado = conversas[user_id]

    # ======================
    # FLUXO DE DESABAFO
    # ======================

    if estado == ESTADO_DESABAFO:
        if any(resposta in texto for resposta in RESPOSTAS_SIM):
            await message.channel.send("Estou aqui para você ❤️\nPode falar, estou te ouvindo.")
            return

        if any(resposta in texto for resposta in RESPOSTAS_NAO):
            await message.channel.send("Tudo bem. Se mudar de ideia, estarei aqui para ouvir você.")
            conversas[user_id] = ESTADO_BATE_PAPO
            return

        await message.channel.send(
             "Entendo... isso realmente parece difícil 😔\n"
            "Quer continuar falando ou prefere um conselho?"
        )
        return
    
    # ======================
    # DETECÇÃO DE TRISTEZA
    # ======================
    palavras_tristeza = [        "triste", "mal", "cansado", "desanimado", "chateado",
        "deprimido", "pra baixo", "infeliz", "desmotivado",
        "sozinho", "solitário", "desesperançado",
        "frustrado", "desiludido", "desapontado", "abatido",]

    if any(palavra in texto for palavra in palavras_tristeza):
        await message.channel.send("Parece que você está se sentindo triste. 😞\n"
        "Quer conversar sobre isso ou prefere um conselho para se sentir melhor?")
        conversas[user_id] = ESTADO_DESABAFO
        return
    
    # ======================
    # DETECÇÃO DE FELICIDADE
    # ======================
    palavras_felicidade = ["feliz", "animado", "contente", "alegre", "satisfeito", "entusiasmado", "radiante", "eufórico", "empolgado", "otimista", "grato", "agradecido", "realizado", "orgulhoso"]
    if any(palavra in texto for palavra in palavras_felicidade):
        await message.channel.send("Fico feliz em saber que você está se sentindo bem! 😊\n"
        "Se quiser compartilhar o que está te deixando assim, estou aqui para ouvir.")
        return

    # ======================
    # INTENÇÕES
    # ======================
    intencao = detectar_intencoes(texto)

    if intencao == "cumprimento":
        if user_id in usuarios:
            nome = usuarios[user_id]["nome"]
            await message.channel.send(f"oi {nome}! Bom te ver de novo!")
        else:
            conversas[user_id] = ESTADO_AGUARDANDO_NOME
            await message.channel.send("Olá! Qual seu nome?")
        return
    
    if intencao == "ajuda":
        await message.channel.send(
            "Posso:\n"
            "• conversar com você\n"
            "• fazer cálculos (`!calc`)\n"
            "• repetir mensagens (`!falar`)"
        )
        return

    # ======================
    # AGUARDANDO NOME
    # ======================
    if estado == ESTADO_AGUARDANDO_NOME:
        nome = message.content.strip()
        usuarios[user_id] = {"nome": nome}
        conversas[user_id] = ESTADO_BATE_PAPO
        await message.channel.send(f"Prazer em te conhecer, {nome}! Como posso ajudar você hoje?")
        return

    #RESPOSTAS PRÉ-DEFINIDAS
    respostas = {
        "como você está": [
            "Estou bem, obrigado por perguntar!",
            "Tudo ótimo por aqui!",
            "Estou funcionando perfeitamente!"
        ],
        "qual é o seu nome?": [
            "Eu sou um bot criado para ajudar você!",
            "Pode me chamar de Bot!",
            "Eu sou seu assistente virtual!"
        ],
        "o que você pode fazer?": [
            "Posso responder perguntas, contar piadas e muito mais!",
            "Estou aqui para ajudar você com várias tarefas!",
            "Posso conversar, calcular expressões e entreter você!"
        ]
    }

    for chave, operacoes in respostas.items():
        if chave in texto:
            await message.channel.send(random.choice(operacoes))
            break
    
    #PROCESSA COMANDOS
    await bot.process_commands(message)

def calcular_expressao(exp):
    #avalia a expressão de forma segura
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return OPERADORES[type(node.op)](
                _eval(node.left),
                _eval(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            return OPERADORES[type(node.op)](_eval(node.operand))
        else:
            raise ValueError("Expressão inválida")
    
    return _eval(ast.parse(exp, mode='eval').body)

@bot.command()
async def calc(ctx, *, expressao: str):
    try:
        resultado = calcular_expressao(expressao)
        await ctx.send(f"O resultado de `{expressao}` é `{resultado}`")
    except ZeroDivisionError:
        await ctx.send("Erro: Divisão por zero não é permitida.")
    except Exception:
        await ctx.send("Erro: Expressão inválida.")


bot.run(token)