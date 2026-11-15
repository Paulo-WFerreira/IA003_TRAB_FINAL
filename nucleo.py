"""Funcoes comuns aos tres paineis: dados, estatisticas, testes e graficos."""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

DIR = Path(__file__).parent / "dados"

# ------------------------------------------------------------------ cores (populacao = azul, amostra = laranja)
AZUL = "#2a78d6"
LARANJA = "#eb6834"
TINTA = "#0b0b0b"
TINTA2 = "#52514e"
GRADE = "#e6e5e1"
REF = "#52514e"          # linhas de referencia (H0)

FONTE_URL = ("https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/"
             "202609/pda-024-icb-RS-2026_09.zip")
DICIONARIO_URL = ("https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/"
                  "dicionario/dicionario-pda-024-informacoes_consolidadas_de_beneficiarios.ods")
CONJUNTO_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/"
IBGE_URL = "https://biblioteca.ibge.gov.br/visualizacao/periodicos/3102/cd_2022_populacao_idade_sexo_rs.pdf"
SIDRA_URL = "https://sidra.ibge.gov.br/tabela/9514"

FAIXAS = ["Menos de 1 ano", "1 a 4 anos", "5 a 9 anos", "10 a 14 anos", "15 a 17 anos", "18 a 19 anos",
          "20 a 24 anos", "25 a 29 anos", "30 a 34 anos", "35 a 39 anos", "40 a 44 anos", "45 a 49 anos",
          "50 a 54 anos", "55 a 59 anos", "60 a 64 anos", "65 a 69 anos", "70 a 74 anos", "75 a 79 anos",
          "80 anos ou mais"]
ORDENS = {
    "faixa_etaria": FAIXAS,
    "contratacao": ["Coletivo Empresarial", "Coletivo por Adesão", "Individual ou Familiar", "Outros / não identificado"],
    "sexo": ["Feminino", "Masculino"],
    "vinculo": ["Titular", "Dependente", "Não identificado"],
    "local": ["Porto Alegre", "Interior"],
    "vigencia": ["Posterior à Lei 9.656/1998", "Anterior à Lei 9.656/1998"],
    "abrangencia": ["Nacional", "Grupo de estados", "Estadual", "Grupo de municípios", "Municipal", "Não Identificado"],
}
ROTULOS = {"sexo": "Sexo", "faixa_etaria": "Faixa etária", "contratacao": "Tipo de contratação",
           "vinculo": "Tipo de vínculo", "modalidade": "Modalidade da operadora",
           "abrangencia": "Abrangência geográfica do plano", "local": "Município de residência",
           "vigencia": "Época do plano"}

# Referencias externas (IBGE, Censo 2022, Rio Grande do Sul; tabela SIDRA 9514, idades simples)
IBGE = {"pop_rs": 10_882_965, "p60": 0.2015, "p0_14": 0.1752, "p65": 0.1408, "mulheres": 0.517,
        "media_idade": 38.91}
ALFA = 0.05
Z95 = stats.norm.ppf(0.975)


# ------------------------------------------------------------------ formatacao pt-BR
def num(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=1):
    return num(100 * x, dec) + "%"


# ------------------------------------------------------------------ dados
@st.cache_data
def carregar():
    pop = pd.read_csv(DIR / "populacao_agregada.csv")
    am = pd.read_csv(DIR / "amostra_AAS.csv", dtype={"CD_PLANO": str})
    am["vinculos"] = 1
    mun = pd.read_csv(DIR / "municipios.csv", dtype={"CD_MUNICIPIO": str})
    meta = json.loads((DIR / "metadados.json").read_text(encoding="utf-8"))
    return pop, am, mun, meta


def filtros(df_pop, chave):
    """Linha de filtros acima dos graficos. Devolve uma funcao que aplica os filtros a qualquer tabela."""
    c1, c2, c3 = st.columns(3)
    sexo = c1.multiselect("Sexo", ORDENS["sexo"], default=ORDENS["sexo"], key=f"{chave}_sexo")
    contr = c2.multiselect("Tipo de contratação", ORDENS["contratacao"], default=ORDENS["contratacao"],
                           key=f"{chave}_contr")
    local = c3.multiselect("Município de residência", ORDENS["local"], default=ORDENS["local"], key=f"{chave}_local")

    def aplicar(df):
        return df[df.sexo.isin(sexo) & df.contratacao.isin(contr) & df.local.isin(local)]

    ativo = len(sexo) < 2 or len(contr) < 4 or len(local) < 2
    return aplicar, ativo


