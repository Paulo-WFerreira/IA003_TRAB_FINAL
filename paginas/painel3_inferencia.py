import pandas as pd
import streamlit as st

import nucleo as nc

pop, am, mun, meta = nc.carregar()
R = nc.resultados(am, pop)
par = R["par"]

st.title("Painel 3 · Inferência estatística e comparação com a população")
st.caption(f"Amostra de {meta['n']} vínculos (semente {meta['semente']}) · α = 5% · intervalos de confiança de 95% · "
           "os parâmetros da população são calculados com a base inteira, só para comparar")

st.markdown(
    """
As quatro hipóteses foram escritas **antes** do sorteio da amostra. Os valores de H₀ vêm de fora da base: a população
do Rio Grande do Sul no Censo 2022 do IBGE (H1 e H3) e a ausência de diferença entre tipos de contratação (H2 e H4).
Todas as alternativas são bilaterais, porque não havia razão prévia para esperar um lado.
"""
)


def decisao(r):
    return "Rejeitar H₀" if r["rejeita"] else "Não rejeitar H₀"


def veredito(r, h0_verdadeira):
    if h0_verdadeira == "pratica":
        if r["rejeita"]:
            return "Rejeitou uma H₀ falsa, mas por uma diferença sem importância prática"
        return "Acerto na prática (tecnicamente, erro tipo II: a diferença real é irrelevante)"
    if r["rejeita"]:
        return "Acerto (rejeitou uma H₀ falsa)" if not h0_verdadeira else "Erro tipo I (rejeitou uma H₀ verdadeira)"
    return "Acerto (não rejeitou uma H₀ verdadeira)" if h0_verdadeira else "Erro tipo II (não rejeitou uma H₀ falsa)"


def condicoes(r):
    linhas = []
    linhas.append(("Independência: AAS sem reposição e n < 10% de N", f"{nc.num(100 * meta['n'] / meta['N'], 3)}%", True))
    for rot, val, ok in r["cond"]:
        linhas.append((rot, nc.num(val, 1) if isinstance(val, float) else nc.num(val), ok))
    return pd.DataFrame({"Condição": [l[0] for l in linhas], "Valor": [l[1] for l in linhas],
                         "Atendida": ["Sim" if l[2] else "Não" for l in linhas]})


def ficha(chave, titulo, pergunta, evento, hip, estat_tex, r, escala, sufixo, dec, h0_verdadeira, nota_h0,
          linhas_resultado, conclusao, comparacao):
    with st.container(border=True):
        st.markdown(f"### {chave} · {titulo}")
        st.markdown(f"**Pergunta:** {pergunta}  \n**Variável e evento:** {evento}")
        a, b = st.columns([1, 1])
        with a:
            st.markdown("**Hipóteses e estatística de teste**")
            st.latex(hip)
            est, _, ic = estat_tex.partition(r"\qquad IC:")
            st.latex(est)
            if ic:
                st.latex(r"IC:" + ic)
            st.markdown("**Condições**")
            st.dataframe(condicoes(r), hide_index=True, width="stretch")
            if "fisher" in r and not all(ok for _, _, ok in r["cond"]):
                st.warning(f"Uma condição da aproximação normal não foi atendida. Como verificação, o teste exato de "
                           f"Fisher, que não depende dela, dá valor-p = {nc.num(r['fisher'], 4)}: a decisão "
                           f"{'se mantém' if (r['fisher'] < nc.ALFA) == r['rejeita'] else 'muda'}.",
                           icon=":material/warning:")
        with b:
            st.markdown("**Resultado na amostra**")
            st.dataframe(pd.DataFrame(linhas_resultado, columns=["Item", "Valor"]), hide_index=True,
                         width="stretch")
            st.plotly_chart(nc.grafico_ic(r, escala, sufixo), width="stretch", key=f"ic_{chave}")
        st.markdown(f"**Decisão:** {decisao(r)} (valor-p = {nc.num(r['pvalor'], 4)} "
                    f"{'<' if r['rejeita'] else '≥'} 0,05).  \n**Conclusão:** {conclusao}")
        st.markdown(f"**Comparação com a população:** {comparacao}  \n**Avaliação da decisão:** "
                    f"{veredito(r, h0_verdadeira)}. {nota_h0}")


