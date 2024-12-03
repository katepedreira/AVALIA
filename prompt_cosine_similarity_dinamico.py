import os
import json
import re
import pandas as pd
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from sklearn.metrics.pairwise import cosine_similarity

# Definir as variáveis de ambiente e configurar o LLM e o modelo de embeddings
os.environ["OPENAI_API_KEY"] = "SUA_CHAVE_DE_API"

# Configurar o LLM e o modelo de embeddings
llm = OpenAI(model="gpt-4o-mini", temperature=0)
embed_model = OpenAIEmbedding()

# Lista de anos a serem processados
anos = [2017, 2021]

# Caminho para as disciplinas
caminho_json_disciplinas = "disciplinas_si_fmg.json"

# Carregar as disciplinas do arquivo JSON
with open(caminho_json_disciplinas, 'r', encoding='utf-8') as f:
    disciplinas = json.load(f)

# Funcao para gerar um resumo do texto da questao
def gerar_resumo_questao(questao_texto, llm):
    prompt_resumo = (
        f"Resuma o seguinte conteúdo de uma questão de forma breve, sem incluir as alternativas ou qualquer texto relacionado às opções de resposta. "
        f"Responda apenas com o resumo da questão em si.\n\n"
        f"Conteúdo da questão:\n{questao_texto}"
    )
    response_resumo = llm.complete(prompt_resumo)
    return response_resumo.text.strip()

# Funcao para calcular o embedding da ementa da disciplina
def calcular_embeddings_ementas(disciplinas, embed_model):
    embeddings_ementas = {}
    for disciplina in disciplinas:
        ementa = disciplina.get('ementa', '')
        componente_nome = disciplina.get('componente', '')
        if ementa:
            ementa_embedding = embed_model.get_text_embedding(ementa)
            embeddings_ementas[componente_nome] = ementa_embedding
        else:
            print(f"Ementa vazia para a disciplina '{componente_nome}'.")
    return embeddings_ementas

# Funcao para obter as "k" disciplinas a serem comparadas pelo modelo, utilizando a similaridade do cosseno
def obter_disciplinas_candidatas(questao_texto, embeddings_ementas, disciplinas, embed_model, top_k):
    questao_embedding = embed_model.get_text_embedding(questao_texto)
    similaridades = []
    for disciplina in disciplinas:
        componente_nome = disciplina.get('componente', '')
        ementa_embedding = embeddings_ementas.get(componente_nome)
        if ementa_embedding is not None:
            similarity = cosine_similarity([questao_embedding], [ementa_embedding])[0][0]
            similaridades.append({
                'disciplina': disciplina,
                'similarity': similarity
            })
        else:
            print(f"Embedding não encontrado para a disciplina '{componente_nome}'.")
    similaridades.sort(key=lambda x: x['similarity'], reverse=True)
    disciplinas_candidatas = similaridades[:top_k]
    return disciplinas_candidatas

# Funcao para obter o percentual de similaridade, calculado pela LLM, entre a questão e as disciplinas
def calcular_similaridade_modelo(ementa_disciplina, questao_texto, llm):
    prompt_similaridade = (
        f"Avalie o grau de correspondência entre a ementa abaixo e o conteúdo da questão a seguir. "
        f"Considere os objetivos de aprendizagem, os conceitos principais, as habilidades e competências abordadas na ementa, "
        f"e analise como eles são aplicados ou requeridos na questão. "
        f"Leve em conta a profundidade dos tópicos, a complexidade das habilidades e a relevância dos conceitos envolvidos. "
        f"Com base nessa análise, atribua um percentual de similaridade entre 0 a 100, onde 0 indica nenhuma correspondência e 100 indica correspondência total. "
        f"Forneça apenas o valor numérico da similaridade em percentual.\n\n"
        f"Ementa:\n{ementa_disciplina}\n\n"
        f"Questão:\n{questao_texto}"
    )
    response_similaridade = llm.complete(prompt_similaridade)
    similaridade_texto = response_similaridade.text
    similaridade_match = re.search(r'\b\d+(\.\d+)?\b', similaridade_texto)
    if similaridade_match:
        similaridade = float(similaridade_match.group(0))
    else:
        similaridade = 0

    return similaridade

