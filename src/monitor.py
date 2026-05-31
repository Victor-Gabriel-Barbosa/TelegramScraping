from telethon.sync import TelegramClient
from telethon import events
import asyncio
import os
import json
from utils import extrair_promocao, baixar_imagem
from config import API_ID, API_HASH, GRUPOS, PROMOCOES_DIR

# Inicializa o cliente do Telegram
client = TelegramClient('sessao_scraper', API_ID, API_HASH)

# Lock para evitar condições de corrida ao acessar o arquivo JSON
lock = asyncio.Lock()

# Evento para novas mensagens
@client.on(events.NewMessage(chats=GRUPOS))
async def nova_mensagem(event):
  mensagem = event.message
  print(f'\nNova mensagem em: {event.chat.title}')

  # Baixa a imagem associada à mensagem
  imagem = await baixar_imagem(mensagem)

  # Tenta extrair a promoção
  if not (promo := extrair_promocao(mensagem.id, mensagem.text, imagem)):
    return
  
  # Extrai o tipo (produto ou cupom) e os dados da promoção
  tipo, dados = promo
  print(json.dumps(dados, ensure_ascii=False, indent=2))

  # Carrega as promoções existentes
  async with lock:
    promocoes = {}
    if os.path.exists(PROMOCOES_DIR):
      with open(PROMOCOES_DIR, 'r', encoding='utf-8') as f:
        try:
          promocoes = json.load(f)
        except json.JSONDecodeError:
          promocoes = {"produtos": [], "cupons": []}
    else:
      promocoes = {"produtos": [], "cupons": []}

    if tipo not in promocoes:
      promocoes[tipo] = []
     
    # Adiciona a nova promoção à lista correspondente   
    promocoes[tipo].append(dados)
    
    # Salva as promoções atualizadas no arquivo JSON
    with open(PROMOCOES_DIR, 'w', encoding='utf-8') as f:
      json.dump(promocoes, f, ensure_ascii=False, indent=2)

async def main():
  print('Monitorando novas mensagens...')
  print('Pressione CTRL+C para parar.\n')
  await client.run_until_disconnected()

# Inicializa o cliente em loop assíncrono
with client:
  client.loop.run_until_complete(main())