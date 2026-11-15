import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import nucleo as nc

pop, am, mun, meta = nc.carregar()

st.title("Painel 1 · Análise descritiva da população")
st.caption(f"{nc.num(meta['N'])} vínculos ativos a planos médico-hospitalares no RS, set/2026 · Fonte: ANS, "
           "Informações Consolidadas de Beneficiários")

aplicar, ativo = nc.filtros(pop, "p1")
p = aplicar(pop)
if p.vinculos.sum() == 0:
    st.warning("Nenhum vínculo com esses filtros.")
    st.stop()
if ativo:
    st.caption(f"Filtro aplicado: {nc.num(p.vinculos.sum())} vínculos ({nc.pct(p.vinculos.sum() / meta['N'])} da população).")

ind = nc.indicadores(p, amostral=False)
c = st.columns(5)
nc.cartao_metricas(c, [
    ("Vínculos", nc.num(ind["n"]), "Tamanho da população (ou do recorte filtrado)"),
    ("Mulheres", nc.pct(ind["mulheres"]), "Proporção de vínculos de mulheres"),
    ("60 anos ou mais", nc.pct(ind["p60"]), "Proporção de vínculos de pessoas com 60 anos ou mais"),
    ("Idade média", nc.num(ind["idade_media"], 1) + " anos", "Média da idade (ponto médio da faixa etária)"),
    ("Coletivo empresarial", nc.pct(ind["empresarial"]), "Proporção de vínculos em planos coletivos empresariais"),
])

# ------------------------------------------------------------------ idade
st.subheader("Idade")
r = nc.resumo_idade(p, amostral=False)
col1, col2 = st.columns([3, 2])
with col1:
    t = nc.frequencia(p, "faixa_etaria")
    st.plotly_chart(nc.barras_faixa([("População", t, nc.AZUL)]), width="stretch")
with col2:
    st.plotly_chart(nc.boxplot([("População", r, nc.AZUL)]), width="stretch")
    medidas = pd.DataFrame({
        "Medida": ["Média", "Mediana", "Desvio padrão (divisor N)", "1º quartil", "3º quartil",
                   "Amplitude interquartil", "Coeficiente de variação", "Assimetria"],
        "Valor": [nc.num(r["media"], 2), nc.num(r["mediana"], 1), nc.num(r["dp"], 2), nc.num(r["q1"], 1),
                  nc.num(r["q3"], 1), nc.num(r["iqr"], 1), nc.pct(r["cv"]), nc.num(r["assimetria"], 3)]})
    st.dataframe(medidas, hide_index=True, width="stretch")
st.caption("As faixas etárias da ANS têm larguras diferentes (de 1 a 10 anos). Por isso o histograma usa a "
           "densidade: a altura de cada barra é o percentual da faixa dividido pela largura dela, e a área da barra é "
           "proporcional ao percentual. A faixa aberta de 80 anos ou mais foi desenhada de 80 a 90. "
           "A idade de cada vínculo é o ponto médio da faixa etária informada pela ANS (por exemplo, 22,5 anos para a "
           "faixa de 20 a 24). Para a faixa aberta de 80 anos ou mais, foi usado 85. Trocar por 82,5 ou 90 muda a "
           "média da população em menos de 0,2 ano. Os quartis são os pontos médios das faixas que os contêm.")

# ------------------------------------------------------------------ qualitativas
st.subheader("Variáveis qualitativas")
abas = st.tabs([nc.ROTULOS[v] for v in ["contratacao", "sexo", "vinculo", "modalidade", "abrangencia", "local", "vigencia"]])
for aba, var in zip(abas, ["contratacao", "sexo", "vinculo", "modalidade", "abrangencia", "local", "vigencia"]):
    with aba:
        t = nc.frequencia(p, var)
        a, b = st.columns([3, 2])
        a.plotly_chart(nc.barras_h([("População", t, nc.AZUL)]), width="stretch")
        tab = t.assign(frequencia=t.frequencia.map(nc.num), percentual=t.percentual.map(lambda v: nc.pct(v, 2)))
        b.dataframe(tab.rename(columns={"categoria": nc.ROTULOS[var], "frequencia": "Vínculos",
                                        "percentual": "%"}), hide_index=True, width="stretch")

# ------------------------------------------------------------------ cruzamentos
st.subheader("Idade e tipo de contratação")
g = nc.por_grupo(p, "contratacao", nc.ORDENS["contratacao"][:3])
a, b = st.columns(2)
fig = go.Figure(go.Bar(x=g.grupo, y=100 * g.p60, marker_color=nc.AZUL, marker_cornerradius=4,
                       text=[nc.pct(v) for v in g.p60], textposition="outside",
                       hovertemplate="%{x}<br>%{y:.1f}% com 60 anos ou mais<extra></extra>"))
a.plotly_chart(nc.layout(fig, "Proporção com 60 anos ou mais", 320, None, "%").update_yaxes(range=[0, max(45, 115 * g.p60.max())]),
               width="stretch")
fig = go.Figure(go.Bar(x=g.grupo, y=g.idade_media, marker_color=nc.AZUL, marker_cornerradius=4,
                       text=[nc.num(v, 1) for v in g.idade_media], textposition="outside",
                       hovertemplate="%{x}<br>Idade média %{y:.1f} anos<extra></extra>"))
b.plotly_chart(nc.layout(fig, "Idade média (anos)", 320, None, "anos").update_yaxes(range=[0, max(60, 1.15 * g.idade_media.max())]),
               width="stretch")
st.caption("Os planos individuais e os coletivos por adesão concentram os mais velhos; os coletivos empresariais "
           "acompanham a idade de quem trabalha e de seus dependentes.")

st.subheader("Onde moram os beneficiários")
top = mun.head(15).iloc[::-1]
fig = go.Figure(go.Bar(y=top.NM_MUNICIPIO, x=top.vinculos, orientation="h", marker_color=nc.AZUL,
                       marker_cornerradius=4, hovertemplate="%{y}<br>%{x:,.0f} vínculos<extra></extra>"))
st.plotly_chart(nc.layout(fig, "Os 15 municípios com mais vínculos (população total, sem filtros)", 440,
                          "Vínculos", None), width="stretch")

with st.expander("Comparação com a população do RS (IBGE, Censo 2022)"):
    ibge = pd.DataFrame({
        "Indicador": ["Idade média (mesmas faixas)", "60 anos ou mais", "0 a 14 anos", "Mulheres"],
        "Beneficiários (ANS, 2026)": [nc.num(ind["idade_media"], 2), nc.pct(ind["p60"], 2), nc.pct(ind["p0_14"], 2),
                                      nc.pct(ind["mulheres"], 2)],
        "População do RS (IBGE, 2022)": [nc.num(nc.IBGE["media_idade"], 2), nc.pct(nc.IBGE["p60"], 2),
                                         nc.pct(nc.IBGE["p0_14"], 2), nc.pct(nc.IBGE["mulheres"], 1)]})
    st.dataframe(ibge, hide_index=True, width="stretch")
    st.caption("Valores do IBGE calculados a partir da tabela SIDRA 9514 (idades simples), agrupados nas mesmas faixas "
               "da ANS. Com os filtros ativos, a coluna da ANS mostra o recorte filtrado.")
