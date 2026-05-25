from dotenv import load_dotenv
import os

# Informações de acesso à API do Telegram
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

GRUPOS = [
  '@SamuelF3lipePromo',
  '@BenchPromos'
]

PROMOCOES_DIR = 'data/promocoes.json'
IMGS_DIR = 'imgs'