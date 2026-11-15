import streamlit as st

import nucleo as nc

pop, am, mun, meta = nc.carregar()
N = meta["N"]

st.title("Beneficiários de planos de saúde no Rio Grande do Sul")
st.caption("IA003 · Probabilidade e Estatística para IA · Profa. Lisiane Selau · Trabalho final · "
           "Aluno: Paulo Roberto Walter Ferreira")

st.markdown(
    f"""
A ANS publica, todo mês, quantas pessoas estão ligadas a cada plano de saúde, por município, sexo e faixa etária.
Este trabalho trata os **{nc.num(N)} vínculos ativos a planos médico-hospitalares no RS em setembro de 2026**
como a **população**. Uma **amostra aleatória simples de {meta['n']} vínculos** é sorteada dela, e o que a
amostra permite concluir é comparado com o que a população realmente é.

**Pergunta do trabalho:** o perfil etário de quem tem plano de saúde no RS é igual ao da população do estado?
E, dentro dos planos, o tipo de contratação separa os mais velhos dos mais novos?
"""
)

c1, c2, c3, c4 = st.columns(4)
nc.cartao_metricas([c1, c2, c3, c4], [
    ("População (N)", nc.num(N), "Vínculos ativos a planos médico-hospitalares, RS, set/2026"),
    ("Amostra (n)", nc.num(meta["n"]), "AAS sem reposição, 95% de confiança, margem de 5 pontos"),
    ("Operadoras", "400", "Operadoras com vínculos médico-hospitalares no RS"),
    ("Municípios", nc.num(len(mun)), "Municípios de residência dos beneficiários"),
])

st.subheader("Ficha da base de dados")
st.markdown(
    f"""
| Item | Conteúdo |
|---|---|
| Fonte | Agência Nacional de Saúde Suplementar (ANS), Plano de Dados Abertos: **Informações Consolidadas de Beneficiários** (PDA-024) |
| Links | [Conjunto de dados]({nc.CONJUNTO_URL}) · [Arquivo do RS, set/2026 (.zip)]({nc.FONTE_URL}) · [Dicionário de dados (.ods)]({nc.DICIONARIO_URL}) |
| Contexto e objetivo | As operadoras informam à ANS, pelo Sistema de Informações de Beneficiários (SIB), cada pessoa ligada a cada plano. A ANS publica os totais por operadora, plano, município, sexo, faixa etária e tipo de vínculo |
| Tamanho original | 910.435 linhas e 22 variáveis; 3.828.301 vínculos ativos (médico-hospitalares e odontológicos) |
| Recorte | Competência 09/2026; planos médico-hospitalares; linhas com beneficiários ativos; faixa etária válida |
| População de interesse | Os {nc.num(N)} vínculos ativos de beneficiários a planos médico-hospitalares com residência no RS em setembro de 2026 |
| Unidade amostral | O vínculo de um beneficiário a um plano (quem tem dois planos médicos conta duas vezes) |
| Variáveis | Idade (ponto médio da faixa etária, em anos); sexo; faixa etária; tipo de contratação; tipo de vínculo; modalidade da operadora; abrangência do plano; município de residência (Porto Alegre ou interior); época do plano |
| Referências externas | IBGE, Censo 2022, população do RS por idade ([publicação]({nc.IBGE_URL}) e [tabela SIDRA 9514]({nc.SIDRA_URL})) |
"""
)

st.subheader("Hipóteses (fixadas antes do sorteio da amostra)")
st.markdown(
    r"""
| | Pergunta | Hipóteses | Teste |
|---|---|---|---|
| H1 | A proporção de vínculos de pessoas com 60 anos ou mais é igual à da população do RS (20,15%)? | $H_0: \pi = 0{,}2015$; $H_1: \pi \neq 0{,}2015$ | Z para uma proporção |
| H2 | A proporção de 60 anos ou mais é igual nos planos individuais e nos coletivos empresariais? | $H_0: \pi_I = \pi_E$; $H_1: \pi_I \neq \pi_E$ | Z para duas proporções |
| H3 | A idade média dos beneficiários é igual à da população do RS (38,91 anos)? | $H_0: \mu = 38{,}91$; $H_1: \mu \neq 38{,}91$ | t para uma média |
| H4 | A idade média é igual nos planos individuais e nos coletivos empresariais? | $H_0: \mu_I = \mu_E$; $H_1: \mu_I \neq \mu_E$ | t de Welch |

Nível de significância α = 5% em todos os testes; intervalos de confiança de 95%.
"""
)

st.info("Use o menu à esquerda: **Painel 1** descreve a população, **Painel 2** descreve a amostra e a compara com a "
        "população, e **Painel 3** traz os intervalos, os testes e a comparação entre o que a amostra concluiu e o "
        "que a população mostra.", icon=":material/info:")
