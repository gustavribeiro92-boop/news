import feedparser
from feedgen.feed import FeedGenerator
import re
from datetime import datetime

# 1. Lista de Feeds
FEEDS = [
    'https://americanapost.com.br/feed/',
    'https://difusorapiracicaba.com.br/feed/',
    'https://hjnews.com.br/feed/',
    'https://jornalojogo.com.br/feed/',
    'https://noticiadelimeira.com.br/feed/',
    'https://noticiafm.com.br/feed/',
    'https://novomomento.com.br/feed/',
    'https://portaldeamericana.com/feed/',
    'https://rapidonoar.com.br/feed/',
    'https://redefamilia.com.br/feed/',
    'https://sb24horas.com.br/feed/'
]

LINK_FALLBACK = 'https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_wk6240wk6240wk62-1.png'

def buscar_imagem(entry):
    """Buscador blindado: escaneia qualquer link de imagem (jpg/png) dentro da notícia"""
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url', '')
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/') or link.get('rel') == 'enclosure':
                return link.get('href', '')
    
    # A MÁGICA AQUI: Encontra qualquer URL que termine com formato de imagem, ignorando o HTML bagunçado
    padrao_img = r'(https?://[^\s"<>\']+?\.(?:jpg|jpeg|png|gif|webp))'
    
    if 'content' in entry and len(entry.content) > 0:
        match = re.search(padrao_img, entry.content[0].value, re.IGNORECASE)
        if match: return match.group(1)
        
    if 'description' in entry:
        match = re.search(padrao_img, entry.description, re.IGNORECASE)
        if match: return match.group(1)
        
    # Só usa o logo se realmente não existir menção a nenhuma foto
    return LINK_FALLBACK

# 2. Configuração do Super Feed
fg = FeedGenerator()
fg.title('Hub de Notícias RMC')
fg.link(href='https://seusite.com.br', rel='alternate')
fg.description('Agregador de notícias da região')
fg.language('pt-br')

todas_noticias = []

print("Puxando as notícias...")
for url in FEEDS:
    try:
        feed = feedparser.parse(url)
        nome_portal = feed.feed.title if 'title' in feed.feed else "Portal"
        
        for entry in feed.entries[:10]:
            entry.portal_origem = nome_portal
            todas_noticias.append(entry)
    except Exception as e:
        print(f"Erro no feed {url}: {e}")

# 3. Ordenar pelas mais recentes
def extrair_data(entry):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return entry.published_parsed
    return datetime.now().timetuple()

todas_noticias.sort(key=extrair_data, reverse=True)

# 4. Monta o arquivo XML final
for noticia in todas_noticias[:50]:
    fe = fg.add_entry()
    fe.title(f"[{noticia.portal_origem}] {noticia.title}")
    fe.link(href=noticia.link)
    
    imagem_original = buscar_imagem(noticia)
    descricao_texto = noticia.get('description', '')
    
    # Limpa as imagens velhas/quebradas do texto para não duplicar no site
    descricao_limpa = re.sub(r'<img[^>]*>', '', descricao_texto)
    
    if imagem_original == LINK_FALLBACK:
        imagem_forcada = LINK_FALLBACK
    else:
        # Passa pelo proxy para quebrar bloqueios
        url_limpa = imagem_original.replace('https://', '').replace('http://', '')
        imagem_forcada = f"https://wsrv.nl/?url={url_limpa}&w=400&h=200&fit=cover&output=jpg"
    
    # Envia pro WordPress de duas formas (garantia dupla)
    fe.enclosure(imagem_forcada, '0', 'image/jpeg')
    nova_descricao = f'<img src="{imagem_forcada}" alt="Imagem" style="width:100%; max-width:400px; border-radius:8px; margin-bottom:10px;" /><br>{descricao_limpa}'
    fe.description(nova_descricao)

# 5. Gera o arquivo
fg.rss_file('feed_mestre.xml')
print("Sucesso! Super Feed atualizado.")
