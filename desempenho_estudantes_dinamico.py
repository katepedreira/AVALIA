import pandas as pd
import os
import re
from PyPDF2 import PdfReader

# Diretório onde os arquivos PDF estão armazenados
pdf_directory = '/Users/katherinesousapedreira/PycharmProjects/chatgpt/relatorios_desempenho'

# Diretório onde os arquivos CSV serão salvos
output_directory = '/Users/katherinesousapedreira/PycharmProjects/chatgpt/tabelas_desempenho_alunos'

os.makedirs(output_directory, exist_ok=True)

year_pattern = re.compile(r'relatorio_desempenho_enade_(\d{4})')

# Função para ler o conteúdo do PDF
def read_pdf_content(pdf_path):
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    all_text = ""

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        all_text += page.extract_text()

    return all_text

# Função para extrair as tabelas
def extract_table_from_text(text):
    lines = text.split("\n")
    table_data = []

    for line in lines:
        if any(str(i) in line for i in range(9, 36)):
            table_data.append(line.split())

    return table_data

# Função para processar o PDF
def process_pdf(pdf_path):
    text = read_pdf_content(pdf_path)
    table_data = extract_table_from_text(text)

    if table_data:
        df = pd.DataFrame(table_data)
        return df
    return None

# Função para ajustar as colunas e lidar com mais colunas do que o esperado
def adjust_columns(df):
    column_names = ['Questão', 'Curso', 'UF', 'Região', 'Cat. Adm.', 'Org. Acad.', 'Brasil']

    if df.shape[1] >= len(column_names):
        df = df.iloc[:, :len(column_names)]
        df.columns = column_names
    else:
        print(f"Aviso: Número inesperado de colunas ({df.shape[1]}). Ajustando dinamicamente.")
        df.columns = column_names[:df.shape[1]]

    return df

# Função para filtrar as questões entre 9 e 35
def filter_dataframe(df):
    df['Questão'] = pd.to_numeric(df['Questão'], errors='coerce')
    df_filtered = df[df['Questão'].between(9, 35)]

    # Selecionar apenas as colunas relevantes
    df_filtered = df_filtered[['Questão', 'Curso', 'UF', 'Região', 'Cat. Adm.', 'Org. Acad.', 'Brasil']]

    return df_filtered

# Função principal para processar os PDFs e salvar as tabelas
def process_pdfs_and_save():
    for filename in os.listdir(pdf_directory):
        match = year_pattern.search(filename)
        if match:
            year = match.group(1)
            pdf_path = os.path.join(pdf_directory, filename)

            print(f"Processando o arquivo PDF do ano {year}: {pdf_path}")

            df = process_pdf(pdf_path)

            if df is not None:
                print(f"Tabelas extraídas com sucesso para o ano {year}")

                df_adjusted = adjust_columns(df)

                df_filtered = filter_dataframe(df_adjusted)

                if 'Questão' not in df_filtered.columns:
                    print("A coluna 'Questão' não foi encontrada no CSV.")
                    return

                df_filtered['Questão'] = pd.to_numeric(df_filtered['Questão'], errors='coerce')

                first_q9_indices = df_filtered.index[df_filtered['Questão'] == 9.0].tolist()

                if not first_q9_indices:
                    print("Não foi encontrada a Questão 9.0 no CSV.")
                    return

                first_q9 = first_q9_indices[0]

                first_q35_indices = df_filtered.index[(df_filtered['Questão'] == 35.0) & (df_filtered.index > first_q9)].tolist()

                if not first_q35_indices:
                    print("Não foi encontrada a Questão 35.0 após a Questão 9.0 no CSV.")
                    return

                first_q35 = first_q35_indices[0]

                # Extrair o bloco de Questão 9 a 35
                df_block = df_filtered.loc[first_q9:first_q35].copy()

                # Resetar o índice do DataFrame filtrado
                df_block.reset_index(drop=True, inplace=True)

                # Verificar se todas as questões de 9 a 35 estão presentes
                expected_questions = set(range(9, 36))
                found_questions = set(df_block['Questão'].dropna().astype(int))

                missing_questions = expected_questions - found_questions
                if missing_questions:
                    print(f"Aviso: As seguintes questões estão faltando no bloco extraído: {sorted(missing_questions)}")

                # Selecionar apenas as colunas relevantes
                columns_relevant = ['Questão', 'Curso', 'UF', 'Região', 'Cat. Adm.', 'Org. Acad.', 'Brasil']
                available_columns = [col for col in columns_relevant if col in df_block.columns]
                df_block = df_block[available_columns]

                # Exportar o bloco filtrado para um novo CSV
                output_csv = os.path.join(output_directory, f'desempenho_enade_{year}.csv')
                try:
                    df_block.to_csv(output_csv, index=False)
                    print(f"Bloco de questões 9 a 35 extraído com sucesso e salvo em '{output_csv}'.")
                except Exception as e:
                    print(f"Erro ao salvar o arquivo CSV filtrado: {e}")

# Executar o processo
process_pdfs_and_save()