# ------------------------------------------------------------------ estatisticas descritivas (com pesos)
def quantil(x, w, q):
    o = np.argsort(x, kind="mergesort")
    x, w = np.asarray(x)[o], np.asarray(w, float)[o]
    c = np.cumsum(w) / w.sum()
    return float(x[np.searchsorted(c, q)])


def resumo_idade(df, amostral):
    x = df.idade.to_numpy(float)
    w = df.vinculos.to_numpy(float)
    n = w.sum()
    media = np.average(x, weights=w)
    sq = np.sum(w * (x - media) ** 2)
    dp = math.sqrt(sq / (n - 1)) if amostral else math.sqrt(sq / n)
    assim = np.sum(w * ((x - media) / math.sqrt(sq / n)) ** 3) / n
    q1, med, q3 = (quantil(x, w, q) for q in (0.25, 0.5, 0.75))
    return {"n": n, "media": media, "dp": dp, "mediana": med, "q1": q1, "q3": q3, "iqr": q3 - q1,
            "min": float(x.min()), "max": float(x.max()), "assimetria": assim, "cv": dp / media}


def frequencia(df, col):
    t = df.groupby(col)["vinculos"].sum()
    ordem = ORDENS.get(col)
    if ordem:
        t = t.reindex([c for c in ordem if c in t.index])
    else:
        t = t.sort_values(ascending=False)
    out = pd.DataFrame({"categoria": t.index, "frequencia": t.values})
    out["percentual"] = out.frequencia / out.frequencia.sum()
    return out


def indicadores(df, amostral):
    w = df.vinculos.to_numpy(float)
    n = w.sum()
    r = resumo_idade(df, amostral)
    p = lambda m: float(w[m].sum() / n)
    return {
        "n": n,
        "mulheres": p((df.sexo == "Feminino").to_numpy()),
        "p60": p((df.idade >= 60).to_numpy()),
        "p0_14": p((df.idade < 15).to_numpy()),
        "individual": p((df.contratacao == "Individual ou Familiar").to_numpy()),
        "empresarial": p((df.contratacao == "Coletivo Empresarial").to_numpy()),
        "titular": p((df.vinculo == "Titular").to_numpy()),
        "poa": p((df.local == "Porto Alegre").to_numpy()),
        "idade_media": r["media"], "idade_dp": r["dp"], "idade_mediana": r["mediana"],
    }


def por_grupo(df, col, ordem):
    linhas = []
    for g in ordem:
        s = df[df[col] == g]
        if s.vinculos.sum() == 0:
            continue
        w = s.vinculos.to_numpy(float)
        linhas.append({"grupo": g, "vinculos": w.sum(),
                       "idade_media": np.average(s.idade, weights=w),
                       "p60": w[(s.idade >= 60).to_numpy()].sum() / w.sum()})
    return pd.DataFrame(linhas)


# ------------------------------------------------------------------ parametros populacionais das hipoteses
def parametros(pop):
    w = pop.vinculos.to_numpy(float)
    ind = (pop.contratacao == "Individual ou Familiar").to_numpy()
    emp = (pop.contratacao == "Coletivo Empresarial").to_numpy()
    p60 = (pop.idade >= 60).to_numpy()
    media = lambda m: float(np.average(pop.idade[m], weights=w[m]))
    prop = lambda m: float(w[m & p60].sum() / w[m].sum())
    todos = np.ones(len(pop), bool)
    return {"H1": prop(todos), "H2": (prop(ind), prop(emp)), "H3": media(todos), "H4": (media(ind), media(emp))}


