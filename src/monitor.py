from telethon.sync import TelegramClient
from telethon import events
import os
import json
from .utils import extrair_promocao
from .config import API_ID, API_HASH, GRUPOS, PROMOCOES_DIR, IMGS_DIR

# Inicializa o cliente do Telegram
client = TelegramClient('sessao_scraper', API_ID, API_HASH)

# Evento para novas mensagens
@client.on(events.NewMessage(chats=GRUPOS))
async def nova_mensagem(event):
  message = event.message

  print(f'\nNova mensagem em: {event.chat.title}')

  imagem = None

  # Baixa a imagem se a mensagem tiver mídia
  if message.media:
    os.makedirs(IMGS_DIR, exist_ok=True)

    imagem = await message.download_media(
      file=f'{IMGS_DIR}/{message.id}.jpg'
    )

  # Extrai as informações da mensagem
  promo = extrair_promocao(
    message.id,
    message.text,
    imagem
  )

  # Ignora mensagens que não contêm promoções válidas
  if not promo:
    return

  print(json.dumps(
    promo,
    ensure_ascii=False,
    indent=2
  ))

  promocoes = []

  # Carrega as promoções existentes, se o arquivo existir
  if os.path.exists(PROMOCOES_DIR):
    with open(PROMOCOES_DIR, 'r', encoding='utf-8') as f:
      promocoes = json.load(f)

  # Adiciona a nova promoção à lista
  promocoes.append(promo)
  with open(PROMOCOES_DIR, 'w', encoding='utf-8') as f:
    json.dump(
      promocoes,
      f,
      ensure_ascii=False,
      indent=2
    )


async def main():
  print('Monitorando novas mensagens...')
  print('Pressione CTRL+C para parar.\n')

  await client.run_until_disconnected()

# Inicializa o cliente em loop assíncrono
with client:
  client.loop.run_until_complete(main())