# AVALIA - Sistemas de Informação

Este repositório contém os scripts e dados utilizados para o desenvolvimento da ferramenta **Avalia**, criada por @katepedreira e @JuliaAlves26 como parte do trabalho de conclusão de curso para obtenção do título de Bacharel em Sistemas de Informação. 

A ferramenta **Avalia** utiliza um *Large Language Model* (LLM), ou modelo de linguagem de grande porte, para analisar dados do Exame Nacional de Desempenho dos Estudantes (ENADE) do curso de Sistemas de Informação da Faculdade Metodista Granbery, visando identificar padrões de dificuldades e lacunas de conhecimento dos alunos, correlacionando questões do exame, disciplinas do curso e resultados dos alunos, com o objetivo de subsidiar revisões no projeto pedagógico e aprimorar a qualidade do ensino. A metodologia do projeto incluiu a coleta e processamento dos dados do ENADE de 2021, aplicando uma abordagem híbrida que combina similaridade de cosseno e LLM para correlacionar questões e disciplinas, além da geração de relatórios e do desenvolvimento de um chatbot interativo. Os resultados da prova de conceito demonstraram alta precisão na correlação entre as questões e as disciplinas, alcançando uma taxa de acerto de 90,9%, bem como na identificação de áreas que necessitam de melhorias curriculares. O estudo concluiu que a aplicação de LLMs é viável e eficaz na análise de dados educacionais, sugerindo a expansão futura da ferramenta para outros cursos.

## Estrutura do Projeto

- **`request_provas_enade.py`**: Script para baixar as provas do ENADE disponíveis online. Utiliza a biblioteca `requests` para realizar o download dos PDFs a partir dos URLs.

- **`requests_relatorio_desempenho_enade.py`**: Realiza requisições para baixar relatórios de desempenho dos estudantes no ENADE a partir dos URLs.

- **`desempenho_estudantes_dinamico.py`**: Extrai dados dos relatórios de desempenho em PDF e os transforma em tabelas CSV, que são usadas para a análise posterior. Esse script processa os relatórios do ENADE e converte os dados para um formato estruturado, facilitando o uso em outras aplicações.
  
- **`extracao_disciplinas_ementa_si_fmg.py`**: Script para extrair as disciplinas e suas informações, como ementa e bibliografia, de um arquivo PDF contendo o currículo do curso. O script utiliza a biblioteca `PyMuPDF` para ler o PDF e armazenar os dados em formato JSON.

- **`questoes_infos_dinamico.py`**: Utiliza OCR (`pytesseract`) para extrair o texto das questões dos arquivos PDF do ENADE, estruturando os dados para posterior análise. As questões extraídas são salvas em arquivos JSON.

- **`disciplinas_si_fmg.json`**: Arquivo JSON contendo as disciplinas do curso de Sistemas de Informação, suas respectivas ementas, carga horária e bibliografias.

- **`provas_enade`**: Pasta que contém os arquivos das provas do ENADE, em pdf.

- **`questoes_infos`**: Pasta que contém os arquivos json com todas as questões extraídas das provas do ENADE.

- **`relatorios_desempenho`**: Pasta que contém os arquivos de relatório de desempenho disponibilizados pelo INEP, em pdf.

- **`tabelas_desempenho_alunos`**: Pasta que contém os arquivos CSV das tabelas com os dados de desempenho dos alunos da FMG no ENADE.
  
- **`prompt_cosine_similarity_dinamico.py`**: Script que utiliza modelos de embedding da OpenAI, similaridade calculada pelo LLM e similaridade do cosseno para correlacionar questões do ENADE com disciplinas do curso.

- **`relatorio_chatbot_unificado.txt`**: Relatório simplificado com informações sobre cada questão e a disciplina correspondente, incluindo um resumo do conteúdo da questão.
  
- **`detalhamento_por_questao_unificado.txt`**: Relatório detalhado das questões do ENADE, incluindo o texto completo das questoes, alternativas, informações sobre a disciplina relacionada, ementa, percentual de acerto, e similaridade entre as questões e o conteúdo das disciplinas.

- **`chatbot.py`**: Implementação do chatbot usando Gradio e o modelo GPT-4. Permite aos usuários fazer perguntas sobre o desempenho dos alunos no ENADE e acessar os relatórios gerados. O chatbot usa o modelo de linguagem para responder perguntas com base nas informações detalhadas armazenadas no arquivo `detalhamento_por_questao_unificado.txt`.

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
   pip install PyMuPDF pytesseract pandas openai gradio requests scikit-learn PyPDF2 pdf2image
   ```

3. **Configure a Chave da API da OpenAI**
   Defina a variável de ambiente `OPENAI_API_KEY` com sua chave de API da OpenAI.

   ```bash
   export OPENAI_API_KEY='SUA_CHAVE_DE_API'
   ```

4. **Processar Dados do ENADE**
   Execute os scripts para processar os dados das provas e relatórios do ENADE:

   ```bash
   python request_provas_enade.py
   python requests_relatorio_desempenho_enade.py
   python questoes_infos_dinamico.py
   python desempenho_estudantes_dinamico.py
   python extracao_disciplinas_ementa_si_fmg.py
   python prompt_cosine_similarity_dinamico.py
   ```

5. **Execute o Chatbot**
   Para iniciar o chatbot e interagir com o sistema, execute:

   ```bash
   python chatbot.py
   ```

## Bibliotecas Utilizadas

O projeto utiliza diversas bibliotecas para a coleta, extração e processamento dos dados:

- **PyMuPDF**: Utilizada para extrair informações textuais de arquivos PDF, facilitando a coleta de dados estruturados.
- **PyPDF2**: Usada para ler e extrair texto dos PDFs dos relatórios de desempenho, permitindo a navegação pelo conteúdo das páginas.
- **pandas**: Utilizada para manipulação e organização dos dados extraídos dos relatórios em DataFrames, facilitando a conversão para CSV.
- **pdf2image**: Converte páginas de PDFs em imagens para posterior processamento com OCR.
- **pytesseract**: Aplicada para realizar reconhecimento óptico de caracteres (OCR) em PDFs convertidos em imagens.
- **Gradio**: Para criar uma interface web interativa que permite aos usuários consultarem os relatórios e interagirem com o chatbot.

## Contribuições

Contribuições são bem-vindas! Fique à vontade para abrir issues ou enviar pull requests para melhorias.

