import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import nucleo as nc

pop, am, mun, meta = nc.carregar()
N, n = meta["N"], meta["n"]

st.title("Painel 2 · Análise descritiva da amostra")
st.caption(f"Amostra aleatória simples de {n} vínculos, sorteada da população de {nc.num(N)} · "
           f"semente {meta['semente']}")

# ------------------------------------------------------------------ dimensionamento
st.subheader("Tamanho da amostra")
a, b = st.columns([3, 2])
with a:
    st.latex(r"n_0=\frac{z^2\,p(1-p)}{E^2}=\frac{1{,}96^2\times0{,}25}{0{,}05^2}=384{,}16")
    st.latex(r"n=\frac{n_0}{1+\frac{n_0-1}{N}}=\frac{384{,}16}{1+\frac{383{,}16}{2.667.053}}=384{,}10"
             r"\;\rightarrow\;385")
    st.markdown(
        """
| Parâmetro | Valor | Justificativa |
|---|---|---|
| Confiança | 95% (z = 1,96) | Padrão em pesquisa e na disciplina; corresponde a α = 5% nos testes |
| Margem de erro | 5 pontos percentuais | Precisão usual para estimar proporções, com uma amostra que dá para examinar caso a caso |
| Proporção | p = 0,5 | Pior caso: na prática a proporção é desconhecida, e 0,5 maximiza p(1−p) |
| População | N = 2.667.053 | Correção para população finita (quase não muda nada, porque N é muito grande) |
"""
    )
with b:
    st.markdown(
        f"""
**Conferência para a média da idade:** com n = {n} e o desvio padrão de cerca de 21 anos, a margem de erro do IC
de 95% fica em torno de ±2,1 anos.

**Fração amostral:** {nc.num(100 * n / N, 3)}% da população, muito abaixo do limite de 10% para tratar as
observações como independentes.
"""
    )

st.subheader("Seleção da amostra aleatória simples")
st.markdown(
    f"""
1. As hipóteses e o α foram fixados **antes** do sorteio (Painel 3).
2. A base da ANS traz contagens: cada linha agrupa vários vínculos iguais. As linhas foram postas numa ordem fixa
   (operadora, plano, município, sexo, faixa etária...), e cada vínculo ganhou uma posição de 1 a {nc.num(N)}.
3. Foram sorteadas **{n} posições distintas**, sem reposição, com o gerador do NumPy e a semente **{meta['semente']}**.
   Cada vínculo teve a mesma probabilidade de entrar: {n}/{nc.num(N)} = {nc.num(100 * n / N, 4)}%.
4. Cada posição foi levada à linha do cadastro que a contém. O sorteio foi feito uma única vez.
"""
)
with st.expander("Código do sorteio (prepara_base.py)"):
    st.code(
        """rng = np.random.default_rng(20261108)                   # semente fixada antes do sorteio
pos = np.sort(rng.choice(N, size=385, replace=False))   # 385 posicoes distintas entre 0 e N-1
linha = np.searchsorted(np.cumsum(cadastro["QT_BENEFICIARIO_ATIVO"]), pos, side="right")
amostra = cadastro.iloc[linha]                           # um vinculo por posicao sorteada""",
        language="python")
    st.dataframe(am.drop(columns="vinculos"), hide_index=True, width="stretch", height=260)
st.download_button("Baixar a amostra (CSV)", am.drop(columns="vinculos").to_csv(index=False).encode("utf-8"),
                   "amostra_AAS.csv", "text/csv")

# ------------------------------------------------------------------ descritiva da amostra
st.divider()
st.subheader("Descrição da amostra, nas mesmas escalas da população")
aplicar, ativo = nc.filtros(pop, "p2")
s, p = aplicar(am), aplicar(pop)
if len(s) < 2:
    st.warning("Poucos vínculos na amostra com esses filtros.")
    st.stop()
if ativo:
    st.caption(f"Filtro aplicado: {len(s)} vínculos da amostra e {nc.num(p.vinculos.sum())} da população.")

ia, ip = nc.indicadores(s, amostral=True), nc.indicadores(p, amostral=False)
c = st.columns(5)
dif = lambda k: f"{nc.num(100 * (ia[k] - ip[k]), 1)} p.p. vs. população"
for col, (rot, k) in zip(c[1:3] + c[4:], [("Mulheres", "mulheres"), ("60 anos ou mais", "p60"),
                                         ("Coletivo empresarial", "empresarial")]):
    col.metric(rot, nc.pct(ia[k]), dif(k), delta_color="off")
c[0].metric("Vínculos na amostra", nc.num(ia["n"]))
c[3].metric("Idade média", nc.num(ia["idade_media"], 1) + " anos",
            f"{nc.num(ia['idade_media'] - ip['idade_media'], 1)} ano vs. população", delta_color="off")