# ------------------------------------------------------------------ H1
r = R["H1"]
ficha("H1", "Proporção de 60 anos ou mais × população do RS",
      "Os vínculos a planos de saúde têm a mesma proporção de pessoas com 60 anos ou mais que a população do RS?",
      "idade ≥ 60 anos (faixas de 60 a 64 em diante); sucesso = vínculo de pessoa com 60 anos ou mais",
      r"H_0:\ \pi = 0{,}2015 \qquad H_1:\ \pi \neq 0{,}2015",
      r"Z=\frac{\hat p-\pi_0}{\sqrt{\pi_0(1-\pi_0)/n}}\qquad IC:\ \hat p \pm 1{,}96\sqrt{\hat p(1-\hat p)/n}",
      r, 100, " %", 2, False,
      f"Na população, a proporção é {nc.pct(par['H1'], 2)}, e não 20,15%: H₀ é falsa por "
      f"{nc.num(100 * (nc.IBGE['p60'] - par['H1']), 1)} pontos.",
      [("Vínculos com 60+ na amostra", f"{r['x']} de {r['n']}"), ("Proporção amostral p̂", nc.pct(r["estimativa"], 2)),
       ("Estatística Z", nc.num(r["estat"], 3)), ("Valor-p (bilateral)", nc.num(r["pvalor"], 4)),
       ("IC de 95% para π", f"{nc.pct(r['ic'][0], 2)} a {nc.pct(r['ic'][1], 2)}")],
      f"com 95% de confiança, a proporção de vínculos de pessoas com 60 anos ou mais está entre "
      f"{nc.pct(r['ic'][0], 1)} e {nc.pct(r['ic'][1], 1)}. A amostra {'mostra' if r['rejeita'] else 'não mostra'} "
      "evidência de que ela seja diferente dos 20,15% da população do RS.",
      f"o parâmetro é {nc.pct(par['H1'], 2)}; a estimativa errou por {nc.num(100 * abs(r['estimativa'] - par['H1']), 2)} "
      f"ponto. O IC {'contém' if r['ic_contem_param'] else 'não contém'} o parâmetro e "
      f"{'também contém' if r['ic_contem_h0'] else 'não contém'} o valor de H₀.")

# ------------------------------------------------------------------ H2
r = R["H2"]
ficha("H2", "Proporção de 60 anos ou mais: individuais × coletivos empresariais",
      "A proporção de pessoas com 60 anos ou mais é a mesma nos planos individuais ou familiares e nos coletivos "
      "empresariais?",
      "idade ≥ 60 anos, comparada entre os grupos \"Individual ou Familiar\" (I) e \"Coletivo Empresarial\" (E)",
      r"H_0:\ \pi_I = \pi_E \qquad H_1:\ \pi_I \neq \pi_E",
      r"Z=\frac{\hat p_I-\hat p_E}{\sqrt{\bar p(1-\bar p)(1/n_I+1/n_E)}}\qquad IC:\ (\hat p_I-\hat p_E)\pm 1{,}96\,"
      r"\sqrt{\tfrac{\hat p_I(1-\hat p_I)}{n_I}+\tfrac{\hat p_E(1-\hat p_E)}{n_E}}",
      r, 100, " p.p.", 2, False,
      f"Na população, a diferença é de {nc.num(100 * r['param'], 1)} pontos "
      f"({nc.pct(par['H2'][0], 1)} × {nc.pct(par['H2'][1], 1)}): H₀ é falsa.",
      [("Individuais: 60+ / n", f"{r['x1']} de {r['n1']} ({nc.pct(r['p1'], 1)})"),
       ("Empresariais: 60+ / n", f"{r['x2']} de {r['n2']} ({nc.pct(r['p2'], 1)})"),
       ("Diferença p̂(I) − p̂(E)", nc.num(100 * r["estimativa"], 2) + " p.p."),
       ("Proporção agrupada p̄", nc.pct(r["pb"], 2)), ("Estatística Z", nc.num(r["estat"], 3)),
       ("Valor-p (bilateral)", nc.num(r["pvalor"], 4)),
       ("Valor-p do teste exato de Fisher", nc.num(r["fisher"], 4)),
       ("IC de 95% para a diferença", f"{nc.num(100 * r['ic'][0], 2)} a {nc.num(100 * r['ic'][1], 2)} p.p.")],
      f"os planos individuais têm proporcionalmente mais pessoas com 60 anos ou mais. Com 95% de confiança, a diferença "
      f"está entre {nc.num(100 * r['ic'][0], 1)} e {nc.num(100 * r['ic'][1], 1)} pontos percentuais.",
      f"a diferença na população é de {nc.num(100 * r['param'], 1)} pontos. O IC "
      f"{'contém' if r['ic_contem_param'] else 'não contém'} esse valor e "
      f"{'contém' if r['ic_contem_h0'] else 'não contém'} o zero.")

