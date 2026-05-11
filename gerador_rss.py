import feedparser
import re
import json
import time
import os
import email.utils
from datetime import datetime
import requests 

# ==========================================
# 1. LISTA DE FEEDS E LOGOS
# ==========================================
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
    'https://sb24horas.com.br/feed/',
    # O nosso radar espião focado em Americana!
    'https://news.google.com/rss/search?q=Americana+SP&hl=pt-BR&gl=BR&ceid=BR:pt-419'
]

LOGOS_PORTAIS = {
    'americanapost': 'https://portaldosportais.com/wp-content/uploads/2026/05/americana-post.png',
    'difusorapiracicaba': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo_font_white.svg',
    'hjnews': 'https://portaldosportais.com/wp-content/uploads/2026/05/KYiJBWc6_400x400.jpg',
    'jornalojogo': 'https://portaldosportais.com/wp-content/uploads/2026/05/O-JOGO_LOGO.png',
    'noticiadelimeira': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo.svg',
    'noticiafm': 'https://portaldosportais.com/wp-content/uploads/2026/05/LogoNoticia_2024_512x512-2.png',
    'novomomento': 'https://portaldosportais.com/wp-content/uploads/2026/05/0addff39-logo-1.png',
    'portaldeamericana': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo.avif',
    'rapidonoar': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo-rapido-no-ar-300.png',
    'redefamilia': 'https://portaldosportais.com/wp-content/uploads/2026/05/logotipo.png',
    'sb24horas': 'https://portaldosportais.com/wp-content/uploads/2026/05/images.jpg'
}

LINK_FALLBACK_PADRAO = 'https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_wk6240wk6240wk62-1.png'

# ==========================================
# 2. INTELIGÊNCIA DAS IMAGENS (CATEGORIAS + CIDADES)
# ==========================================
IMAGENS_CATEGORIA = {
    'politica': 'https://portaldosportais.com/wp-content/uploads/2026/05/Politica-scaled.jpg',
    'policia': 'https://portaldosportais.com/wp-content/uploads/2026/05/Policia.png',
    'saude': 'https://portaldosportais.com/wp-content/uploads/2026/05/saude-scaled.jpg',
    'infraestrutura': 'https://portaldosportais.com/wp-content/uploads/2026/05/infraestrutura-scaled.jpg',
    'dae': 'https://portaldosportais.com/wp-content/uploads/2026/05/dae.jpeg',
    'economia': 'https://portaldosportais.com/wp-content/uploads/2026/05/financas-scaled.jpg',
    'educacao': 'https://portaldosportais.com/wp-content/uploads/2026/05/classroom-scaled.jpg',
    'esportes': 'https://portaldosportais.com/wp-content/uploads/2026/05/esporte-scaled.jpg',
    'eventos': 'https://portaldosportais.com/wp-content/uploads/2026/05/events-scaled.jpg',
    'transito': 'https://portaldosportais.com/wp-content/uploads/2026/05/transito-scaled.jpg',
    'campinas': 'https://portaldosportais.com/wp-content/uploads/2026/05/download.jpg',
    'frio': 'https://portaldosportais.com/wp-content/uploads/2026/05/pexels-ammy-singh-294201421-14965455-scaled.jpg',
    'sbo': 'https://portaldosportais.com/wp-content/uploads/2026/05/images-1.jpg',
    'americana': 'https://portaldosportais.com/wp-content/uploads/2026/05/americana.jpg'
}