# ------------------------------------------------------------------ testes (Aula 4)
def teste_1prop(x, n, p0):
    p = x / n
    ep_teste = math.sqrt(p0 * (1 - p0) / n)
    z = (p - p0) / ep_teste
    pv = 2 * stats.norm.sf(abs(z))
    ep_ic = math.sqrt(p * (1 - p) / n)
    return {"estimativa": p, "x": x, "n": n, "estat": z, "pvalor": pv, "ep": ep_ic,
            "ic": (p - Z95 * ep_ic, p + Z95 * ep_ic),
            "cond": [("Sucessos esperados sob H0: nπ₀ ≥ 10", n * p0, n * p0 >= 10),
                     ("Fracassos esperados sob H0: n(1−π₀) ≥ 10", n * (1 - p0), n * (1 - p0) >= 10),
                     ("Sucessos na amostra (IC) ≥ 10", x, x >= 10),
                     ("Fracassos na amostra (IC) ≥ 10", n - x, n - x >= 10)]}


def teste_2prop(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    pb = (x1 + x2) / (n1 + n2)
    z = (p1 - p2) / math.sqrt(pb * (1 - pb) * (1 / n1 + 1 / n2))
    pv = 2 * stats.norm.sf(abs(z))
    ep = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p1 - p2
    fisher = stats.fisher_exact([[x1, n1 - x1], [x2, n2 - x2]]).pvalue   # verificacao sem aproximacao normal
    return {"estimativa": d, "p1": p1, "p2": p2, "x1": x1, "x2": x2, "n1": n1, "n2": n2, "pb": pb, "fisher": fisher,
            "estat": z, "pvalor": pv, "ep": ep, "ic": (d - Z95 * ep, d + Z95 * ep),
            "cond": [("Grupo 1, esperados com p̄: n₁p̄ e n₁(1−p̄) ≥ 10", min(n1 * pb, n1 * (1 - pb)),
                      min(n1 * pb, n1 * (1 - pb)) >= 10),
                     ("Grupo 2, esperados com p̄: n₂p̄ e n₂(1−p̄) ≥ 10", min(n2 * pb, n2 * (1 - pb)),
                      min(n2 * pb, n2 * (1 - pb)) >= 10),
                     ("Observados em cada grupo (IC) ≥ 10",
                      min(x1, n1 - x1, x2, n2 - x2), min(x1, n1 - x1, x2, n2 - x2) >= 10)]}


def teste_1media(x, mu0):
    x = np.asarray(x, float)
    n = len(x)
    r = stats.ttest_1samp(x, mu0)
    ep = stats.sem(x)
    tc = stats.t.ppf(0.975, n - 1)
    return {"estimativa": x.mean(), "dp": x.std(ddof=1), "n": n, "estat": r.statistic, "gl": n - 1,
            "pvalor": r.pvalue, "ep": ep, "ic": (x.mean() - tc * ep, x.mean() + tc * ep),
            "cond": [("Tamanho da amostra n ≥ 30 (TCL)", n, n >= 30),
                     ("Assimetria da idade na amostra entre −1 e 1", stats.skew(x), abs(stats.skew(x)) < 1)]}


def teste_2medias(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    r = stats.ttest_ind(a, b, equal_var=False)
    ep = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    gl = (a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)) ** 2 / (
        (a.var(ddof=1) / len(a)) ** 2 / (len(a) - 1) + (b.var(ddof=1) / len(b)) ** 2 / (len(b) - 1))
    tc = stats.t.ppf(0.975, gl)
    d = a.mean() - b.mean()
    return {"estimativa": d, "m1": a.mean(), "m2": b.mean(), "s1": a.std(ddof=1), "s2": b.std(ddof=1),
            "n1": len(a), "n2": len(b), "estat": r.statistic, "gl": gl, "pvalor": r.pvalue, "ep": ep,
            "ic": (d - tc * ep, d + tc * ep),
            "cond": [("Grupo 1 com n ≥ 30", len(a), len(a) >= 30),
                     ("Grupo 2 com n ≥ 30", len(b), len(b) >= 30)]}


def resultados(am, pop):
    """As quatro hipoteses, definidas antes do sorteio (ver painel de inferencia)."""
    par = parametros(pop)
    i = am.idade.to_numpy(float)
    ind = (am.contratacao == "Individual ou Familiar").to_numpy()
    emp = (am.contratacao == "Coletivo Empresarial").to_numpy()
    r = {
        "H1": teste_1prop(int((i >= 60).sum()), len(i), IBGE["p60"]),
        "H2": teste_2prop(int((i[ind] >= 60).sum()), int(ind.sum()), int((i[emp] >= 60).sum()), int(emp.sum())),
        "H3": teste_1media(i, IBGE["media_idade"]),
        "H4": teste_2medias(i[ind], i[emp]),
    }
    alvo = {"H1": par["H1"], "H2": par["H2"][0] - par["H2"][1], "H3": par["H3"], "H4": par["H4"][0] - par["H4"][1]}
    h0 = {"H1": IBGE["p60"], "H2": 0.0, "H3": IBGE["media_idade"], "H4": 0.0}
    for k in r:
        r[k]["param"] = alvo[k]
        r[k]["h0"] = h0[k]
        r[k]["rejeita"] = r[k]["pvalor"] < ALFA
        r[k]["ic_contem_param"] = r[k]["ic"][0] <= alvo[k] <= r[k]["ic"][1]
        r[k]["ic_contem_h0"] = r[k]["ic"][0] <= h0[k] <= r[k]["ic"][1]
    r["par"] = par
    return r


# ------------------------------------------------------------------ simulacao da variabilidade amostral
@st.cache_data
def simular(R=1000, n=385, semente=2026):
    pop, _, _, _ = carregar()
    w = pop.vinculos.to_numpy(np.int64)
    cum = np.cumsum(w)
    N = int(cum[-1])
    idade = pop.idade.to_numpy(float)
    ind = (pop.contratacao == "Individual ou Familiar").to_numpy()
    emp = (pop.contratacao == "Coletivo Empresarial").to_numpy()
    par = parametros(pop)
    rng = np.random.default_rng(semente)
    out = {k: np.empty(R) for k in ("p60", "media", "d60", "dmedia")}
    cob = {k: 0 for k in ("H1", "H2", "H3", "H4")}
    rej = {k: 0 for k in ("H1", "H2", "H3", "H4")}
    for j in range(R):
        lin = np.searchsorted(cum, rng.choice(N, n, replace=False), side="right")
        i, si, se = idade[lin], ind[lin], emp[lin]
        res = {"H1": teste_1prop(int((i >= 60).sum()), n, IBGE["p60"]),
               "H2": teste_2prop(int((i[si] >= 60).sum()), int(si.sum()), int((i[se] >= 60).sum()), int(se.sum())),
               "H3": teste_1media(i, IBGE["media_idade"]),
               "H4": teste_2medias(i[si], i[se])}
        out["p60"][j], out["d60"][j] = res["H1"]["estimativa"], res["H2"]["estimativa"]
        out["media"][j], out["dmedia"][j] = res["H3"]["estimativa"], res["H4"]["estimativa"]
        alvo = {"H1": par["H1"], "H2": par["H2"][0] - par["H2"][1], "H3": par["H3"], "H4": par["H4"][0] - par["H4"][1]}
        for k in res:
            cob[k] += res[k]["ic"][0] <= alvo[k] <= res[k]["ic"][1]
            rej[k] += res[k]["pvalor"] < ALFA
    return out, {k: v / R for k, v in cob.items()}, {k: v / R for k, v in rej.items()}


# ------------------------------------------------------------------ graficos
def layout(fig, titulo=None, altura=320, eixo_x=None, eixo_y=None, legenda=False):
    fig.update_layout(
        template="plotly_white", height=altura, margin=dict(l=8, r=8, t=40 if titulo else 10, b=8),
        title=dict(text=titulo, font=dict(size=14, color=TINTA), x=0, xanchor="left") if titulo else None,
        font=dict(color=TINTA2, size=12), showlegend=legenda, bargap=0.25, bargroupgap=0.08,
        legend=(dict(orientation="h", yanchor="top", y=-0.28, xanchor="left", x=0) if titulo else
                dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1)),
        hoverlabel=dict(bgcolor="white", font_color=TINTA))
    if titulo and legenda:
        fig.update_layout(margin=dict(l=8, r=8, t=40, b=70), height=altura + 40)
    fig.update_xaxes(title=eixo_x, gridcolor=GRADE, zeroline=False, linecolor=GRADE)
    fig.update_yaxes(title=eixo_y, gridcolor=GRADE, zeroline=False, linecolor=GRADE)
    return fig


