from dotenv import load_dotenv
import json
import requests
import time
import os
from rich import print
from rich.panel import Panel

# Configurações do seu Bot
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_promocoes(arquivo_json):
  # Carrega as promoções do arquivo
  with open(arquivo_json, 'r', encoding='utf-8') as f:
    promocoes = json.load(f)

  # Envia cada promoção para o Telegram
  for promo in promocoes:
    mensagem = f"<b>💥 {promo['nome']}</b>\n\n"
    
    if promo.get('preco'):
      mensagem += f"<b>💸 R$ {promo['preco']}</b>\n"
    if promo.get('preco_parcelado'):
      mensagem += f"💳 R$ {promo['preco_parcelado']} parcelado\n"
    if promo.get('valor_cupom'):
      mensagem += f"\n🔖 Cupom: R$ {promo['valor_cupom']}"
      if promo.get('limite_minimo'):
        mensagem += f" (em compras acima de R$ {promo['limite_minimo']})"
      mensagem += "\n"
        
    mensagem += f"\n<a href='{promo['link']}'>🔗 {promo['link']}</a>"

    caminho_imagem = promo.get('imagem')
    
    # Lógica para enviar com foto se o arquivo existir, ou apenas texto se não existir
    if caminho_imagem and os.path.exists(caminho_imagem):
      url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
      with open(caminho_imagem, 'rb') as photo:
        payload = {'chat_id': CHAT_ID, 'caption': mensagem, 'parse_mode': 'HTML'}
        files = {'photo': photo}
        resposta = requests.post(url, data=payload, files=files)
    else:
      url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
      payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'HTML', 'disable_web_page_preview': False}
      resposta = requests.post(url, data=payload)

    if resposta.status_code == 200:
      print(
        Panel(f"✓ Enviado: "
              f"[cyan]{promo['id']}[/] - "
              f"[white]{promo['nome'][:30]}...[/]",
              title="Mensagem Enviada",
              title_align="left",
              style="bold green")
      )
    else:
      print(
        Panel(f"✗ Erro ao enviar: "
              f"[yellow]{promo['id']}[/]: "
              f"[red]{resposta.text}[/]",
              title="Erro ao Enviar",
              title_align="left",
              style="bold red")
      )

    # Pausa de 3 segundos entre mensagens para evitar bloqueio por spam
    time.sleep(3) 

# Executa a função
if __name__ == '__main__':
  enviar_promocoes('data/promocoes.json')