def categorizar_noticia(titulo, imagem_atual):
    t = titulo.lower()
    nova_imagem = None
    
    if any(p in t for p in ['gama', 'polícia', 'pm', 'preso', 'furto', 'roubo', 'acidente', 'baep', 'guarda', 'golpe']):
        nova_imagem = IMAGENS_CATEGORIA['policia']
    elif any(p in t for p in ['câmara', 'prefeito', 'vereador', 'sardelli', 'eleição', 'projeto', 'lei', 'tce']):
        nova_imagem = IMAGENS_CATEGORIA['politica']
    elif any(p in t for p in ['saúde', 'hospital', 'médico', 'vacina', 'dengue', 'paciente', 'ubs', 'hm', 'vacinação']):
        nova_imagem = IMAGENS_CATEGORIA['saude']
    elif any(p in t for p in ['dae', 'água', 'vazamento', 'abastecimento', 'esgoto']):
        nova_imagem = IMAGENS_CATEGORIA['dae']
    elif any(p in t for p in ['frio', 'geada', 'temperatura', 'inverno', 'frente fria']):
        nova_imagem = IMAGENS_CATEGORIA['frio']
    elif any(p in t for p in ['asfalto', 'obra', 'iluminação', 'reforma', 'praça', 'infraestrutura']):
        nova_imagem = IMAGENS_CATEGORIA['infraestrutura']
    elif any(p in t for p in ['vagas', 'pat', 'emprego', 'indústria', 'comércio', 'economia', 'mercado', 'inflação']):
        nova_imagem = IMAGENS_CATEGORIA['economia']
    elif any(p in t for p in ['escola', 'creche', 'educação', 'univesp', 'fatec', 'aluno', 'professor', 'enem']):
        nova_imagem = IMAGENS_CATEGORIA['educacao']
    elif any(p in t for p in ['futebol', 'rio branco', 'campeonato', 'jogo', 'atleta', 'esporte', 'ginásio']):
        nova_imagem = IMAGENS_CATEGORIA['esportes']
    elif any(p in t for p in ['festa', 'rodeio', 'show', 'fidam', 'evento', 'cultura', 'teatro']):
        nova_imagem = IMAGENS_CATEGORIA['eventos']
    elif any(p in t for p in ['rodovia', 'anhanguera', 'sp-304', 'trânsito', 'pedágio', 'motorista', 'ônibus']):
        nova_imagem = IMAGENS_CATEGORIA['transito']
    elif 'campinas' in t:
        nova_imagem = IMAGENS_CATEGORIA['campinas']
    elif any(p in t for p in ['santa bárbara', 'sbo']):
        nova_imagem = IMAGENS_CATEGORIA['sbo']
    elif 'americana' in t:
        nova_imagem = IMAGENS_CATEGORIA['americana']

    if not imagem_atual:
        return nova_imagem if nova_imagem else LINK_FALLBACK_PADRAO
        
    link_limpo = imagem_atual.lower()
    
    # 🚜 O TRATOR IMPLACÁVEL V2: Lista massivamente agressiva contra ficheiros camuflados
    palavras_lixo = ['logo', 'default', 'padrao', 'fallback', '0addff39', 'americana-post', 'kyijbwc6', 'o-jogo', 'images.jpg', 'images.png', 'download.jpg', 'download.png', 'cropped', 'nm-site', 'sem-foto', 'placeholder', 'blank', 'thumb', 'marca', 'capa']
    
    is_lixo = any(lixo in link_limpo for lixo in palavras_lixo)
    is_nossa_imagem_generica = any(logo.split('/')[-1].lower() in link_limpo for logo in LOGOS_PORTAIS.values())
    is_fallback = LINK_FALLBACK_PADRAO.split('/')[-1].lower() in link_limpo

    # Se tem categoria (ex: Saúde) E a foto atual for lixo ou logo: SUBSTITUI SEM PIEDADE!
    if nova_imagem and (is_lixo or is_nossa_imagem_generica or is_fallback):
        return nova_imagem
        
    # Se NÃO tem categoria, mas é lixo, mantém o lixo para não ficar o ecrã em branco
    if is_lixo or is_nossa_imagem_generica or is_fallback:
        return imagem_atual
        
    # Se chegou aqui, é porque a imagem do jornal é (teoricamente) uma FOTO REAL! Não mexe.
    return imagem_atual

# ==========================================
# 3. FUNÇÕES DE SUPORTE
# ==========================================
def nome_curto_portal(link_noticia):
    link = link_noticia.lower()
    if 'americanapost' in link: return 'Americana Post'
    if 'difusorapiracicaba' in link: return 'Difusora FM'
    if 'hjnews' in link: return 'HJ News'
    if 'jornalojogo' in link: return 'O Jogo'
    if 'noticiadelimeira' in link: return 'Notícia de Limeira'
    if 'noticiafm' in link: return 'Notícia FM'
    if 'novomomento' in link: return 'Novo Momento'
    if 'portaldeamericana' in link: return 'Portal de Americana'
    if 'rapidonoar' in link: return 'Rápido no Ar'
    if 'redefamilia' in link: return 'Rede Família'
    if 'sb24horas' in link: return 'SB24Horas'
    if 'news.google' in link: return 'Google Notícias' # Adicionado o radar da Google!
    return 'Portal RMC'

