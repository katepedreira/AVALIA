# AVALIA - Sistemas de Informação

Este repositório contém os scripts e os dados utilizados para o desenvolvimento da ferramenta **Avalia**, que utiliza um Large Language Model (LLM), ou modelo de linguagem de grande porte, para analisar dados do Exame Nacional de Desempenho dos Estudantes (ENADE) do curso de Sistemas de Informação da Faculdade Metodista Granbery. 

A ferramenta **AvalIA** visa identificar padrões de dificuldades e lacunas de conhecimento dos alunos, correlacionando questões do exame, disciplinas do curso e resultados dos alunos, com o objetivo de subsidiar revisões no projeto pedagógico e aprimorar a qualidade do ensino. 

A metodologia do projeto incluiu a coleta e processamento dos dados do ENADE de 2021, aplicando uma abordagem híbrida que combina similaridade de cosseno e LLM para correlacionar questões e disciplinas, além da geração de relatórios e do desenvolvimento de um chatbot interativo. Os resultados da prova de conceito demonstraram alta precisão na correlação entre as questões e as disciplinas, alcançando uma taxa de acerto de 90,9%, bem como na identificação de áreas que necessitam de melhorias curriculares. 

O estudo conclui que a aplicação de LLMs é viável e eficaz na análise de dados educacionais, sugerindo a expansão futura da ferramenta para outros cursos.

Trabalho de conclusão de curso apresentado por @katepedreira e @JuliaAlves26 como requisito para obtenção do título de Bacharel em Sistemas de Informação.

## Estrutura do Projeto

- **`chatbot.py`**: Implementação do chatbot usando Gradio e o modelo GPT-4. Permite aos usuários fazer perguntas sobre o desempenho dos alunos no ENADE e acessar relatórios gerados a partir das análises. O chatbot usa o modelo de linguagem para responder perguntas com base em um resumo das questões e informações armazenadas no arquivo `detalhamento_por_questao_unificado.txt`.

- **`desempenho_estudantes_dinamico.py`**: Extrai dados de relatórios de desempenho em PDF e os transforma em tabelas CSV, que são usadas para a análise posterior. Esse script processa os relatórios do ENADE e converte os dados para um formato estruturado, facilitando o uso em outras aplicações.

- **`detalhamento_por_questao_unificado.txt`**: Contém um resumo detalhado das questões do ENADE, incluindo informações sobre a disciplina relacionada, ementa, percentual de acerto, e similaridade entre as questões e o conteúdo das disciplinas.

- **`disciplinas_si_fmg.json`**: Arquivo JSON contendo as disciplinas do curso de Sistemas de Informação, suas respectivas ementas, carga horária e bibliografias.

- **`extracao_disciplinas_ementa_si_fmg.py`**: Script para extrair as disciplinas e suas informações, como ementa e bibliografia, de um arquivo PDF contendo o currículo do curso. O script utiliza a biblioteca `PyMuPDF` para ler o PDF e armazenar os dados em formato JSON.

- **`prompt_cosine_similarity_dinamico.py`**: Script que utiliza modelos de embedding da OpenAI e similaridade do cosseno para correlacionar questões do ENADE com disciplinas do curso. Ele também utiliza um modelo de linguagem para calcular uma média ponderada entre a similaridade do cosseno e uma avaliação mais subjetiva baseada no contexto.

- **`questoes_infos_dinamico.py`**: Utiliza OCR (`pytesseract`) para extrair o texto das questões dos arquivos PDF do ENADE, estruturando os dados para posterior análise. As questões extraídas são salvas em arquivos JSON.

- **`relatorio_chatbot_unificado.txt`**: Relatório simplificado com informações sobre cada questão e a disciplina correspondente, incluindo um resumo do conteúdo da questão.

- **`request_provas_enade.py`**: Script para baixar as provas do ENADE disponíveis online. Utiliza a biblioteca `requests` para realizar o download dos PDFs a partir dos URLs.

- **`requests_relatorio_desempenho_enade.py`**: Realiza requisições para baixar relatórios de desempenho dos estudantes no ENADE. Gera arquivos PDF dos relatórios que são usados em outras etapas da análise.

## Como Executar

1. **Clone o Repositório**
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. **Instale as Dependências**
   Crie um ambiente virtual e instale as dependências necessárias.
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install PyMuPDF pytesseract pandas openai gradio requests scikit-learn
   ```

3. **Configure a Chave da API da OpenAI**
   Defina a variável de ambiente `OPENAI_API_KEY` com sua chave de API da OpenAI.
   ```bash
   export OPENAI_API_KEY='SUA_CHAVE_DE_API'
   ```

4. **Execute o Chatbot**
   Para iniciar o chatbot e interagir com o sistema, execute:
   ```bash
   python chatbot.py
   ```

5. **Processar Dados do ENADE**
   Execute os scripts para processar os dados das provas e relatórios do ENADE:
   ```bash
   python desempenho_estudantes_dinamico.py
   python request_provas_enade.py
   python requests_relatorio_desempenho_enade.py
   ```

## Tecnologias Utilizadas

- **Python**: Linguagem principal usada nos scripts.
- **Gradio**: Interface para construir o chatbot.
- **PyMuPDF (`fitz`) e `pytesseract`**: Para extração de texto de PDFs.
- **OpenAI API**: Para gerar resumos e realizar análises de similaridade com modelos de linguagem.
- **Pandas**: Para manipulação dos dados extraídos dos relatórios.

## Contribuições

Contribuições são bem-vindas! Fique à vontade para abrir issues ou enviar pull requests para melhorias.