# ------------------------------------------------------------------ H3
r = R["H3"]
ficha("H3", "Idade média × população do RS",
      "A idade média dos beneficiários de planos médico-hospitalares é igual à da população do RS?",
      "idade em anos (ponto médio da faixa etária)",
      r"H_0:\ \mu = 38{,}91 \qquad H_1:\ \mu \neq 38{,}91",
      r"T=\frac{\bar x-\mu_0}{s/\sqrt n}\ \ (gl=n-1)\qquad IC:\ \bar x \pm t_{0{,}975;\,n-1}\,\frac{s}{\sqrt n}",
      r, 1, " anos", 2, "pratica",
      f"Na população, a média é {nc.num(par['H3'], 2)} anos: a diferença para 38,91 é de "
      f"{nc.num(abs(nc.IBGE['media_idade'] - par['H3']), 2)} ano, tecnicamente H₀ é falsa, mas a diferença não tem "
      "importância prática (menos de meio ano numa variável com desvio padrão de 21 anos).",
      [("Média amostral x̄", nc.num(r["estimativa"], 2) + " anos"), ("Desvio padrão s", nc.num(r["dp"], 2)),
       ("Estatística T", nc.num(r["estat"], 3)), ("Graus de liberdade", str(r["gl"])),
       ("Valor-p (bilateral)", nc.num(r["pvalor"], 4)),
       ("IC de 95% para μ", f"{nc.num(r['ic'][0], 2)} a {nc.num(r['ic'][1], 2)} anos")],
      f"com 95% de confiança, a idade média dos beneficiários está entre {nc.num(r['ic'][0], 1)} e "
      f"{nc.num(r['ic'][1], 1)} anos, faixa que inclui a média do estado. Não há evidência de que quem tem plano seja, "
      "em média, mais velho ou mais novo que a população gaúcha.",
      f"a média da população é {nc.num(par['H3'], 2)} anos; a estimativa errou por "
      f"{nc.num(abs(r['estimativa'] - par['H3']), 2)} ano. O IC {'contém' if r['ic_contem_param'] else 'não contém'} "
      "o parâmetro.")

