# Trabalho Final — Beneficiários de Planos de Saúde no Rio Grande do Sul

**Disciplina:** IA003 Probabilidade e Estatística para IA · **Profa.:** Lisiane Selau · **Aluno:** Paulo Roberto Walter Ferreira · **Data:** 15/11/2026

## 1. Links para avaliação

Todos os links abrem sem login e sem pedido de autorização.

| Item | Link |
|---|---|
| **Painel 1** — Análise descritiva da população | <https://ia003-trab-final-paulo.streamlit.app/populacao> |
| **Painel 2** — Análise descritiva da amostra | <https://ia003-trab-final-paulo.streamlit.app/amostra> |
| **Painel 3** — Inferência estatística e comparação dos resultados | <https://ia003-trab-final-paulo.streamlit.app/inferencia> |
| Página inicial dos painéis (ficha da base e hipóteses) | <https://ia003-trab-final-paulo.streamlit.app/> |
| **Vídeo de apresentação** (YouTube, 3 min 34 s) | <https://www.youtube.com/watch?v=BtQb52t6o-c> |
| Código-fonte, dados e instruções (GitHub) | <https://github.com/Paulo-WFerreira/IA003_TRAB_FINAL> |

Os painéis estão no Streamlit Community Cloud. Se a página abrir com um aviso de que o app está em espera, basta clicar no botão para reativá-lo; ele volta em alguns segundos.

## 2. Base de dados original

| Item | Conteúdo |
|---|---|
| Fonte | Agência Nacional de Saúde Suplementar (ANS), Plano de Dados Abertos: **Informações Consolidadas de Beneficiários** (PDA-024) |
| Conjunto de dados | <https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/> |
| Arquivo utilizado | Rio Grande do Sul, competência 09/2026: <https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/202609/pda-024-icb-RS-2026_09.zip> |
| Dicionário de dados | <https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/dicionario/dicionario-pda-024-informacoes_consolidadas_de_beneficiarios.ods> |
| Contexto | As operadoras informam à ANS cada pessoa ligada a cada plano de saúde. A ANS publica, por mês e por estado, o número de beneficiários por operadora, plano, município, sexo, faixa etária e tipo de vínculo |
| Tamanho | 910.435 linhas e 22 variáveis; 3.828.301 vínculos ativos |
| Referência externa | IBGE, Censo 2022, população do RS por idade: <https://sidra.ibge.gov.br/tabela/9514> |

## 3. Resumo do trabalho

- **População de interesse:** os 2.667.053 vínculos ativos de beneficiários a planos médico-hospitalares com residência no RS, em setembro de 2026.
- **Unidade amostral:** o vínculo de um beneficiário a um plano.
- **Variáveis:** idade (quantitativa, ponto médio da faixa etária, em anos); faixa etária, sexo, tipo de contratação, tipo de vínculo, modalidade da operadora, abrangência do plano e município (qualitativas).
- **Tamanho da amostra:** $n = 385$, com 95% de confiança, margem de erro de 5 pontos percentuais e $p = 0{,}5$ (pior caso), com correção para população finita ($n_0 = 384{,}16$; $n = 384{,}10$, arredondado para 385).
- **Amostra aleatória simples:** cada vínculo recebeu uma posição de 1 a 2.667.053, e 385 posições foram sorteadas sem reposição, com semente fixa (20261108). Todos os vínculos tiveram a mesma probabilidade de seleção. As hipóteses foram definidas antes do sorteio.
- **Hipóteses e resultados** (bilaterais, $\alpha = 5\%$; valores de referência do IBGE, Censo 2022):

| | Hipótese nula | Estimativa (IC de 95%) | Teste | Decisão | Na população |
|---|---|---|---|---|---|
| H1 | Proporção de 60 anos ou mais = 20,15% | 17,92% (14,09% a 21,75%) | $Z = -1{,}090$; valor-p = 0,276 | Não rejeita $H_0$ | 17,44%: erro tipo II |
| H2 | Proporção de 60 anos ou mais igual nos planos individuais e nos coletivos empresariais | Diferença de 16,27 pontos (4,47 a 28,07) | $Z = 3{,}404$; valor-p = 0,0007 (Fisher: 0,0017) | Rejeita $H_0$ | 20,51 pontos: acerto |
| H3 | Idade média = 38,91 anos | 38,68 anos (36,58 a 40,78) | $t = -0{,}218$; valor-p = 0,827 | Não rejeita $H_0$ | 38,46 anos: acerto na prática |
| H4 | Idade média igual nos planos individuais e nos coletivos empresariais | Diferença de 4,46 anos ($-2{,}20$ a 11,13) | $t$ de Welch = 1,335; valor-p = 0,186 | Não rejeita $H_0$ | 7,09 anos: erro tipo II |

- **Interpretação:** os quatro intervalos de confiança contêm o parâmetro da população. Os erros tipo II de H1 e H4 vêm de diferenças reais menores do que a precisão de uma amostra de 385. Na simulação de 1.000 outras amostras, cerca de 95% dos intervalos contiveram o parâmetro, e H1 e H4 seriam rejeitadas em apenas 31% e 42% das amostras.
- **Conclusão:** quem tem plano de saúde no RS tem, em média, a idade da população do estado, mas o tipo de contratação separa as gerações: 30,8% de pessoas com 60 anos ou mais nos planos individuais, contra 10,3% nos coletivos empresariais.

## 4. Onde encontrar cada item do enunciado

| Item do enunciado | Onde está |
|---|---|
| Fonte, link, contexto, número de observações e de variáveis, população, unidade amostral e variáveis | Página inicial dos painéis ("Ficha da base de dados") e seção 2 deste documento |
| Dimensionamento da amostra e seleção da AAS | Painel 2, seções "Tamanho da amostra" e "Seleção da amostra aleatória simples" |
| Análise descritiva da população | Painel 1 |
| Análise descritiva da amostra e comparação com a população | Painel 2 |
| Duas hipóteses para proporção (H1 e H2) e duas para média (H3 e H4), com IC, estatística de teste, valor-p, condições e conclusão | Painel 3 |
| Comparação entre população e amostra, variabilidade amostral e limitações | Painel 3, seções "Resumo", "Variabilidade amostral" e "Limitações" |
| Vídeo de até 5 minutos | YouTube (link na seção 1) |
| Reprodução dos dados e do sorteio | GitHub: script `prepara_base.py` e arquivo `README.md` |