def extrair_melhor_imagem(entry, url_feed):
    candidatas = []
    if 'media_content' in entry:
        for m in entry.media_content: candidatas.append(m.get('url', ''))
    if 'media_thumbnail' in entry:
        for m in entry.media_thumbnail: candidatas.append(m.get('url', ''))
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', '') or link.get('rel') == 'enclosure':
                candidatas.append(link.get('href', ''))

    textos_html = []
    if 'summary' in entry: textos_html.append(entry.summary)
    if 'description' in entry: textos_html.append(entry.description)
    if 'content' in entry:
        for c in entry.content: textos_html.append(c.value)

    for texto in textos_html:
        matches = re.findall(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', texto, re.IGNORECASE)
        candidatas.extend(matches)

    for url in candidatas:
        if not url: continue
        url_limpa = url.strip()
        lixos = ['avatar', 'emoji', 'icon', 'logo', 'spinner', 'gravatar', 'pixel', 'wp-includes']
        if not any(lixo in url_limpa.lower() for lixo in lixos):
            return url_limpa

    url_feed_limpa = url_feed.lower().replace('.', '')
    for chave, link_logo in LOGOS_PORTAIS.items():
        if chave in url_feed_limpa:
            return link_logo
            
    return LINK_FALLBACK_PADRAO

# ==========================================
# 4. EXECUÇÃO PRINCIPAL
# ==========================================
historico_noticias = {}
if os.path.exists('feed_mestre.json'):
    try:
        with open('feed_mestre.json', 'r', encoding='utf-8') as f:
            dados_antigos = json.load(f)
            for noticia in dados_antigos:
                noticia['imagem'] = categorizar_noticia(noticia['titulo'], noticia['imagem'])
                historico_noticias[noticia['link']] = noticia
    except:
        print("Iniciando novo banco de dados...")

print("Puxando as novas notícias...")

headers_navegador = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for url in FEEDS:
    try:
        # A MÁGICA DE DISTINÇÃO DE LEITURA OCORRE AQUI:
        if 'news.google' in url:
            # Google Notícias gosta de robôs puros. Retiramos o disfarce!
            feed = feedparser.parse(url)
        else:
            # Jornais locais precisam do disfarce de Chrome para não bloquear
            resposta = requests.get(url, headers=headers_navegador, timeout=15)
            feed = feedparser.parse(resposta.content)
        
        print(f"[{nome_curto_portal(url)}] Baixou {len(feed.entries)} notícias.")
        
        for entry in feed.entries[:100]:
            link_noticia = entry.link
            
            if link_noticia in historico_noticias:
                continue
            
            data_bruta = entry.get('published', None)
            if data_bruta:
                try:
                    parsed_date = email.utils.parsedate_to_datetime(data_bruta)
                    timestamp_absoluto = parsed_date.timestamp()
                    data_formatada = parsed_date.strftime("%d/%m/%Y")
                except:
                    timestamp_absoluto = time.time()
                    data_formatada = datetime.now().strftime("%d/%m/%Y")
            elif hasattr(entry, 'published_parsed') and entry.published_parsed:
                ts_utc = time.mktime(entry.published_parsed)
                timestamp_absoluto = ts_utc
                data_formatada = datetime.fromtimestamp(ts_utc).strftime("%d/%m/%Y")
            else:
                timestamp_absoluto = time.time()
                data_formatada = datetime.now().strftime("%d/%m/%Y")
            
            imagem_original = extrair_melhor_imagem(entry, url)
            imagem_categorizada = categorizar_noticia(entry.title, imagem_original)

            # --- OTIMIZADOR DE IMAGENS ---
            todas_nossas_imagens = list(LOGOS_PORTAIS.values()) + list(IMAGENS_CATEGORIA.values()) + [LINK_FALLBACK_PADRAO]
            
            if any(nossa.split('/')[-1] in imagem_categorizada for nossa in todas_nossas_imagens):
                imagem_final = imagem_categorizada
            elif 'wsrv.nl' in imagem_categorizada:
                imagem_final = imagem_categorizada
            else:
                url_sem_http = imagem_categorizada.replace('https://', '').replace('http://', '')
                imagem_final = f"https://wsrv.nl/?url={url_sem_http}&w=400&h=200&fit=cover&output=jpg"

            historico_noticias[link_noticia] = {
                "portal": nome_curto_portal(link_noticia),
                "titulo": entry.title,
                "link": link_noticia,
                "data": data_formatada,
                "imagem": imagem_final,
                "timestamp": timestamp_absoluto
            }
    except Exception as e:
        print(f"Erro no feed {url}: {e}")

lista_final = list(historico_noticias.values())
lista_final.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
lista_final = lista_final[:1000]

with open('feed_mestre.json', 'w', encoding='utf-8') as f:
    json.dump(lista_final, f, ensure_ascii=False, indent=4)

print(f"Sucesso! Acervo atualizado com {len(lista_final)} notícias.")