# ------------------------------------------------------------------ H4
r = R["H4"]
ficha("H4", "Idade média: individuais × coletivos empresariais",
      "A idade média é a mesma nos planos individuais ou familiares e nos coletivos empresariais?",
      "idade em anos, comparada entre os grupos \"Individual ou Familiar\" (I) e \"Coletivo Empresarial\" (E)",
      r"H_0:\ \mu_I = \mu_E \qquad H_1:\ \mu_I \neq \mu_E",
      r"T=\frac{\bar x_I-\bar x_E}{\sqrt{s_I^2/n_I+s_E^2/n_E}}\ \ (\text{Welch})\qquad IC:\ (\bar x_I-\bar x_E)\pm "
      r"t_{0{,}975;\,gl}\sqrt{s_I^2/n_I+s_E^2/n_E}",
      r, 1, " anos", 2, False,
      f"Na população, a diferença é de {nc.num(r['param'], 1)} anos ({nc.num(par['H4'][0], 1)} × "
      f"{nc.num(par['H4'][1], 1)}): H₀ é falsa.",
      [("Individuais: média (s; n)", f"{nc.num(r['m1'], 2)} ({nc.num(r['s1'], 1)}; {r['n1']})"),
       ("Empresariais: média (s; n)", f"{nc.num(r['m2'], 2)} ({nc.num(r['s2'], 1)}; {r['n2']})"),
       ("Diferença x̄(I) − x̄(E)", nc.num(r["estimativa"], 2) + " anos"), ("Estatística T (Welch)", nc.num(r["estat"], 3)),
       ("Graus de liberdade (Welch)", nc.num(r["gl"], 1)), ("Valor-p (bilateral)", nc.num(r["pvalor"], 4)),
       ("IC de 95% para a diferença", f"{nc.num(r['ic'][0], 2)} a {nc.num(r['ic'][1], 2)} anos")],
      f"na amostra, os planos individuais têm média {nc.num(r['estimativa'], 1)} anos maior, mas o IC vai de "
      f"{nc.num(r['ic'][0], 1)} a {nc.num(r['ic'][1], 1)} anos e inclui o zero: a amostra não tem precisão para afirmar "
      "a diferença." if not r["rejeita"] else
      f"os planos individuais têm idade média maior; com 95% de confiança, a diferença está entre "
      f"{nc.num(r['ic'][0], 1)} e {nc.num(r['ic'][1], 1)} anos.",
      f"a diferença na população é de {nc.num(r['param'], 1)} anos, e o IC "
      f"{'contém' if r['ic_contem_param'] else 'não contém'} esse valor. Com só {r['n1']} vínculos individuais na "
      "amostra, o erro padrão da diferença é grande.")

# ------------------------------------------------------------------ resumo
st.subheader("Resumo: o que a amostra concluiu e o que a população mostra")
lin = []
for k, nome, esc, suf in [("H1", "π (60+) = 20,15%", 100, "%"), ("H2", "π(I) − π(E) (60+) = 0", 100, " p.p."),
                          ("H3", "μ (idade) = 38,91", 1, " anos"), ("H4", "μ(I) − μ(E) (idade) = 0", 1, " anos")]:
    r = R[k]
    lin.append({"Hipótese": f"{k}: {nome}", "Estimativa": nc.num(esc * r["estimativa"], 2) + suf,
                "IC de 95%": f"{nc.num(esc * r['ic'][0], 2)} a {nc.num(esc * r['ic'][1], 2)}",
                "Valor-p": nc.num(r["pvalor"], 4), "Decisão": decisao(r),
                "Parâmetro na população": nc.num(esc * r["param"], 2) + suf,
                "IC contém o parâmetro?": "Sim" if r["ic_contem_param"] else "Não",
                "Avaliação": veredito(r, "pratica" if k == "H3" else False).split(" (")[0]})
st.dataframe(pd.DataFrame(lin), hide_index=True, width="stretch")
st.markdown(
    """
- **Os quatro intervalos de confiança contêm o parâmetro da população.** As estimativas pontuais erraram, como sempre
  erram, mas os intervalos cumpriram o que prometem.
- **H2 acertou:** a diferença entre individuais e empresariais é grande (cerca de 20 pontos) e a amostra a detectou.
  A condição de 10 esperados falhou no grupo individual (7,2), mas o teste exato de Fisher confirma a decisão.
- **H3 acertou na prática:** a idade média dos beneficiários e a do estado diferem em menos de meio ano.
- **H1 e H4 são erros tipo II:** as diferenças existem na população (2,7 pontos em H1 e 7,1 anos em H4), mas a
  amostra não teve poder para detectá-las. Em H4, só 58 dos 385 vínculos são de planos individuais.
"""
)

