import re

# Extrai o nome do produto, ignorando alertas comuns e links
def _extrair_nome_produto(texto: str) -> str | None:
  linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
  alertas_ignorados = ["PARCELADO!", "BAIXOU!", "PREÇO HISTÓRICO!", "VÍDEO NOVO"]

  for linha in linhas:
    linha_upper = linha.upper()
    if any(alerta in linha_upper for alerta in alertas_ignorados):
      continue
    if linha.startswith('http'):
      continue
    return linha
  return None

# Normaliza o nome do produto, removendo hashtags, preços e caracteres indesejados
def _normalizar_nome(nome: str) -> str:
  nome = nome.replace('"', "'")
  nome = re.sub(r'#\w+', '', nome)
  nome = re.split(r'\s*-\s*R\$|\s+R\$', nome)[0]
  nome = re.sub(r'[^\w\s,.\-!?\'/()+:%]', '', nome)
  nome = re.sub(r'\s{2,}', ' ', nome)
  return nome.strip(' -')

# Extrai preços e informações de cupom do texto, diferenciando entre promoções normais e cupons
def _extrair_precos_cupom(texto: str, is_cupom: bool):
  precos = re.findall(r'R\$\s*([\d.,]+)', texto)
  preco = None
  preco_parcelado = None
  valor_cupom = None
  limite_minimo = None

  if is_cupom:
    if precos:
      valor_cupom = precos[0]
    if len(precos) > 1:
      limite_minimo = precos[1]

    match_porcentagem = re.search(r'(\d+)%\s*(?:off|OFF)?', texto)
    if match_porcentagem and not valor_cupom:
      valor_cupom = f"{match_porcentagem[1]}%"
      
  elif len(precos) == 1:
    preco = precos[0]
  elif len(precos) == 2:
    preco = precos[0]
    preco_parcelado = precos[1]
  elif len(precos) >= 3:
    preco = precos[1]
    preco_parcelado = precos[2]

  return precos, preco, preco_parcelado, valor_cupom, limite_minimo

# Extrai as informações relevantes de uma mensagem, retornando um dicionário estruturado ou None se a mensagem não for válida
def extrair_promocao(mensagem_id, texto, imagem):
  # Ignora mensagens sem texto
  if not texto:
    return None

  # Extrai o nome do produto, ignorando alertas comuns e links
  nome_bruto = _extrair_nome_produto(texto)
  if not nome_bruto:
    return None

  is_cupom = 'cupom' in nome_bruto.lower() or 'cupons' in nome_bruto.lower()
  nome = _normalizar_nome(nome_bruto)

  # Extrai preços e informações de cupom do texto
  precos, preco, preco_parcelado, valor_cupom, limite_minimo = _extrair_precos_cupom(
    texto, is_cupom
  )

  # Extrai códigos de cupom, normalizando para remover caracteres indesejados
  codigos_cupom = re.findall(r'(?i)cupom:\s*(\S+)', texto)
  codigos_cupom = [
    re.sub(r'[^A-Z0-9_-]', '', cupom, flags=re.I)
    for cupom in codigos_cupom
  ]

  # Extrai o primeiro link da mensagem
  link_match = re.search(r'https?://\S+', texto)
  link = link_match[0] if link_match else None

  # Ignora a mensagem se não tiver link/nome/preço/cupom válido
  if not (link or nome or precos or valor_cupom):
    return None

  return {
    'id': mensagem_id,
    'nome': nome,
    'preco': preco,
    'preco_parcelado': preco_parcelado,
    'link': link,
    'codigos_cupom': codigos_cupom,
    'valor_cupom': valor_cupom,
    'limite_minimo': limite_minimo,
    'imagem': imagem
  }