import warnings

warnings.filterwarnings("ignore")

import os
import gradio as gr
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# Configurar a chave da API da OpenAI
os.environ[
    "OPENAI_API_KEY"] = "SUA_CHAVE_DE_API"

# Definir o modelo do OpenAI
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.1)


# Função para carregar o arquivo e retornar o conteúdo
def ler_arquivo_txt(caminho_txt):
    try:
        with open(caminho_txt, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        return conteudo
    except FileNotFoundError:
        return f"Arquivo '{caminho_txt}' não encontrado."


# Função para processar a pergunta do chatbot
def processar_pergunta(pergunta, conversa):
    caminho_txt = "detalhamento_por_questao_unificado.txt"
    conteudo_txt = ler_arquivo_txt(caminho_txt)

    if "não encontrado" in conteudo_txt.lower():
        return "Desculpe, o relatório de questões não foi encontrado. Por favor, verifique se ele foi gerado corretamente.", conversa

    # Inicializa a conversa se estiver vazia
    if conversa is None or len(conversa) == 0:
        conversa = []

        # Adiciona o conteúdo do arquivo como mensagem do sistema
        system_message = SystemMessage(content=conteudo_txt)
        conversa.append(system_message)

    # Adiciona a pergunta do usuário ao histórico
    conversa.append(HumanMessage(content=pergunta))

    # Gera a resposta usando o histórico da conversa
    resposta = llm(conversa).content

    # Adiciona a resposta do assistente ao histórico
    conversa.append(AIMessage(content=resposta))

    return resposta, conversa


# Função para fornecer o relatório para download
def baixar_relatorio():
    caminho_relatorio = "relatorio_chatbot_unificado.txt"
    if os.path.exists(caminho_relatorio):
        return caminho_relatorio
    else:
        return None


# Configurar o estilo da interface
with gr.Blocks(css="""
    .gradio-container {
        max-width: 800px;
        margin: 0 auto; /* Centralizar a interface */
    }

    #enviar_btn {
        width: 180px !important;
    }

    #pergunta textarea {
        min-height: 80px !important;

    }

    #resposta textarea {
        min-height: 270px !important;

    }

    #baixar_relatorio_btn {
        width: 150px !important;
    }

    #download_button {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }

    #top_section {
        display: flex;
        justify-content: space-between;
        align-items: center; 
    }


""") as demo:
    with gr.Row(elem_id="top_section"):
        with gr.Column(scale=3, elem_id="title_section"):
            gr.Markdown("""
            # Aval<span style="color:#FF5733; font-weight:bold;">IA</span> - Sistemas de Informação
            """)
            gr.Markdown(
                "Faça perguntas sobre o desempenho dos alunos de Sistemas de Informação da Faculdade Metodista Granbery no ENADE.")
        with gr.Column(scale=1, elem_id="button_section"):
            with gr.Row(elem_id="download_button"):
                download_btn = gr.DownloadButton(
                    label="Baixar Relatório Geral",
                    value=baixar_relatorio,
                    elem_id="baixar_relatorio_btn"
                )

    with gr.Column():
        conversa = gr.State([])  # Inicializa o estado da conversa
        pergunta = gr.Textbox(
            label="Sua Pergunta",
            placeholder="Exemplo: 'Como foi o desempenho dos alunos da IES na prova do ENADE de 2021?'",
            elem_id="pergunta"
        )
        enviar_btn = gr.Button("Enviar", elem_id="enviar_btn")
        resposta = gr.Textbox(
            label="Resposta",
            interactive=False,
            elem_id="resposta"
        )

    enviar_btn.click(
        fn=processar_pergunta,
        inputs=[pergunta, conversa],
        outputs=[resposta, conversa]
    )

# Rodar o chatbot
if __name__ == "__main__":
    demo.launch()