# ------------------------------------------------------------------ variabilidade amostral
st.subheader("Variabilidade amostral: e se fossem outras amostras?")
st.markdown("Foram sorteadas outras 1.000 amostras de 385 vínculos da mesma população, com o mesmo procedimento. "
            "Os histogramas mostram onde caem as estimativas; a linha laranja marca a nossa amostra.")
sim, cob, rej = nc.simular()
a, b = st.columns(2)
a.plotly_chart(nc.histograma_sim(sim["p60"], par["H1"], R["H1"]["estimativa"], nc.IBGE["p60"],
                                 "Proporção de 60 anos ou mais (H1)", "%", 100), width="stretch")
b.plotly_chart(nc.histograma_sim(sim["media"], par["H3"], R["H3"]["estimativa"], nc.IBGE["media_idade"],
                                 "Idade média (H3)", "anos"), width="stretch")
a, b = st.columns(2)
a.plotly_chart(nc.histograma_sim(sim["d60"], par["H2"][0] - par["H2"][1], R["H2"]["estimativa"], 0,
                                 "Diferença de proporções, individuais − empresariais (H2)", "p.p.", 100),
               width="stretch")
b.plotly_chart(nc.histograma_sim(sim["dmedia"], par["H4"][0] - par["H4"][1], R["H4"]["estimativa"], 0,
                                 "Diferença de idades médias, individuais − empresariais (H4)", "anos"),
               width="stretch")
st.dataframe(pd.DataFrame({
    "Hipótese": ["H1", "H2", "H3", "H4"],
    "IC de 95% contém o parâmetro": [nc.pct(cob[k], 1) for k in ("H1", "H2", "H3", "H4")],
    "Amostras que rejeitam H₀ (α = 5%)": [nc.pct(rej[k], 1) for k in ("H1", "H2", "H3", "H4")]}),
    hide_index=True, width="stretch")
st.caption("Como H₀ é falsa nas quatro hipóteses, a taxa de rejeição é o poder do teste com n = 385. Em H3 a diferença "
           "é tão pequena que o teste quase nunca a detecta; em H1 e H4 o poder fica baixo ou médio, e não rejeitar era "
           "o resultado mais provável ou quase tão provável quanto rejeitar.")

# ------------------------------------------------------------------ limitacoes
st.subheader("Limitações")
st.markdown(
    """
- **Idade aproximada:** a ANS publica faixas etárias, não a idade. Usou-se o ponto médio de cada faixa (85 anos para
  "80 ou mais"); mudar esse valor para 82,5 ou 90 altera a média da população em menos de 0,2 ano.
- **Unidade é o vínculo, não a pessoa:** quem tem dois planos médico-hospitalares aparece duas vezes.
- **Referências de 2022:** as hipóteses H1 e H3 comparam beneficiários de 2026 com a população do Censo 2022, que
  envelheceu desde então. Isso pesa mais em H1: a parcela de 60 anos ou mais do estado hoje deve ser maior que 20,15%.
- **Poder limitado:** a amostra foi dimensionada para estimar uma proporção com margem de 5 pontos. Diferenças
  menores que isso, ou comparações com grupos pequenos (58 vínculos individuais), ficam fora do alcance (H1 e H4).
- **Comparações múltiplas:** com quatro testes a 5%, a chance de pelo menos um falso positivo, se todas as H₀ fossem
  verdadeiras, seria de 1 − 0,95⁴ = 18,5%.
- **Dados administrativos:** os números vêm do que as operadoras informam à ANS e descrevem associação, não causa.
"""
)
