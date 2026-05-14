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
'https://news.google.com/rss/search?q=Americana+SP&hl=pt-BR&gl=BR&ceid=BR:pt-419',
'https://vagas019.com.br/feed/'
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
'sb24horas': 'https://portaldosportais.com/wp-content/uploads/2026/05/images.jpg',
    'vagas019': 'https://vagas019.com.br/wp-content/uploads/2025/10/cropped-logo-vagas019-32x32.png'
    # ATUALIZADO: Novo logo em alta qualidade
    'vagas019': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo-vagas0192.webp'
}

LINK_FALLBACK_PADRAO = 'https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_wk6240wk6240wk62-1.png'

# ==========================================
# 2. INTELIGÊNCIA DAS IMAGENS (DICIONÁRIO MASSIVO)
# 2. INTELIGÊNCIA DAS IMAGENS
# ==========================================
IMAGENS_CATEGORIA = {
'politica': 'https://portaldosportais.com/wp-content/uploads/2026/05/Politica-scaled.jpg',
@@ -53,6 +54,8 @@
'infraestrutura': 'https://portaldosportais.com/wp-content/uploads/2026/05/infraestrutura-scaled.jpg',
'dae': 'https://portaldosportais.com/wp-content/uploads/2026/05/dae.jpeg',
'economia': 'https://portaldosportais.com/wp-content/uploads/2026/05/financas-scaled.jpg',
    # ATUALIZADO: Nova categoria genérica só para empregos!
    'empregos': 'https://portaldosportais.com/wp-content/uploads/2026/05/pexels-mart-production-7644081-scaled.jpg',
'educacao': 'https://portaldosportais.com/wp-content/uploads/2026/05/classroom-scaled.jpg',
'esportes': 'https://portaldosportais.com/wp-content/uploads/2026/05/esporte-scaled.jpg',
'eventos': 'https://portaldosportais.com/wp-content/uploads/2026/05/events-scaled.jpg',
@@ -64,12 +67,16 @@
}

def categorizar_noticia(titulo, imagem_atual, fonte):
    # BLINDAGEM: Converte para string para não travar se vier vazio
t = str(titulo).lower()
f = str(fonte).lower()
nova_imagem = None

    if any(p in t for p in ['gama', 'polícia', 'pm', 'preso', 'furto', 'roubo', 'acidente', 'baep', 'guarda', 'golpe', 'tráfico', 'arma', 'violência', 'crime', 'homicídio', 'morte', 'assalto', 'tiroteio', 'drogas', 'investigação']):
    # ATUALIZADO: Separamos Empregos de Economia para usar a sua foto nova
    if any(p in t for p in ['vagas', 'pat', 'emprego', 'estágio', 'ciee', 'contrata', 'processo seletivo']):
        nova_imagem = IMAGENS_CATEGORIA['empregos']
    elif any(p in t for p in ['indústria', 'comércio', 'economia', 'mercado', 'inflação', 'venda', 'negócio']):
        nova_imagem = IMAGENS_CATEGORIA['economia']
    elif any(p in t for p in ['gama', 'polícia', 'pm', 'preso', 'furto', 'roubo', 'acidente', 'baep', 'guarda', 'golpe', 'tráfico', 'arma', 'violência', 'crime', 'homicídio', 'morte', 'assalto', 'tiroteio', 'drogas', 'investigação']):
nova_imagem = IMAGENS_CATEGORIA['policia']
elif any(p in t for p in ['câmara', 'prefeito', 'vereador', 'sardelli', 'eleição', 'projeto', 'lei', 'tce', 'tse', 'votação', 'deputado']):
nova_imagem = IMAGENS_CATEGORIA['politica']
@@ -81,8 +88,6 @@
nova_imagem = IMAGENS_CATEGORIA['frio']
elif any(p in t for p in ['asfalto', 'obra', 'iluminação', 'reforma', 'praça', 'infraestrutura', 'recapeamento', 'viaduto']):
nova_imagem = IMAGENS_CATEGORIA['infraestrutura']
    elif any(p in t for p in ['vagas', 'pat', 'emprego', 'indústria', 'comércio', 'economia', 'mercado', 'inflação', 'estágio', 'ciee', 'contrata', 'venda', 'negócio']):
        nova_imagem = IMAGENS_CATEGORIA['economia']
