from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os
import json
import re

# Informações de acesso à API do Telegram
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
 
# Lista de grupos para scraping
GRUPOS = [
  '@SamuelF3lipe', 
  '@BenchPromos'
]

# Extrai informações de promoção de uma mensagem
def extrair_promocao(msg_id, texto):
  # Ignora mensagens sem texto
  if not texto:
    return None
    
  # Remove linhas vazias e espaços extras
  linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
  nome = None
  alertas_ignorados = ["PARCELADO!", "BAIXOU!", "PREÇO HISTÓRICO!", "VÍDEO NOVO"]
  
  # Filtra linhas que contenham alertas ou links, e pega a primeira linha válida como nome
  for linha in linhas:
    linha_upper = linha.upper()
    if any(alerta in linha_upper for alerta in alertas_ignorados) or linha.startswith('http'):
      continue
    nome = linha
    break
     
  # Ignora mensagens que não tenham um nome válido
  if not nome:
    return None
    
  is_cupom = 'cupom' in nome.lower() or 'cupons' in nome.lower()

  # Limpa o nome do produto, removendo hashtags, preços e caracteres especiais
  nome = re.sub(r'#\w+', '', nome)
  nome = re.split(r'\s*-\s*R\$|\s+R\$', nome)[0]
  nome = re.sub(r'[^\w\s,.\-!?"\'/()+:%]', '', nome)
  nome = nome.replace('"', "'")
  nome = nome.strip(' -')
  precos = re.findall(r'R\$\s*([\d.,]+)', texto)
  
  preco = None
  preco_parcelado = None
  valor_cupom = None
  limite_minimo = None

  # Se for cupom o valor pode ser o desconto ou o preço mínimo
  if is_cupom:
    if len(precos) >= 1:
      valor_cupom = precos[0]
    
    if len(precos) >= 2:
      limite_minimo = precos[1]
        
    match_porcentagem = re.search(r'(\d+)%\s*(?:off|OFF)?', texto)
    if match_porcentagem and not valor_cupom:
      valor_cupom = f"{match_porcentagem.group(1)}%"
        
  # Se não for cupom, o valor é o preço do produto  
  else:
    if len(precos) == 1:
      preco = precos[0]
    elif len(precos) == 2:
      preco = precos[0]
      preco_parcelado = precos[1]
    elif len(precos) >= 3:
      preco = precos[1] 
      preco_parcelado = precos[2]

  # Extrai o primeiro link encontrado na mensagem
  link_match = re.search(r'https?://\S+', texto)
  link = link_match[0] if link_match else None

  # Ignora a mensagem se não tiver link ou nome/preço/cupom válido
  if not link or (not nome and not precos and not valor_cupom):
    return None

  return {
    'id': msg_id,
    'nome': nome,
    'preco': preco,
    'preco_parcelado': preco_parcelado,
    'link': link,
    'valor_cupom': valor_cupom,
    'limite_minimo': limite_minimo
  }
  
# Inicializa o cliente do Telegram
client = TelegramClient('sessao_scraper', API_ID, API_HASH)

async def main():
  print("Conectado! Iniciando a coleta de mensagens...\n")
  mensagens = []

  for group in GRUPOS:
    print(f"-> Coletando mensagens de: {group}")
    try:
      async for message in client.iter_messages(group, limit=50):
        promo = extrair_promocao(message.id, message.text)
        if promo:
          mensagens.append(promo)
    except Exception as e:
      print(f"Erro ao acessar o grupo {group}: {e}")

  # Exporta em JSON após coletar as mensagens
  with open('promocoes.json', 'w', encoding='utf-8') as f:
    json.dump(mensagens, f, ensure_ascii=False, indent=2)

  print(f"\nExportado {len(mensagens)} promoções para promocoes.json")

# Inicializa o cliente em loop assíncrono
with client:
  client.loop.run_until_complete(main())