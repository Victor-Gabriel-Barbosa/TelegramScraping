import re
import os
from config import IMGS_DIR

# Formatação e limpeza de texto
RE_FORMATACAO_MD = re.compile(r'[*_~`]')
RE_QUEBRA_LINHA = re.compile(r'\n+')

# Limpeza do nome do produto
RE_HASHTAG = re.compile(r'#[^\s]+')
RE_SEPARADOR_PRECO = re.compile(r'\s*-\s*R\$|\s+R\$')
RE_CARACTERES_ESPECIAIS = re.compile(r'[^\w\s,.\-!?\'/()+:%]')
RE_ESPACOS_MULTIPLOS = re.compile(r'\s+')

# Extração de dados (preços, cupons e links)
RE_PRECO = re.compile(r'R\$\s*([\d.,]+)')
RE_PORCENTAGEM = re.compile(r'(\d+)%\s*(?i:off)?')
RE_CUPOM = re.compile(r'(?i)(?:cupom|cupons):\s*([^\n]+)')
RE_CUPOM_ALTERNATIVO = re.compile(r': \s*([^\n]+)')
RE_URL = re.compile(r'https?://\S+')

# Normaliza o texto, removendo formatações comuns do Telegram e links, para facilitar a extração de informações
def _normalizar_texto(texto):
  texto = RE_FORMATACAO_MD.sub('', texto)
  texto = RE_QUEBRA_LINHA.sub('\n', texto)
  return texto
  
# Normaliza o nome do produto, removendo hashtags, preços e caracteres indesejados
def _normalizar_nome(nome: str) -> str:
  nome = RE_HASHTAG.sub('', nome)
  nome = RE_SEPARADOR_PRECO.split(nome)[0]
  nome = RE_CARACTERES_ESPECIAIS.sub('', nome)
  nome = RE_ESPACOS_MULTIPLOS.sub(' ', nome)
  return nome.strip(' -')
  
# Extrai o nome do produto, ignorando alertas comuns e links
def _extrair_nome(texto: str) -> str | None:
  linhas = (linha.strip() for linha in texto.splitlines() if linha.strip())
  alertas_ignorados = ["parcelado!", "baixou!", "preço histórico!", "vídeo novo"]

  for linha in linhas:
    linha_lower = linha.lower()
    if any(alerta in linha_lower for alerta in alertas_ignorados):
      continue
    if 'http' in linha_lower:
      continue
    return linha
  return None

# Extrai os dados de um cupom, considerando o valor do desconto e o limite mínimo, se disponíveis
def _extrair_dados_cupom(texto: str) -> tuple[str | None, str | None]:
  precos = RE_PRECO.findall(texto)
  desconto = precos[0] if precos else None
  limite_minimo = precos[1] if len(precos) > 1 else None

  if not desconto:
    desconto = f"{match[1]}%" if (match := RE_PORCENTAGEM.search(texto)) else None
  
  return desconto, limite_minimo

# Extrai os dados de um produto, considerando o preço à vista e o preço parcelado, se disponíveis
def _extrair_dados_produto(texto: str) -> tuple[str | None, str | None]:
  precos = RE_PRECO.findall(texto)
  
  match len(precos):
    case 0:
      return None, None
    case 1:
      return precos[0], None
    case 2:
      return precos[0], precos[1]
    case _:
      return precos[1], precos[2]
    
# Extrai as informações relevantes de uma mensagem, retornando um dicionário estruturado ou None se a mensagem não for válida
def extrair_promocao(mensagem_id: int, texto: str, imagem: str | None) -> tuple[str, dict] | None:
  if not texto:
    return None

  # Normaliza o texto para facilitar a extração de informações
  texto = _normalizar_texto(texto)

  # Extrai o nome do produto, ignorando alertas comuns e links
  if not (nome_bruto := _extrair_nome(texto)):
    return None
  
  # Normaliza o nome do produto
  nome = _normalizar_nome(nome_bruto)

  # Determina se a mensagem é de um cupom
  eh_cupom = 'cupom' in nome_bruto.lower() or 'cupons' in nome_bruto.lower()

  # Extrai os dados de desconto e limite mínimo para cupons
  desconto, limite_minimo = _extrair_dados_cupom(texto) if eh_cupom else (None, None)
  
  # Extrai os dados de preço à vista e preço parcelado para produtos
  preco, preco_parcelado = (None, None) if eh_cupom else _extrair_dados_produto(texto)

  # Extrai códigos de cupom
  cupom = (match[1] if (match := RE_CUPOM.search(texto)) else None) or (match[1] if (match := RE_CUPOM_ALTERNATIVO.search(texto)) else None)

  # Extrai o primeiro link da mensagem
  link = match[0] if (match := RE_URL.search(texto)) else None

  # Ignora a mensagem se não tiver preço/cupom/desconto válido
  if not (preco or cupom or desconto):
    print(f"Mensagem ignorada:{texto[:50]}")
    return None

  if (eh_cupom):
    return "cupons", {
      'id': mensagem_id,
      'nome': nome,
      'codigo': cupom,
      'desconto': desconto,
      'limite_minimo': limite_minimo,
      'link': link,
      'imagem': imagem
    }

  return "produtos", {
    'id': mensagem_id,
    'nome': nome,
    'preco': preco,
    'preco_parcelado': preco_parcelado,
    'link': link,
    'cupom': cupom,
    'imagem': imagem
  }

# Baixa a imagem associada a uma mensagem
async def baixar_imagem(mensagem) -> str | None:
  if not mensagem.photo:
    return None
  
  os.makedirs(IMGS_DIR, exist_ok=True)
  
  return await mensagem.download_media(file=f'{IMGS_DIR}/{mensagem.id}.jpg')