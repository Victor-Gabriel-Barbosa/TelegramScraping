from telethon.sync import TelegramClient
import json
from utils import extrair_promocao, baixar_imagem
from config import API_ID, API_HASH, GRUPOS, PROMOCOES_DIR

# Inicializa o cliente do Telegram
client = TelegramClient('sessao_scraper', API_ID, API_HASH)

async def main():
  print("Conectado! Iniciando a coleta de mensagens...\n")

  promocoes = {
    "produtos": [],
    "cupons": []
  }

  # Itera sobre os grupos para coletar mensagens
  for grupo in GRUPOS:
    print(f"-> Coletando mensagens de: {grupo}")
    try:
      async for mensagem in client.iter_messages(grupo, limit=10):
        # Baixa a imagem associada à mensagem
        imagem = await baixar_imagem(mensagem)
        
        # Tenta extrair a promoção
        if promo := extrair_promocao(mensagem.id, mensagem.text, imagem):
          chave, dados = promo
          promocoes[chave].append(dados)
    except Exception as e:
      print(f"Erro ao acessar o grupo {grupo}: {e}")

  # Exporta em JSON após coletar as mensagens
  with open(PROMOCOES_DIR, 'w', encoding='utf-8') as f:
    json.dump(promocoes, f, ensure_ascii=False, indent=2)

  print(f"\nExportado {len(promocoes['produtos']) + len(promocoes['cupons'])} promoções para promocoes.json")

# Inicializa o cliente em loop assíncrono
with client:
  client.loop.run_until_complete(main())