from dotenv import load_dotenv
import os

# Informações de acesso à API do Telegram
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Grupos a monitorar
GRUPOS = [
  '@SamuelF3lipePromo',
  '@BenchPromos',
  "@PoisonPromos"
]

# Diretórios para salvar dados e imagens
PROMOCOES_DIR = 'data/promocoes.json'
IMGS_DIR = 'imgs'