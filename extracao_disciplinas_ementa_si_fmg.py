import fitz  # PyMuPDF
import re
import json
import uuid

def extrair_texto_pdf(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    texto_completo = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        texto_completo += page.get_text("text") + "\n"
    return texto_completo

# Função para filtrar todas as informações de cada disciplina
def filtrar_disciplinas(texto):
    # Dividir o texto completo em seções baseadas em "COMPONENTE CARGA HORÁRIA PERÍODO"
    secoes = re.split(r'COMPONENTE\s+CARGA\s+HORÁRIA\s+PERÍODO', texto)
    disciplinas = []

    for secao in secoes[1:]:  # A primeira secao não contém uma disciplina válida
        linhas = [linha.strip() for linha in secao.splitlines() if linha.strip()]  # Ignorar linhas vazias e espaços
        disciplina_info = {}

        # Passar pelas linhas até encontrar a primeira linha não vazia, que será o componente (nome da disciplina)
        for linha in linhas:
            if linha:
                disciplina_info['componente'] = linha.strip()
                break

        # Captura dinâmica da carga horária e do período, extraindo apenas a parte numérica
        for x, linha in enumerate(linhas):
            carga_horaria_match = re.search(r'\d+', linhas[x])
            if carga_horaria_match:
                disciplina_info['carga_horaria'] = carga_horaria_match.group()
                if x + 1 < len(linhas):
                    periodo_match = re.search(r'\d+', linhas[x + 1])
                    if periodo_match:
                        disciplina_info['periodo'] = periodo_match.group()
                break

        ementa_iniciada = False
        ementa_linhas = []
        for i, linha in enumerate(linhas):
            if "EMENTA" in linha:
                ementa_iniciada = True
            elif "BIBLIOGRAFIA BÁSICA" in linha or "BIBLIOGRAFIA COMPLEMENTAR" in linha:
                ementa_iniciada = False
            if ementa_iniciada:
                ementa_linhas.append(linha.strip())

        # Armazena a ementa coletada
        if ementa_linhas:
            disciplina_info['ementa'] = "\n".join(ementa_linhas[1:]).strip()

        # Captura as bibliografias
        for i, linha in enumerate(linhas):
            if "BIBLIOGRAFIA BÁSICA" in linha:
                disciplina_info['bibliografia_basica'] = "\n".join(linhas[
                                                                   i + 1:linhas.index("BIBLIOGRAFIA COMPLEMENTAR",
                                                                                      i) if "BIBLIOGRAFIA COMPLEMENTAR" in linhas else len(
                                                                       linhas)]).strip()
            elif "BIBLIOGRAFIA COMPLEMENTAR" in linha:
                disciplina_info['bibliografia_complementar'] = "\n".join(linhas[i + 1:len(linhas)]).strip()

        # Adiciona o ID único usando UUID
        disciplina_info['id'] = str(uuid.uuid4())

        if disciplina_info:
            disciplinas.append(disciplina_info)

    return disciplinas

# Caminho para o arquivo PDF
caminho_pdf = "/Users/katherinesousapedreira/Desktop/contexto/EMENTA_GRANBERY_SI.pdf"

# Extrair texto do PDF
texto_extraido = extrair_texto_pdf(caminho_pdf)

# Filtrar disciplinas e todas as suas informações
disciplinas = filtrar_disciplinas(texto_extraido)

# Salvar as informações em um arquivo JSON
with open('disciplinas_si_fmg.json', 'w', encoding='utf-8') as f:
    json.dump(disciplinas, f, ensure_ascii=False, indent=4)