def limites_faixa(faixa):
    """Intervalo de idades exatas [inicio, fim) de cada faixa; a faixa aberta 80+ e tratada como [80, 90)."""
    if faixa.startswith("Menos"):
        return 0, 1
    if faixa.startswith("80"):
        return 80, 90
    a, b = faixa.replace(" anos", "").split(" a ")
    return int(a), int(b) + 1


YMAX_HIST = 2.8      # mesma escala vertical nos Paineis 1 e 2 (% por ano de idade)


def barras_faixa(tabelas):
    """Histograma da idade com classes de larguras diferentes: altura = % da faixa / largura da faixa,
    de modo que a AREA de cada barra e proporcional ao percentual. tabelas: lista de (nome, df_frequencia, cor)."""
    fig = go.Figure()
    topo = 0
    k = len(tabelas)
    for j, (nome, t, cor) in enumerate(tabelas):
        t = t.set_index("categoria").reindex(FAIXAS, fill_value=0).reset_index()
        tot = t.frequencia.sum()
        perc = 100 * t.frequencia / tot if tot else t.frequencia * 0
        lim = np.array([limites_faixa(f) for f in t.categoria], float)
        larg = lim[:, 1] - lim[:, 0]
        dens = perc.to_numpy() / larg
        topo = max(topo, dens.max())
        x = lim[:, 0] + larg * (j + 0.5) / k                 # cada serie ocupa uma fatia do intervalo
        fig.add_bar(x=x, y=dens, width=larg / k * 0.92, name=nome, marker_color=cor,
                    customdata=np.c_[t.categoria, perc.round(2), t.frequencia],
                    hovertemplate="%{customdata[0]}<br>%{customdata[1]}% dos vínculos (%{customdata[2]:,.0f})"
                                  "<br>%{y:.2f}% por ano de idade<extra>" + nome + "</extra>")
    layout(fig, None, 340, "Idade (anos)", "% dos vínculos por ano de idade", legenda=k > 1)
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(range=[0, 90], dtick=10)
    fig.update_yaxes(range=[0, max(YMAX_HIST, topo * 1.1)])
    return fig


