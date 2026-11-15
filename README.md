# READ_ME — Painéis do Trabalho Final de IA003

**Disciplina:** IA003 Probabilidade e Estatística para IA · **Profa.:** Lisiane Selau · **Versão:** V1 · **Data:** 08/11/2026

Este programa é um app em Streamlit com os três painéis do trabalho final: **beneficiários de planos de saúde no Rio Grande do Sul** (ANS, setembro de 2026). Ele mostra a população de 2.667.053 vínculos a planos médico-hospitalares (Painel 1), uma amostra aleatória simples de 385 vínculos (Painel 2) e os intervalos de confiança, os testes de hipóteses e a comparação com a população (Painel 3).

---

## 1. O que tem na pasta

| Arquivo ou pasta | Para que serve |
|---|---|
| `app.py` | Arquivo principal: abre o app e monta o menu das páginas |
| `nucleo.py` | Funções usadas pelos painéis: leitura dos dados, estatísticas, testes, simulação e gráficos |
| `paginas/` | As quatro páginas: `inicio.py`, `painel1_populacao.py`, `painel2_amostra.py` e `painel3_inferencia.py` |
| `dados/` | Os dados já prontos: população agregada, vínculos por município, amostra sorteada e metadados |
| `prepara_base.py` | Refaz os dados do zero a partir do arquivo da ANS (opcional; ver seção 4) |
| `requirements.txt` | Lista das bibliotecas que o app usa |
| `.streamlit/config.toml` | Cores e tema do app |
| `README.md` | Cópia deste texto, para aparecer na página do repositório no GitHub |

## 2. Requisitos

- **Python 3.10 ou mais recente.** O app foi testado com Python 3.13, e o preparo da base com Python 3.10.
- **Internet**, só para instalar as bibliotecas e, se for refazer a base, para baixar o arquivo da ANS.
- **Bibliotecas:** `streamlit`, `pandas`, `numpy`, `scipy` e `plotly`, instaladas pelo `requirements.txt`.

## 3. Como executar no Windows

**Passo 1. Instalar o Python** (se ainda não tiver). Baixe em python.org e, na primeira tela do instalador, marque **"Add python.exe to PATH"**. Para conferir, abra o PowerShell e digite `python --version`.

**Passo 2. Abrir o terminal na pasta do programa.** No Explorador de Arquivos, entre na pasta `AVALIAÇÃO_painel_streamlit_V1`, clique na barra de endereço, digite `powershell` e tecle Enter. O PowerShell abre já dentro da pasta.

**Passo 3 (opcional, recomendado). Criar um ambiente virtual**, para não misturar estas bibliotecas com outras do computador:

```
python -m venv .venv
.venv\Scripts\activate
```

Com o ambiente ativo, o terminal mostra `(.venv)` no início da linha. Nas próximas vezes, basta repetir a segunda linha.

**Passo 4. Instalar as bibliotecas** (leva cerca de um minuto):

```
python -m pip install -r requirements.txt
```

**Passo 5. Rodar o app:**

```
python -m streamlit run app.py
```

O navegador abre sozinho em `http://localhost:8501`. Cada painel tem o seu endereço:

| Página | Endereço local |
|---|---|
| Início | `http://localhost:8501` |
| Painel 1 · População | `http://localhost:8501/populacao` |
| Painel 2 · Amostra | `http://localhost:8501/amostra` |
| Painel 3 · Inferência | `http://localhost:8501/inferencia` |

Na primeira vez, o Painel 3 leva alguns segundos para abrir, porque simula 1.000 amostras; depois o resultado fica guardado em memória.

**Passo 6. Encerrar:** volte ao terminal e tecle Ctrl+C.

**No Linux ou no macOS**, os comandos são os mesmos, trocando `python` por `python3` e a ativação do ambiente por `source .venv/bin/activate`.

## 4. Refazer a base e o sorteio (opcional)

A pasta `dados` já traz tudo o que o app precisa. Para conferir que os dados saem da fonte original, o script `prepara_base.py` refaz tudo do zero:

1. lê o arquivo da ANS (`pda-024-icb-RS-2026_09.zip`);
2. mantém os vínculos ativos a planos médico-hospitalares com faixa etária válida;
3. calcula a idade pelo ponto médio da faixa etária;
4. sorteia a amostra aleatória simples de 385 vínculos com a semente fixa 20261108;
5. grava os quatro arquivos da pasta `dados`.

Para baixar o arquivo direto do site da ANS (23,9 MB):

```
python prepara_base.py
```

