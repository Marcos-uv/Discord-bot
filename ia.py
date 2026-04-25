import httpx
import os
from dotenv import load_dotenv

# ================= CONFIG =================
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

async def gerar_resposta(mensagem, historico):
    messages = [
        {
            "role": "system", 
            "content": "Você é um assistente amigável e natural."
        }
    ]

    # Adiciona o histórico das mensagens anteriores
    for msg in historico[-5:]:  # Pega as últimas 5 mensagens
        if isinstance(msg, str) and msg.strip():
            messages.append({
                "role": "user", 
                "content": msg.strip()
            })

    # Adiciona a mensagem atual
    messages.append({"role": "user", "content": mensagem.strip()})

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "Discord Bot"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7
            }
        )
    
    if response.status_code != 200:
        print("ERRO API:", response.text)
        return f"Erro API: {response.text}"

    data = response.json()

    print("Resposta da IA:", data)  # DEBUG

    # Se a API retornou erro
    if "error" in data:
        return f"Erro da IA: {data['error'].get('message', data['error'])}"

    # Se não veio no formato esperado
    if "choices" not in data:
        return f"Resposta inesperada da API: {data}"

    # Se veio vazio
    if not data["choices"]:
        return "A IA não retornou nenhuma resposta."

    return data["choices"][0]["message"]["content"]