# Funcao para calcular a média ponderada entre a similaridade do cosseno e a similaridade calculada pelo LLM
def calcular_similaridade_media(peso_cosseno, similaridade_cosseno, peso_modelo, similaridade_modelo):
    media_similaridades = (peso_cosseno * similaridade_cosseno + peso_modelo * similaridade_modelo)

    return media_similaridades

# Funcao que faz a correlacao 1:1 entre as questoes e as disciplinas
def identificar_componente_correlacionado(questao_texto, disciplinas_candidatas, llm, limiar_similaridade, peso_cosseno, peso_modelo):
    melhor_disciplina = None
    maior_media_similaridades = -1

    for item in disciplinas_candidatas:
        disciplina = item['disciplina']
        similaridade_cosseno = item['similarity'] * 100
        componente_nome = disciplina.get('componente', '')
        ementa = disciplina.get('ementa', '')

        # Calcular a similaridade do modelo
        similaridade_modelo = calcular_similaridade_modelo(ementa, questao_texto, llm)

        # Calcular a média das similaridades
        media_similaridades = calcular_similaridade_media(peso_cosseno, similaridade_cosseno, peso_modelo, similaridade_modelo)

        print(
            f"Analisando Disciplina '{componente_nome}': Similaridade do Cosseno = {similaridade_cosseno:.2f}%, "
            f"Similaridade do Modelo = {similaridade_modelo}%, Média = {media_similaridades:.2f}%")

        # Verificar se atende ao limiar de similaridade do modelo
        if media_similaridades >= limiar_similaridade:
            if media_similaridades > maior_media_similaridades:
                melhor_disciplina = {
                    'componente_nome': componente_nome,
                    'similaridade_cosseno': similaridade_cosseno,
                    'similaridade_modelo': similaridade_modelo,
                    'media_similaridades': media_similaridades
                }
                maior_media_similaridades = media_similaridades

    # Selecionar a disciplina com a maior média das similaridades que atende ao limiar
    if melhor_disciplina:
        componente_nome = melhor_disciplina['componente_nome']
        similaridade_cosseno = melhor_disciplina['similaridade_cosseno']
        similaridade_modelo = melhor_disciplina['similaridade_modelo']
        media_similaridades = melhor_disciplina['media_similaridades']
        print(f"\nDisciplina selecionada: '{componente_nome}' com Média de Similaridades = {media_similaridades:.2f}%")
        return componente_nome, similaridade_cosseno, similaridade_modelo, media_similaridades

    # Caso nenhuma disciplina atenda ao limiar, seleciona a disciplina com a maior média geral
    if disciplinas_candidatas:
        print("\nNenhuma disciplina atendeu ao limiar de similaridade do modelo. Selecionando a disciplina com a maior média geral de similaridades.")
        melhor_media_item = None
        maior_media = -1
        for item in disciplinas_candidatas:
            disciplina = item['disciplina']
            similaridade_cosseno = item['similarity'] * 100
            componente_nome = disciplina.get('componente', '')
            ementa = disciplina.get('ementa', '')
            similaridade_modelo = calcular_similaridade_modelo(ementa, questao_texto, llm)
            media_similaridades = calcular_similaridade_media(peso_cosseno, similaridade_cosseno, peso_modelo, similaridade_modelo)

            if media_similaridades > maior_media:
                maior_media = media_similaridades
                melhor_media_item = (componente_nome, similaridade_cosseno, similaridade_modelo)

        if melhor_media_item:
            componente_nome, similaridade_cosseno, similaridade_modelo = melhor_media_item
            media_similaridades = calcular_similaridade_media(peso_cosseno, similaridade_cosseno, peso_modelo, similaridade_modelo)
            print(f"Fallback: Selecionando Disciplina '{componente_nome}' com Média de Similaridades = {maior_media:.2f}%")
            return componente_nome, similaridade_cosseno, similaridade_modelo, media_similaridades

    return None, 0.0, 0.0, 0.0

# Funcao para obter a ementa relacionada a disciplina
def buscar_ementa_disciplina(disciplina_nome, disciplinas):
    for disciplina in disciplinas:
        if disciplina['componente'].lower() == disciplina_nome.lower():
            ementa = disciplina.get('ementa', 'Ementa não encontrada')
            carga_horaria = disciplina.get('carga_horaria', 'Carga horária não encontrada')
            periodo = disciplina.get('periodo', 'Período não encontrado')
            return ementa, carga_horaria, periodo
    return 'Ementa não encontrada', 'Carga horária não encontrada', 'Período não encontrado'