def barras_h(tabelas, xmax=None, altura=None):
    fig = go.Figure()
    for nome, t, cor in tabelas:
        fig.add_bar(y=t.categoria, x=100 * t.percentual, orientation="h", name=nome, marker_color=cor,
                    marker_cornerradius=4, customdata=np.c_[t.frequencia],
                    text=[num(100 * v, 1) + "%" for v in t.percentual], textposition="outside",
                    textfont=dict(color=TINTA2, size=11),
                    hovertemplate="%{y}<br>%{x:.1f}% (%{customdata[0]:,.0f})<extra>" + nome + "</extra>")
    n_cat = len(tabelas[0][1])
    layout(fig, None, altura or max(180, 46 * n_cat * len(tabelas) + 60), "% dos vínculos", None,
           legenda=len(tabelas) > 1)
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(range=[0, xmax or 100])
    return fig


def boxplot(resumos):
    """Boxplot a partir dos quartis (dados agrupados com pesos). resumos: lista de (nome, resumo, cor)."""
    fig = go.Figure()
    for nome, r, cor in resumos:
        lo = max(r["min"], r["q1"] - 1.5 * r["iqr"])
        hi = min(r["max"], r["q3"] + 1.5 * r["iqr"])
        fig.add_trace(go.Box(name=nome, y=[nome], q1=[r["q1"]], median=[r["mediana"]], q3=[r["q3"]], lowerfence=[lo],
                             upperfence=[hi], mean=[r["media"]], marker_color=cor, line_width=2,
                             orientation="h", boxmean=True, hoverinfo="x"))
    layout(fig, None, 90 + 70 * len(resumos), "Idade (anos)", None)
    fig.update_xaxes(range=[0, 90])
    return fig