ts, tp = nc.frequencia(s, "faixa_etaria"), nc.frequencia(p, "faixa_etaria")
rs, rp = nc.resumo_idade(s, amostral=True), nc.resumo_idade(p, amostral=False)
a, b = st.columns([3, 2])
a.plotly_chart(nc.barras_faixa([("População", tp, nc.AZUL), ("Amostra", ts, nc.LARANJA)]),
               width="stretch")
with b:
    st.plotly_chart(nc.boxplot([("População", rp, nc.AZUL), ("Amostra", rs, nc.LARANJA)]), width="stretch")
    med = pd.DataFrame({
        "Medida": ["Média", "Mediana", "Desvio padrão", "1º quartil", "3º quartil", "Assimetria"],
        "População": [nc.num(rp[k], 2) for k in ("media", "mediana", "dp", "q1", "q3")] + [nc.num(rp["assimetria"], 3)],
        "Amostra": [nc.num(rs[k], 2) for k in ("media", "mediana", "dp", "q1", "q3")] + [nc.num(rs["assimetria"], 3)]})
    st.dataframe(med, hide_index=True, width="stretch")
st.caption("Na amostra, o desvio padrão usa o divisor n − 1; na população, o divisor N.")

st.subheader("Variáveis qualitativas: população × amostra")
vars_ = ["contratacao", "sexo", "vinculo", "modalidade", "abrangencia", "local", "vigencia"]
for aba, var in zip(st.tabs([nc.ROTULOS[v] for v in vars_]), vars_):
    with aba:
        tp_, ts_ = nc.frequencia(p, var), nc.frequencia(s, var)
        ts_ = ts_.set_index("categoria").reindex(tp_.categoria, fill_value=0).reset_index()
        ts_["percentual"] = ts_.frequencia / max(ts_.frequencia.sum(), 1)
        x, y = st.columns([1, 1])
        x.plotly_chart(nc.barras_h([("População", tp_, nc.AZUL), ("Amostra", ts_, nc.LARANJA)]),
                       width="stretch")
        tab = pd.DataFrame({"Categoria": tp_.categoria, "Pop. %": tp_.percentual.map(lambda v: nc.pct(v, 1)),
                            "Am. n": ts_.frequencia.astype(int), "Am. %": ts_.percentual.map(lambda v: nc.pct(v, 1)),
                            "Dif. p.p.": (100 * (ts_.percentual - tp_.percentual)).map(lambda v: nc.num(v, 1))})
        y.dataframe(tab, hide_index=True, width="stretch")

st.subheader("Idade e tipo de contratação na amostra")
gs = nc.por_grupo(s, "contratacao", nc.ORDENS["contratacao"][:3])
gp = nc.por_grupo(p, "contratacao", nc.ORDENS["contratacao"][:3])
a, b = st.columns(2)
for col, campo, tit, esc, rng in [(a, "p60", "Proporção com 60 anos ou mais (%)", 100,
                                    [0, max(45, 115 * max(gp.p60.max(), gs.p60.max()))]),
                                   (b, "idade_media", "Idade média (anos)", 1,
                                    [0, max(60, 1.15 * max(gp.idade_media.max(), gs.idade_media.max()))])]:
    fig = go.Figure()
    fig.add_bar(x=gp.grupo, y=esc * gp[campo], name="População", marker_color=nc.AZUL, marker_cornerradius=4,
                hovertemplate="%{x}<br>População: %{y:.1f}<extra></extra>")
    fig.add_bar(x=gs.grupo, y=esc * gs[campo], name="Amostra", marker_color=nc.LARANJA, marker_cornerradius=4,
                customdata=gs.vinculos, hovertemplate="%{x}<br>Amostra: %{y:.1f} (n = %{customdata})<extra></extra>")
    col.plotly_chart(nc.layout(fig, tit, 320, None, None, legenda=True).update_yaxes(range=rng),
                     width="stretch")
st.caption(f"Na amostra: {', '.join(f'{g} n = {int(v)}' for g, v in zip(gs.grupo, gs.vinculos))}. Grupos pequenos "
           "oscilam mais em relação à população.")

st.subheader("Forma da distribuição da idade na amostra")
a, b = st.columns([3, 2])
a.plotly_chart(nc.qqplot(s.idade), width="stretch")
b.markdown(
    """
O QQ-plot compara os quantis da idade na amostra com os de uma normal. Os pontos acompanham a reta no centro e se
afastam nas pontas: a idade tem limites (0 e cerca de 85 anos) e é mais "achatada" que a normal, com muitos
vínculos de crianças e de adultos jovens.

Para os testes de média do Painel 3, isso não é problema: com n = 385, pelo Teorema Central do Limite, a média
amostral é aproximadamente normal mesmo que a idade não seja.
"""
)