def formatar_ementa(ementa_texto, componente_nome):
    # Remove o nome do componente da ementa, se presente
    ementa_formatada = ementa_texto.replace(f"Componente: {componente_nome}", "").replace(f"EMENTA:", "").replace(
        f"Ementa:", "")

    # Remove quebras de linha desnecessárias e espaços extras
    ementa_formatada = re.sub(r'\n+', ' ', ementa_formatada)
    ementa_formatada = re.sub(r'\s+', ' ', ementa_formatada)
    return ementa_formatada.strip()

# Função principal para processar os dados de múltiplos anos
def processar_anos(anos, disciplinas, embed_model, llm):
    resultados_correlacao = {}
    questao_texts = {}

    # Processar os embeddings das ementas
    embeddings_ementas = calcular_embeddings_ementas(disciplinas, embed_model)

    for ano in anos:
        print(f"\nProcessando o ano: {ano}")

        # Definir os caminhos dos arquivos para o ano atual
        caminho_desempenho_csv = f"tabelas_desempenho_alunos/desempenho_enade_{ano}.csv"
        caminho_json_questoes = f"questoes_infos/questoes_infos_enade_{ano}.json"

        # Carregar a tabela de desempenho para o ano atual
        if not os.path.exists(caminho_desempenho_csv):
            print(f"Arquivo CSV não encontrado para o ano {ano}: {caminho_desempenho_csv}")
            continue
        df_tabela_ano = pd.read_csv(caminho_desempenho_csv)

        # Carregar as questões do ano atual
        if not os.path.exists(caminho_json_questoes):
            print(f"Arquivo JSON de questões não encontrado para o ano {ano}: {caminho_json_questoes}")
            continue
        with open(caminho_json_questoes, 'r', encoding='utf-8') as f:
            questoes_ano = json.load(f)

        for questao in questoes_ano:
            questao_numero_str = questao.get('numero', '0')
            numeros_encontrados = re.findall(r'\d+', questao_numero_str)
            if numeros_encontrados:
                questao_numero = int(numeros_encontrados[0])
            else:
                print(f"Não foi possível extrair o número da questão '{questao_numero_str}'.")
                continue

            # Pegar somente as questões específicas
            if questao_numero < 9:
                continue

            dados_questao = df_tabela_ano[df_tabela_ano['Questão'] == questao_numero]

            # Verificar se o percentual de acerto é válido
            if dados_questao.empty:
                print(f"Dados não encontrados para a questão {questao_numero} no ano {ano}.")
                continue

            percentual_acerto = dados_questao['Curso'].values[0]
            if percentual_acerto == "-" or percentual_acerto == "*":
                continue

            valor_uf = dados_questao['UF'].values[0]
            valor_regiao = dados_questao['Região'].values[0]
            valor_brasil = dados_questao['Brasil'].values[0]

            resumo_questao = gerar_resumo_questao(questao['conteudo'], llm)

            # Obter disciplinas candidatas com similaridade do cosseno
            disciplinas_candidatas = obter_disciplinas_candidatas(
                questao_texto=questao['conteudo'],
                embeddings_ementas=embeddings_ementas,
                disciplinas=disciplinas,
                embed_model=embed_model,
                top_k=5
            )

            # Identificar o componente correlacionado usando o LLM baseado na média das similaridades
            disciplina_correlacionada, similaridade_cosseno, similaridade_modelo, media_similaridades = identificar_componente_correlacionado(
                questao_texto=questao['conteudo'],
                disciplinas_candidatas=disciplinas_candidatas,
                llm=llm,
                limiar_similaridade=50.0,
                peso_cosseno=0.5,
                peso_modelo=0.5
            )

            # Verificar se a disciplina correlacionada foi identificada
            if disciplina_correlacionada is None:
                print(f"Não foi possível identificar a disciplina para a questão {questao_numero} no ano {ano}")
                continue

            # Obter a ementa, carga horária e período da disciplina correlacionada
            ementa_disciplina, carga_horaria, periodo = buscar_ementa_disciplina(disciplina_correlacionada, disciplinas)
            if ementa_disciplina is None:
                print(f"Ementa não encontrada para a disciplina '{disciplina_correlacionada}' no ano {ano}.")
                continue

            # Armazenar os resultados com a informação do ano
            resultados_correlacao[questao['id']] = {
                "ano": ano,
                "questao_numero": questao_numero,
                "questao_texto": questao['conteudo'],
                "questao_resumo": resumo_questao,
                "percentual_acerto_ies": percentual_acerto,
                "percentual_acerto_uf": valor_uf,
                "percentual_acerto_regiao": valor_regiao,
                "percentual_acerto_brasil": valor_brasil,
                "disciplina_relacionada": disciplina_correlacionada,
                "grau_de_similaridade_cosseno": similaridade_cosseno,
                "grau_de_similaridade_modelo": similaridade_modelo,
                "grau_similaridade_media": media_similaridades
            }
            questao_texts[questao['id']] = questao['conteudo']

    return resultados_correlacao, questao_texts

