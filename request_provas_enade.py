import requests
import os
import re

# Função para extrair o ano a partir do URL
def extract_year_from_url(url):
    match = re.search(r'(\d{4})', url)
    if match:
        return match.group(1)
    return "ano_desconhecido"


# Função para baixar o arquivo
def download_pdf(url, output_dir):
    year = extract_year_from_url(url)

    output_file = os.path.join(output_dir, f'prova_enade_sistemas_de_informacao_{year}.pdf')

    response = requests.get(url)

    if response.status_code == 200:
        with open(output_file, 'wb') as file:
            file.write(response.content)
        print(f"Download concluído! Arquivo salvo como {output_file}")
    else:
        print(f"Falha ao fazer o download de {url}. Código de status: {response.status_code}")


# URLs das provas
urls = [
    'https://download.inep.gov.br/educacao_superior/enade/provas/2017/40_SIS_INFORMACAO_BAIXA.pdf',
    'https://download.inep.gov.br/enade/provas_e_gabaritos/2021_PV_bacharelado_sistema_informacao.pdf'
]

# Diretorio onde os arquivos PDF serão salvos
output_directory = '/Users/katherinesousapedreira/PycharmProjects/chatgpt/provas_enade'

# Criar o diretorio, se não existir
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Baixar todas as provas
for url in urls:
    download_pdf(url, output_directory)
