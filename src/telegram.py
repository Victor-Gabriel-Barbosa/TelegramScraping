import json
import requests
import time
import os
from config import TOKEN, CHAT_ID

def enviar_promocoes(arquivo_json):
  # Carrega as promoções do arquivo JSON
  with open(arquivo_json, 'r', encoding='utf-8') as f:
    promocoes = json.load(f)

  # Separa e junta os itens
  produtos = promocoes.get('produtos', [])
  cupons = promocoes.get('cupons', [])
  itens = produtos + cupons

  # Envia cada promoção para o Telegram
  for promo in itens:
    mensagem = f"<b>💥 {promo.get('nome', 'Oferta')}</b>\n\n"

    # Formatação para produtos
    if 'preco' in promo:
      if promo.get('preco'):
        mensagem += f"<b>💸 R$ {promo['preco']}</b>\n"
      if promo.get('preco_parcelado'):
        mensagem += f"💳 R$ {promo['preco_parcelado']} parcelado\n"
      if promo.get('cupom'):
        mensagem += f"\n🔖 Cupom: {promo['cupom']}\n"

    # Formatação para cupons
    elif 'codigo' in promo:
      if promo.get('codigo'):
        mensagem += f"🎟️ Código: <b>{promo['codigo']}</b>\n"
      if promo.get('desconto'):
        mensagem += f"💸 Desconto: R$ {promo['desconto']}\n"
      if promo.get('limite_minimo'):
        mensagem += f"🛑 Em compras acima de R$ {promo['limite_minimo']}\n"
        
    # Adiciona o link ao final
    if promo.get('link'):
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

    # Feedback no terminal
    if resposta.status_code == 200:
      print(f"✓ Enviado: {promo.get('id', 'N/A')} - {promo.get('nome', '')[:30]}...")
    else:
      print(f"✗ Erro ao enviar: {promo.get('id', 'N/A')}: {resposta.text}")

    # Pausa de 3 segundos para evitar bloqueio por spam
    time.sleep(3) 

# Executa a função
if __name__ == '__main__':
  enviar_promocoes('data/promocoes.json')