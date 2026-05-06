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

def buscar_imagem(entry):
    """Busca a imagem original de forma limpa, sem forçar um logo falso"""
    
    # 1. Tenta pegar a "Featured Image" do WP
    if 'post-thumbnail' in entry:
        return entry.get('post-thumbnail')
        
    if hasattr(entry, 'media_thumbnail') and len(entry.media_thumbnail) > 0:
         return entry.media_thumbnail[0].get('url', '')

    # 2. Tenta no Media Content
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url', '')
    
    # 3. Tenta no Enclosure
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/') or link.get('rel') == 'enclosure':
                return link.get('href', '')
                
    # 4. Caça no conteúdo HTML
    if 'content' in entry and len(entry.content) > 0:
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.content[0].value)
        if match: 
            url = match.group(1)
            if "emoji" not in url and "avatar" not in url:
                return url
        
    # 5. Caça na descrição resumida
    if 'description' in entry:
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.description)
        if match: 
            url = match.group(1)
            if "emoji" not in url and "avatar" not in url:
                return url
        
    # SE NÃO ACHAR NADA, RETORNA VAZIO (Deixa o Feedzy lidar com o fallback)
    return None

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
    
    # Extrai o texto e limpa imagens quebradas que vêm de fábrica nos sites
    descricao_texto = noticia.get('description', '')
    if 'content' in noticia and len(noticia.content) > 0:
        descricao_texto = noticia.content[0].value
        
    descricao_limpa = re.sub(r'<img[^>]*>', '', descricao_texto)
    
    # SE TEM IMAGEM: Passa pelo proxy e injeta
    if imagem_original:
        url_limpa = imagem_original.replace('https://', '').replace('http://', '')
        imagem_forcada = f"https://wsrv.nl/?url={url_limpa}&w=400&h=200&fit=cover&output=jpg"
        
        fe.enclosure(imagem_forcada, '0', 'image/jpeg')
        nova_descricao = f'<img src="{imagem_forcada}" alt="Imagem" style="width:100%; max-width:400px; border-radius:8px; margin-bottom:10px;" /><br>{descricao_limpa}'
        fe.description(nova_descricao)
        
    # SE NÃO TEM IMAGEM: Envia só o texto. O WordPress vai colocar a sua foto padrão.
    else:
        fe.description(descricao_limpa)

# 5. Gera o arquivo
fg.rss_file('feed_mestre.xml')
print("Sucesso! Super Feed limpo e sem fallbacks forçados.")