def grafico_ic(r, escala=1.0, sufixo="", titulo=None):
    """IC de 95% com o valor de H0 (cinza) e o parametro da populacao (azul)."""
    lo, hi = (v * escala for v in r["ic"])
    est, h0, par = r["estimativa"] * escala, r["h0"] * escala, r["param"] * escala
    fig = go.Figure()
    fig.add_shape(type="line", x0=lo, x1=hi, y0=0, y1=0, line=dict(color=LARANJA, width=3))
    fig.add_scatter(x=[est], y=[0], mode="markers", marker=dict(color=LARANJA, size=12),
                    name="Estimativa da amostra", hovertemplate=f"Estimativa: %{{x:.2f}}{sufixo}<extra></extra>")
    fig.add_scatter(x=[lo, hi], y=[0, 0], mode="markers", marker=dict(color=LARANJA, size=9, symbol="line-ns-open"),
                    name="IC de 95%", hovertemplate=f"Limite do IC: %{{x:.2f}}{sufixo}<extra></extra>")
    fig.add_scatter(x=[h0], y=[0.35], mode="markers", marker=dict(color=REF, size=11, symbol="diamond-open"),
                    name="Valor de H₀", hovertemplate=f"H₀: %{{x:.2f}}{sufixo}<extra></extra>")
    fig.add_scatter(x=[par], y=[-0.35], mode="markers", marker=dict(color=AZUL, size=11, symbol="diamond"),
                    name="Parâmetro da população", hovertemplate=f"População: %{{x:.2f}}{sufixo}<extra></extra>")
    vals = [lo, hi, h0, par]
    pad = (max(vals) - min(vals)) * 0.15 or 1
    layout(fig, titulo, 170, sufixo.strip() or None, None, legenda=True)
    fig.update_yaxes(visible=False, range=[-0.8, 0.8])
    fig.update_xaxes(range=[min(vals) - pad, max(vals) + pad])
    fig.update_layout(legend=dict(y=1.15, font=dict(size=11)))
    return fig


def histograma_sim(valores, param, amostra, h0, titulo, eixo, escala=1.0):
    v = np.asarray(valores) * escala
    fig = go.Figure()
    fig.add_histogram(x=v, nbinsx=40, marker_color=AZUL, opacity=0.55, marker_line=dict(color="white", width=1),
                      name="1.000 amostras", hovertemplate="%{x}<br>%{y} amostras<extra></extra>")
    for x, cor, nome, dash in [(param * escala, AZUL, "Parâmetro da população", "solid"),
                               (amostra * escala, LARANJA, "A nossa amostra", "solid"),
                               (h0 * escala, REF, "Valor de H₀", "dot")]:
        fig.add_vline(x=x, line_color=cor, line_width=2, line_dash=dash)
        fig.add_scatter(x=[x], y=[None], mode="lines", line=dict(color=cor, width=2, dash=dash), name=nome)
    layout(fig, titulo, 300, eixo, "Nº de amostras", legenda=True)
    fig.update_layout(legend=dict(font=dict(size=11)))
    return fig


def qqplot(x):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    teo = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
    fig = go.Figure()
    fig.add_scatter(x=teo, y=x, mode="markers", marker=dict(color=LARANJA, size=8, line=dict(color="white", width=1)),
                    name="Amostra", hovertemplate="Quantil teórico %{x:.2f}<br>Idade %{y}<extra></extra>")
    b, a = np.polyfit(teo, x, 1)
    fig.add_scatter(x=[teo.min(), teo.max()], y=[a + b * teo.min(), a + b * teo.max()], mode="lines",
                    line=dict(color=REF, width=2, dash="dot"), name="Referência normal")
    layout(fig, None, 320, "Quantis da normal padrão", "Idade (anos)")
    return fig


def cartao_metricas(cols, dados):
    for c, (rotulo, valor, ajuda) in zip(cols, dados):
        c.metric(rotulo, valor, help=ajuda)
