from telethon.sync import TelegramClient
import json
from utils import extrair_promocao
from config import API_ID, API_HASH, GRUPOS, PROMOCOES_DIR, IMGS_DIR

# Inicializa o cliente do Telegram
client = TelegramClient('sessao_scraper', API_ID, API_HASH)

async def main():
  print("Conectado! Iniciando a coleta de mensagens...\n")
  mensagens = []

  for group in GRUPOS:
    print(f"-> Coletando mensagens de: {group}")
    try:
      async for message in client.iter_messages(group, limit=20):
        imagem = None
        if message.media:
          imagem = await message.download_media(file=f'{IMGS_DIR}/{message.id}.jpg')

        if promo := extrair_promocao(message.id, message.text, imagem):
          mensagens.append(promo)
    except Exception as e:
      print(f"Erro ao acessar o grupo {group}: {e}")

  # Exporta em JSON após coletar as mensagens
  with open(PROMOCOES_DIR, 'w', encoding='utf-8') as f:
    json.dump(mensagens, f, ensure_ascii=False, indent=2)

  print(f"\nExportado {len(mensagens)} promoções para promocoes.json")

# Inicializa o cliente em loop assíncrono
with client:
  client.loop.run_until_complete(main())