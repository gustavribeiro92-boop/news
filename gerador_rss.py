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
    'https://sb24horas.com.br/feed/'
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
    # Novas Imagens
    'campinas': 'https://portaldosportais.com/wp-content/uploads/2026/05/download.jpg',
    'frio': 'https://portaldosportais.com/wp-content/uploads/2026/05/pexels-ammy-singh-294201421-14965455-scaled.jpg',
    'sbo': 'https://portaldosportais.com/wp-content/uploads/2026/05/images-1.jpg',
    'americana': 'https://portaldosportais.com/wp-content/uploads/2026/05/americana.jpg'
}

def categorizar_noticia(titulo, imagem_atual):
    if imagem_atual not in LOGOS_PORTAIS.values() and imagem_atual != LINK_FALLBACK_PADRAO:
        return imagem_atual

    t = titulo.lower()
    
    # 1. TEMAS CRÍTICOS (Prioridade Máxima)
    if any(p in t for p in ['gama', 'polícia', 'pm', 'preso', 'furto', 'roubo', 'acidente', 'baep', 'guarda', 'golpe']):
        return IMAGENS_CATEGORIA['policia']
    if any(p in t for p in ['câmara', 'prefeito', 'vereador', 'sardelli', 'eleição', 'projeto', 'lei', 'tce']):
        return IMAGENS_CATEGORIA['politica']
    if any(p in t for p in ['saúde', 'hospital', 'médico', 'vacina', 'dengue', 'paciente', 'ubs', 'hm']):
        return IMAGENS_CATEGORIA['saude']
    if any(p in t for p in ['dae', 'água', 'vazamento', 'abastecimento', 'esgoto']):
        return IMAGENS_CATEGORIA['dae']

    # 2. CLIMA (Frio/Geada)
    if any(p in t for p in ['frio', 'geada', 'temperatura', 'inverno', 'frente fria']):
        return IMAGENS_CATEGORIA['frio']

    # 3. OUTROS TEMAS
    if any(p in t for p in ['asfalto', 'obra', 'iluminação', 'reforma', 'praça', 'infraestrutura']):
        return IMAGENS_CATEGORIA['infraestrutura']
    if any(p in t for p in ['vagas', 'pat', 'emprego', 'indústria', 'comércio', 'economia', 'mercado', 'inflação']):
        return IMAGENS_CATEGORIA['economia']
    if any(p in t for p in ['escola', 'creche', 'educação', 'univesp', 'fatec', 'aluno', 'professor', 'enem']):
        return IMAGENS_CATEGORIA['educacao']
    if any(p in t for p in ['futebol', 'rio branco', 'campeonato', 'jogo', 'atleta', 'esporte', 'ginásio']):
        return IMAGENS_CATEGORIA['esportes']
    if any(p in t for p in ['festa', 'rodeio', 'show', 'fidam', 'evento', 'cultura', 'teatro']):
        return IMAGENS_CATEGORIA['eventos']
    if any(p in t for p in ['rodovia', 'anhanguera', 'sp-304', 'trânsito', 'pedágio', 'motorista', 'ônibus']):
        return IMAGENS_CATEGORIA['transito']

    # 4. CIDADES (Se não cair em nenhum tema específico acima)
    if 'campinas' in t:
        return IMAGENS_CATEGORIA['campinas']
    if any(p in t for p in ['santa bárbara', 'sbo']):
        return IMAGENS_CATEGORIA['sbo']
    if 'americana' in t:
        return IMAGENS_CATEGORIA['americana']
    
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
            imagem_final = categorizar_noticia(entry.title, imagem_original)

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
