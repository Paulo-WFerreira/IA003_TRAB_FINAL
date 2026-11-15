"""IA003 - Trabalho final - preparo da base e sorteio da AAS

Fonte: ANS, Dados Abertos, "Informacoes Consolidadas de Beneficiarios" (PDA-024), RS, competencia 2026-09.
Populacao: vinculos ativos de beneficiarios a planos medico-hospitalares no RS em set/2026.

Uso:
    pip install pandas numpy
    python prepara_base.py                  # baixa o arquivo, monta a populacao e sorteia a AAS
    python prepara_base.py --zip arquivo.zip # usa um zip ja baixado

Gera em dados/:
    populacao_agregada.csv    -> populacao resumida pelas variaveis do trabalho (coluna "vinculos")
    municipios.csv            -> vinculos por municipio de residencia
    amostra_AAS.csv           -> a AAS sorteada (um vinculo por linha)
    metadados.json            -> N, n, semente, fonte e versoes
"""
import argparse
import json
import math
import re
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

URL = ("https://dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios-024/"
       "202609/pda-024-icb-RS-2026_09.zip")
SEMENTE = 20261108          # fixada antes do sorteio (data do sorteio: 08/11/2026)
CONF_Z, MARGEM, P = 1.96, 0.05, 0.5
A = "QT_BENEFICIARIO_ATIVO"

FAIXAS = ["Menos de 1 ano", "1 a 4 anos", "5 a 9 anos", "10 a 14 anos", "15 a 17 anos", "18 a 19 anos",
          "20 a 24 anos", "25 a 29 anos", "30 a 34 anos", "35 a 39 anos", "40 a 44 anos", "45 a 49 anos",
          "50 a 54 anos", "55 a 59 anos", "60 a 64 anos", "65 a 69 anos", "70 a 74 anos", "75 a 79 anos",
          "80 anos ou mais"]


def ponto_medio(faixa):
    """Idade (anos) atribuida a cada faixa: ponto medio do intervalo de idades exatas."""
    if faixa.startswith("Menos"):
        return 0.5
    if faixa.startswith("80"):
        return 85.0                      # faixa aberta: valor assumido (ver sensibilidade no trabalho)
    a, b = map(int, re.match(r"(\d+) a (\d+)", faixa).groups())
    return (a + b + 1) / 2


def le_populacao(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        nome = z.namelist()[0]
        with z.open(nome) as f:
            d = pd.read_csv(f, sep=";", dtype=str)
    d[A] = pd.to_numeric(d[A])
    d = d[(d.COBERTURA_ASSIST_PLAN == "Médico-hospitalar") & (d[A] > 0) & d.DE_FAIXA_ETARIA.isin(FAIXAS)].copy()
    # ordem fixa do cadastro, para que a posicao sorteada sempre aponte para o mesmo vinculo
    chave = ["CD_OPERADORA", "CD_PLANO", "TP_VIGENCIA_PLANO", "CD_MUNICIPIO", "TP_SEXO", "DE_FAIXA_ETARIA",
             "DE_FAIXA_ETARIA_REAJ", "TIPO_VINCULO", "DE_CONTRATACAO_PLANO", "DE_SEGMENTACAO_PLANO",
             "DE_ABRG_GEOGRAFICA_PLANO"]
    d = d.sort_values(chave, kind="mergesort").reset_index(drop=True)
    d["idade"] = d.DE_FAIXA_ETARIA.map(ponto_medio)
    d["faixa_etaria"] = d.DE_FAIXA_ETARIA
    d["sexo"] = d.TP_SEXO.map({"F": "Feminino", "M": "Masculino"})
    d["contratacao"] = d.DE_CONTRATACAO_PLANO.where(
        d.DE_CONTRATACAO_PLANO.isin(["Coletivo Empresarial", "Coletivo por Adesão", "Individual ou Familiar"]),
        "Outros / não identificado")
    d["vinculo"] = d.TIPO_VINCULO.replace({"Não Identificado": "Não identificado"})
    d["modalidade"] = d.MODALIDADE_OPERADORA.str.capitalize()
    d["abrangencia"] = d.DE_ABRG_GEOGRAFICA_PLANO
    d["local"] = np.where(d.CD_MUNICIPIO == "431490", "Porto Alegre", "Interior")
    d["vigencia"] = d.TP_VIGENCIA_PLANO.map({"P": "Posterior à Lei 9.656/1998", "A": "Anterior à Lei 9.656/1998"})
    return d


def tamanho_amostral(N):
    n0 = CONF_Z ** 2 * P * (1 - P) / MARGEM ** 2
    return n0, math.ceil(n0 / (1 + (n0 - 1) / N))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default=None)
    ap.add_argument("--saida", default=str(Path(__file__).with_name("dados")))
    a = ap.parse_args()
    saida = Path(a.saida)
    saida.mkdir(exist_ok=True)
    zp = Path(a.zip) if a.zip else saida / Path(URL).name
    if not zp.exists():
        print("baixando", URL)
        urllib.request.urlretrieve(URL, zp)

    d = le_populacao(zp)
    N = int(d[A].sum())
    vars_ = ["sexo", "faixa_etaria", "idade", "contratacao", "vinculo", "modalidade", "abrangencia", "local", "vigencia"]
    pop = d.groupby(vars_, as_index=False)[A].sum().rename(columns={A: "vinculos"})
    pop.to_csv(saida / "populacao_agregada.csv", index=False)
    mun = (d.groupby(["CD_MUNICIPIO", "NM_MUNICIPIO"], as_index=False)[A].sum()
             .rename(columns={A: "vinculos"}).sort_values("vinculos", ascending=False))
    mun.to_csv(saida / "municipios.csv", index=False)

    # AAS: sorteio de n posicoes distintas entre 1 e N; cada vinculo tem a mesma chance n/N
    n0, n = tamanho_amostral(N)
    rng = np.random.default_rng(SEMENTE)
    pos = np.sort(rng.choice(N, size=n, replace=False))            # posicoes 0..N-1
    linha = np.searchsorted(np.cumsum(d[A].to_numpy()), pos, side="right")
    am = d.iloc[linha][["NM_RAZAO_SOCIAL", "CD_PLANO", "NM_MUNICIPIO"] + vars_].copy()
    am.insert(0, "posicao_sorteada", pos + 1)
    am.insert(1, "linha_do_cadastro", linha + 1)
    am.to_csv(saida / "amostra_AAS.csv", index=False)

    meta = {"fonte": URL, "competencia": "2026-09", "N": N, "n0": round(n0, 2), "n": n,
            "confianca": 0.95, "margem": MARGEM, "p": P, "semente": SEMENTE,
            "linhas_cadastro": int(len(d)), "linhas_populacao_agregada": int(len(pop)),
            "numpy": np.__version__, "pandas": pd.__version__}
    (saida / "metadados.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=1))