Para usar o arquivo que já está na pasta `AVALIAÇÃO`, sem baixar de novo:

```
python prepara_base.py --zip "..\..\AVALIAÇÃO\pda-024-icb-RS-2026_09.zip"
```

- **Tempo e memória:** leva menos de um minuto e usa cerca de 1 GB de memória.
- **Resultado esperado:** $N$ = 2.667.053 e $n$ = 385. A semente fixa reproduz exatamente a mesma amostra: o arquivo gerado foi conferido e é idêntico, byte a byte, ao da pasta `dados`.
- **Não troque a semente.** Sortear outra amostra depois de ver os resultados invalidaria a inferência.
- **Arquivo baixado:** se o script baixar o zip, ele fica na pasta `dados`. O app não precisa dele, então não é preciso enviá-lo ao GitHub.

## 5. Publicar na internet (Streamlit Community Cloud)

1. No GitHub, crie um repositório **público** e envie o conteúdo desta pasta: `app.py`, `nucleo.py`, `prepara_base.py`, `requirements.txt`, `README.md` e as pastas `paginas`, `dados` e `.streamlit`.
2. Em share.streamlit.io, entre com a conta do GitHub e crie um app apontando para o repositório, a branch `main` e o arquivo `app.py`.
3. O app ganha um endereço do tipo `https://NOME.streamlit.app`. Os painéis ficam em `/populacao`, `/amostra` e `/inferencia`.
4. Abra os links numa janela anônima para confirmar que abrem sem login. O app "dorme" após 12 horas sem acesso; qualquer visitante o reativa com um clique.

## 6. Problemas comuns

| Problema | Solução |
|---|---|
| `python` não é reconhecido | Reinstale o Python marcando "Add python.exe to PATH", ou use `py` no lugar de `python` (por exemplo, `py -m streamlit run app.py`) |
| `streamlit` não é reconhecido | Rode sempre como `python -m streamlit run app.py` |
| O PowerShell bloqueia a ativação do ambiente virtual | Rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, ou use o Prompt de Comando com `.venv\Scripts\activate.bat` |
| A porta 8501 já está em uso | `python -m streamlit run app.py --server.port 8502` |
| Erro de arquivo não encontrado em `dados/` | Rode o comando de dentro da pasta do programa e confira se a pasta `dados` tem os quatro arquivos |
| A pasta `.streamlit` não subiu para o GitHub | O app funciona sem ela; só muda o tema. Para manter as cores, envie a pasta também |
| O app online mostra que está dormindo | Clique no botão para reativá-lo e aguarde alguns segundos |

## 7. Como o programa funciona

- **Dados agregados com pesos.** A ANS publica contagens, não registros individuais. Por isso `populacao_agregada.csv` tem uma linha por combinação de sexo, faixa etária, tipo de contratação, tipo de vínculo, modalidade, abrangência, município (Porto Alegre ou interior) e época do plano, com o número de vínculos na coluna `vinculos`. Todas as estatísticas da população usam essa coluna como peso.
- **Amostra.** `amostra_AAS.csv` tem uma linha por vínculo sorteado (peso 1), com a posição sorteada e a linha do cadastro de onde ele saiu.
- **Testes.** `nucleo.py` traz os quatro testes da Aula 4: $Z$ para uma proporção, $Z$ para duas proporções (com o teste exato de Fisher como verificação), $t$ para uma média e $t$ de Welch para duas médias. Os parâmetros da população são calculados com a base inteira, só para comparar.
- **Simulação.** O Painel 3 sorteia 1.000 outras amostras de 385 vínculos (semente 2026) para mostrar a variabilidade amostral, a cobertura dos intervalos e o poder dos testes.
- **Gráficos.** São feitos com Plotly; passar o mouse sobre um gráfico mostra os valores.

## 8. Fontes dos dados

- ANS, Informações Consolidadas de Beneficiários (PDA-024): [conjunto de dados](https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/), [arquivo do RS de set/2026](https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/202609/pda-024-icb-RS-2026_09.zip) e [dicionário de dados](https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/dicionario/dicionario-pda-024-informacoes_consolidadas_de_beneficiarios.ods).
- IBGE, Censo 2022, população do RS por idade: [publicação](https://biblioteca.ibge.gov.br/visualizacao/periodicos/3102/cd_2022_populacao_idade_sexo_rs.pdf) e [tabela SIDRA 9514](https://sidra.ibge.gov.br/tabela/9514).

## Histórico de versões

| Versão | Data | Alteração |
|---|---|---|
| V1 | 08/11/2026 | Criação: instruções para executar, refazer a base e publicar o app |
