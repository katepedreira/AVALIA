import pytesseract  # OCR
from pdf2image import convert_from_path
import re
import json
import uuid
import os

# Funcao para tranformar o pdf em imagem e extrair o texto com OCR
def extrair_texto_ocr(caminho_pdf):
    imagens_paginas = convert_from_path(caminho_pdf)
    texto_completo = ""

    for imagem in imagens_paginas:
        texto = pytesseract.image_to_string(imagem, lang='por')
        texto_completo += texto + "\n"

    return texto_completo

# Funcao para identificar e formatar as questoes do texto extraido
def filtrar_questoes(texto, ano_prova):
    padrao_questao = re.compile(r'(QUESTÃO\s+\d+)', re.IGNORECASE)
    secoes = padrao_questao.split(texto)
    questoes = []

    for i in range(1, len(secoes), 2):
        numero_questao = secoes[i].strip().upper()
        conteudo_questao = secoes[i + 1].strip()

        questao_info = {
            "id": str(uuid.uuid4()),
            "ano": ano_prova,
            "numero": numero_questao,
            "conteudo": conteudo_questao
        }
        questoes.append(questao_info)

    return questoes


# Função para extrair o ano do caminho do arquivo PDF
def extrair_ano_do_caminho(caminho_pdf):
    nome_arquivo = os.path.basename(caminho_pdf)
    padrao_ano = re.compile(r'(\d{4})')  # Padrão para capturar o ano (4 dígitos)
    match = padrao_ano.search(nome_arquivo)
    if match:
        return match.group(1)
    return None


# Função para filtrar o primeiro bloco de questões (de 1 a 35)
def filtrar_primeiro_bloco_questoes(questoes):
    questoes_filtradas = []
    for questao in questoes:
        numero_questao = int(questao['numero'].split(' ')[1])
        if 1 <= numero_questao <= 35:
            questoes_filtradas.append(questao)
        if numero_questao == 35:
            break
    return questoes_filtradas

pasta_pdf = "provas_enade"

pasta_json = "/Users/katherinesousapedreira/PycharmProjects/chatgpt/questoes_infos"

os.makedirs(pasta_json, exist_ok=True)

arquivos_pdf = [f for f in os.listdir(pasta_pdf) if f.endswith('.pdf')]

for arquivo_pdf in arquivos_pdf:
    caminho_pdf = os.path.join(pasta_pdf, arquivo_pdf)

    ano_prova = extrair_ano_do_caminho(caminho_pdf)

    if ano_prova:
        texto_extraido = extrair_texto_ocr(caminho_pdf)

        questoes = filtrar_questoes(texto_extraido, ano_prova)

        questoes_filtradas = filtrar_primeiro_bloco_questoes(questoes)

        nome_arquivo_json = f'questoes_infos_enade_{ano_prova}.json'

        caminho_json = os.path.join(pasta_json, nome_arquivo_json)

        with open(caminho_json, 'w', encoding='utf-8') as f_out:
            json.dump(questoes_filtradas, f_out, ensure_ascii=False, indent=4)

        print(f'Foram filtradas {len(questoes_filtradas)} questões para o ano {ano_prova}.')
    else:
        print(f'Não foi possível extrair o ano do nome do arquivo PDF: {arquivo_pdf}')