# Função para gerar os relatórios
def gerar_relatorios(resultados_correlacao, disciplinas):
    relatorio = "Detalhamento por Questão de Conteúdo Específico:\n\n"
    relatorio2 = "Relatório por Questão de Conteúdo Específico:\n\n"
    for questao_id, dados in resultados_correlacao.items():
        ementa_disciplina, carga_horaria, periodo = buscar_ementa_disciplina(dados['disciplina_relacionada'], disciplinas)
        ementa_formatada = formatar_ementa(ementa_disciplina, dados['disciplina_relacionada'])

        relatorio += (
            f"Ano: {dados['ano']}\n"
            f"    Questão {dados['questao_numero']}:\n"
            f"        Texto: {dados['questao_texto'].strip()}\n"
            f"        Disciplina relacionada: {dados['disciplina_relacionada'].strip()}\n"
            f"        Ementa relacionada: {ementa_formatada}\n"
            f"        Carga horária: {carga_horaria}\n"
            f"        Período: {periodo}\n"
            f"        Percentual de acerto (IES): {dados['percentual_acerto_ies']}\n"
            f"        Percentual de acerto (UF): {dados['percentual_acerto_uf']}\n"
            f"        Percentual de acerto (Região): {dados['percentual_acerto_regiao']}\n"
            f"        Percentual de acerto (Brasil): {dados['percentual_acerto_brasil']}\n"
            f"        Percentual de similaridade do cosseno: {dados['grau_de_similaridade_cosseno']:.2f}%\n"
            f"        Percentual de similaridade do modelo: {dados['grau_de_similaridade_modelo']}\n"
            f"        Percentual de similaridade média: {dados['grau_similaridade_media']:.2f}\n\n"
        )

        relatorio2 += (
            f"Ano: {dados['ano']}\n"
            f"Questão {dados['questao_numero']}:\n"
            f"    Resumo: {dados['questao_resumo'].strip()}\n"
            f"    Disciplina Relacionada: {dados['disciplina_relacionada'].strip()}\n"
            f"    Ementa relacionada: {ementa_formatada}\n"
            f"    Período: {periodo}\n"
            f"    Carga Horária: {carga_horaria}\n"
            f"    Percentual de Acerto (IES): {dados['percentual_acerto_ies']}\n"
            f"    Percentual de Acerto (UF): {dados['percentual_acerto_uf']}\n"
            f"    Percentual de Acerto (Região): {dados['percentual_acerto_regiao']}\n"
            f"    Percentual de Acerto (Brasil): {dados['percentual_acerto_brasil']}\n\n"
        )

    # Salvar o relatório em um arquivo txt
    with open('detalhamento_por_questao_unificado.txt', 'w', encoding='utf-8') as f:
        f.write(relatorio)

    print("Relatório 'detalhamento_por_questao_unificado.txt' gerado com sucesso.")

    # Salvar o relatório2 em um arquivo txt
    with open('relatorio_chatbot_unificado.txt', 'w', encoding='utf-8') as f:
        f.write(relatorio2)

    print("Relatório 'relatorio_chatbot_unificado.txt' gerado com sucesso.")

# Execução principal
def main():
    # Processar os anos e obter os resultados
    resultados_correlacao, questao_texts = processar_anos(
        anos=anos,
        disciplinas=disciplinas,
        embed_model=embed_model,
        llm=llm
    )

    # Gerar os relatórios finais
    gerar_relatorios(resultados_correlacao, disciplinas)

if __name__ == "__main__":
    main()
