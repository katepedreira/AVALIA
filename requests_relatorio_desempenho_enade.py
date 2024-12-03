import requests
import os
from datetime import datetime

pdf_url = 'https://enade.inep.gov.br/enade/rest/relatorio/downloadArquivoCurso'

# Cabeçalhos da requisição
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Referer': 'https://enade.inep.gov.br/enade/',
    'X-Requested-With': 'XMLHttpRequest'
}

cookies = {
    'dtCookie': 'v_4_srv_2_sn_76F8E892272AC86646BAA0A9E2E3B42A_perc_100000_ol_0_mul_1_app-3A87964e2e77eecde1_1',
    'BIGipServerEnade_angular': 'oIQzn1j3m/dBF9jwaOUTahtKXK1EngYZJwsyoLdap6gcVXDpk8V/PudJW2ZnWL/0Gkd9UAGKqWVmqg==',
    'TS01a5831c': '01ae2560afbff1f2e0a33057b31d62f66b4090530998317b2029cc5c3844d0910786f387c0d5fd5d67d35f3b6eb9776c78ef8f208e379f48e32c71e062b07e365f417077a632ffbe0dbcacf67a751906b66031a0df'
}

save_directory = '/Users/katherinesousapedreira/PycharmProjects/chatgpt/relatorios_desempenho'

if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Obter o ano atual
ano_atual = datetime.now().year

for ano in range(2000, ano_atual + 1):
    data = {
        "ano": ano,
        "coMunicipio": 3136702,
        "noMunicipio": "JUIZ DE FORA",
        "coIes": 1253,
        "noIes": "FACULDADE METODISTA GRANBERY",
        "coArea": 4006,
        "noArea": "SISTEMAS DE INFORMAÇÃO",
        "coCurso": 47113,
        "noCurso": "SISTEMAS DE INFORMACAO",
        "fileName": "40060125331367020000047113.pdf"
    }

    # Nome dinâmico para o arquivo PDF salvo localmente
    file_name = f"relatorio_desempenho_enade_{ano}_{data['noCurso']}.pdf"

    # Caminho completo onde o arquivo será salvo
    file_path = os.path.join(save_directory, file_name)

    # Fazer a requisição POST para baixar o PDF
    response = requests.post(pdf_url, headers=headers, cookies=cookies, json=data)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Download concluído e salvo como '{file_path}'")
    else:
        print(f"Falha ao acessar o arquivo PDF para o ano {ano}. Status code: {response.status_code}")
        print("Resposta do servidor:")
        print(response.text)