elif any(p in t for p in ['escola', 'creche', 'educação', 'univesp', 'fatec', 'aluno', 'professor', 'enem', 'curso', 'aula', 'faculdade']):
nova_imagem = IMAGENS_CATEGORIA['educacao']
elif any(p in t for p in ['futebol', 'rio branco', 'campeonato', 'jogo', 'atleta', 'esporte', 'ginásio', 'torneio', 'medalha', 'copa', 'libertadores']):
@@ -98,6 +103,11 @@
elif 'americana' in t:
nova_imagem = IMAGENS_CATEGORIA['americana']

    # Força a categoria de empregos se a fonte for o Vagas019 (para usar a foto genérica caso precise)
    if 'vagas019' in f or 'vagas 019' in f:
        if not nova_imagem:
            nova_imagem = IMAGENS_CATEGORIA['empregos']

if 'novomomento' in f or 'novo momento' in f:
return nova_imagem if nova_imagem else LINK_FALLBACK_PADRAO

@@ -106,7 +116,8 @@

link_limpo = str(imagem_atual).lower()

    palavras_lixo = ['logo', 'default', 'padrao', 'fallback', '0addff39', 'americana-post', 'kyijbwc6', 'o-jogo', 'images.jpg', 'images.png', 'download.jpg', 'download.png', 'cropped', 'nm-site', 'sem-foto', 'placeholder', 'blank', 'thumb', 'marca', 'capa', '150x150', '300x200', '300x300']
    # ATUALIZADO: Adicionei o 'logo-vagas' na lista de lixos para ele substituir o logo pequeno da sua print pela foto genérica do Pexels
    palavras_lixo = ['logo', 'default', 'padrao', 'fallback', '0addff39', 'americana-post', 'kyijbwc6', 'o-jogo', 'images.jpg', 'images.png', 'download.jpg', 'download.png', 'cropped', 'nm-site', 'sem-foto', 'placeholder', 'blank', 'thumb', 'marca', 'capa', '150x150', '300x200', '300x300', 'logo-vagas']

is_lixo = any(lixo in link_limpo for lixo in palavras_lixo)
is_fallback = LINK_FALLBACK_PADRAO.split('/')[-1].lower() in link_limpo
@@ -183,7 +194,6 @@
with open('feed_mestre.json', 'r', encoding='utf-8') as f:
dados_antigos = json.load(f)
for noticia in dados_antigos:
                # BLINDAGEM: Usamos o .get() para não dar erro fatal se a notícia antiga vier com defeito
titulo = noticia.get('titulo', 'Notícia')
imagem = noticia.get('imagem', '')
portal = noticia.get('portal', 'Portal RMC')
@@ -212,7 +222,6 @@
print(f"[{nome_curto_portal(url)}] Descarregou {len(feed.entries)} notícias.")

for entry in feed.entries[:100]:
            # BLINDAGEM: Se a notícia não tiver link, nós ignoramos e passamos para a próxima
link_noticia = entry.get('link', '')
if not link_noticia:
continue
@@ -237,7 +246,6 @@
timestamp_absoluto = time.time()
data_formatada = datetime.now().strftime("%d/%m/%Y")

            # BLINDAGEM: Pega o título com segurança
titulo_seguro = entry.get('title', 'Notícia')

imagem_original = extrair_melhor_imagem(entry, url)
@@ -268,7 +276,6 @@
lista_final.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
lista_final = lista_final[:1000]

# TRAVA DE SEGURANÇA MÁXIMA: Só salva o JSON se tiver notícias. Se a internet do GitHub falhar, ele NÃO apaga o seu site!
if len(lista_final) > 0:
with open('feed_mestre.json', 'w', encoding='utf-8') as f:
json.dump(lista_final, f, ensure_ascii=False, indent=4)
