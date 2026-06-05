
import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="matemática financeira reduzido", page_icon="📘", layout="centered")

PER_YEAR = {
    "dia útil (252)": 252,
    "mês": 12,
    "bimestre": 6,
    "trimestre": 4,
    "semestre": 2,
    "ano": 1,
}

def money(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(v, d=4):
    return f"{v:.{d}f}%".replace(".", ",")

def equivalent_rate(rate_pct, from_unit, to_unit):
    i = rate_pct / 100
    return (((1 + i) ** (PER_YEAR[to_unit] / PER_YEAR[from_unit])) - 1) * 100

def effective_from_nominal(nom_rate_pct, nominal_unit, cap_unit):
    return nom_rate_pct * (PER_YEAR[cap_unit] / PER_YEAR[nominal_unit])

def annual_effective_from_rate(rate_pct, unit):
    return ((1 + rate_pct / 100) ** PER_YEAR[unit]) - 1

def gross_required_for_real(real_pct, inflation_pct):
    return (((1 + real_pct/100) * (1 + inflation_pct/100)) - 1) * 100

def rate_real(gross_eff_pct, inflation_pct):
    return ((1 + gross_eff_pct/100) / (1 + inflation_pct/100) - 1) * 100

def annuity_pmt(pv, i_pct, n, due="END", fv=0.0):
    i = i_pct / 100
    if abs(i) < 1e-12:
        return -(pv + fv) / n
    factor = 1 if due == "END" else (1+i)
    return -((pv*(1+i)**n + fv) * i) / (((1+i)**n - 1) * factor)

def annuity_pv(pmt, i_pct, n, due="END", fv=0.0):
    i = i_pct / 100
    if abs(i) < 1e-12:
        return -(pmt*n + fv)
    factor = 1 if due == "END" else (1+i)
    return -(((pmt*factor) * (((1+i)**n - 1)/i) + fv) / ((1+i)**n))

def annuity_fv(pmt, i_pct, n, due="END", pv=0.0):
    i = i_pct / 100
    if abs(i) < 1e-12:
        return -(pv + pmt*n)
    factor = 1 if due == "END" else (1+i)
    return -pv*(1+i)**n - pmt*factor*(((1+i)**n - 1)/i)

def npv(rate_pct, cashflows):
    r = rate_pct / 100
    return sum(cf / ((1+r) ** t) for t, cf in enumerate(cashflows))

def irr(cashflows):
    def f(r):
        return sum(cf / ((1+r) ** t) for t, cf in enumerate(cashflows))
    lo, hi = -0.9999, 10.0
    flo, fhi = f(lo), f(hi)
    tries = 0
    while flo * fhi > 0 and tries < 40:
        hi *= 2
        fhi = f(hi)
        tries += 1
    if flo * fhi > 0:
        return None
    for _ in range(250):
        mid = (lo + hi) / 2
        fmid = f(mid)
        if abs(fmid) < 1e-12:
            return mid * 100
        if flo * fmid <= 0:
            hi = mid
            fhi = fmid
        else:
            lo = mid
            flo = fmid
    return mid * 100

def formula_box(text):
    st.markdown("**pela fórmula**")
    st.code(text)

def hp_box(text):
    st.markdown("**pela hp12c**")
    st.code(text)

st.title("matemática financeira aplicada — versão reduzida")
st.caption("focada nos tipos de exercícios que você indicou do livro.")

tabs = st.tabs([
    "taxa nominal x efetiva",
    "taxa real",
    "desconto comercial simples",
    "custo efetivo do desconto",
    "séries uniformes",
    "fluxo irregular VPL/TIR",
    "comparar bancos"
])

with tabs[0]:
    st.subheader("taxa nominal x efetiva")
    nominal = st.number_input("taxa nominal (%)", value=12.0)
    un_nominal = st.selectbox("unidade da taxa nominal", list(PER_YEAR.keys()), index=5)
    cap = st.selectbox("capitalização", list(PER_YEAR.keys()), index=1)
    alvo = st.selectbox("quero a taxa equivalente em", list(PER_YEAR.keys()), index=5)

    taxa_efetiva_cap = effective_from_nominal(nominal, un_nominal, cap)
    taxa_equiv = equivalent_rate(taxa_efetiva_cap, cap, alvo)

    st.metric("taxa efetiva da capitalização", f"{pct(taxa_efetiva_cap)} {cap}")
    st.metric("taxa equivalente na unidade desejada", f"{pct(taxa_equiv)} {alvo}")

    formula_box(
        f"1) taxa efetiva na capitalização = {nominal:.6f} × ({PER_YEAR[cap]}/{PER_YEAR[un_nominal]}) = {taxa_efetiva_cap:.6f}% {cap}\n"
        f"2) taxa equivalente = (1+{taxa_efetiva_cap/100:.8f})^({PER_YEAR[alvo]}/{PER_YEAR[cap]}) - 1 = {taxa_equiv:.6f}% {alvo}"
    )

    hp_box(
        "exemplo de lógica hp12c:\n"
        "primeiro transforme a nominal em efetiva da capitalização\n"
        "depois use a equivalência: (1+i_origem)^(n_destino/n_origem) - 1"
    )

with tabs[1]:
    st.subheader("taxa real")
    modo = st.radio("modo", ["achar taxa bruta necessária", "achar taxa real embutida"], horizontal=True)
    if modo == "achar taxa bruta necessária":
        real = st.number_input("taxa real desejada (%)", value=6.0)
        infl = st.number_input("inflação (%)", value=4.0)
        bruta = gross_required_for_real(real, infl)
        st.metric("taxa efetiva necessária", pct(bruta))
        formula_box(f"taxa bruta = (1+{real/100:.8f})(1+{infl/100:.8f}) - 1 = {bruta:.6f}%")
    else:
        bruta = st.number_input("rendimento efetivo (%)", value=10.24)
        infl = st.number_input("inflação (%)", value=4.0, key="infl2")
        real = rate_real(bruta, infl)
        st.metric("taxa real", pct(real))
        formula_box(f"taxa real = (1+{bruta/100:.8f})/(1+{infl/100:.8f}) - 1 = {real:.6f}%")

with tabs[2]:
    st.subheader("desconto comercial simples — por fora")
    modo = st.selectbox("descobrir", ["valor recebido e desconto", "taxa d", "vários títulos"])
    if modo == "valor recebido e desconto":
        FV = st.number_input("valor nominal / FV", min_value=0.0, value=65000.0)
        d = st.number_input("taxa de desconto (%)", value=3.0)
        n = st.number_input("prazo em períodos", min_value=0.0, value=8.0)
        D = FV * d/100 * n
        PV = FV - D
        st.metric("desconto D", money(D))
        st.metric("valor recebido PV", money(PV))
        formula_box(f"D = FV·d·n = {FV:.6f} × {d/100:.8f} × {n:.6f} = {D:.6f}\nPV = FV - D = {PV:.6f}")
        hp_box(f"como é juros simples, normalmente resolve direto pela fórmula.\nD = FV·d·n\nPV = FV - D")
    elif modo == "taxa d":
        FV = st.number_input("valor nominal / FV", min_value=0.0, value=12000.0)
        PV = st.number_input("valor recebido / PV", min_value=0.0, value=9600.0)
        n = st.number_input("prazo em períodos", min_value=0.0, value=5.0)
        D = FV - PV
        d = D / (FV*n) * 100
        st.metric("desconto D", money(D))
        st.metric("taxa d", pct(d))
        formula_box(f"D = FV - PV = {D:.6f}\nd = D/(FV·n) = {d:.6f}%")
    else:
        qtd = st.number_input("quantidade de títulos", min_value=2, max_value=10, value=3)
        d = st.number_input("taxa de desconto (%)", value=3.0, key="multi_d")
        total_d = 0.0
        total_pv = 0.0
        linhas = []
        for k in range(int(qtd)):
            fv = st.number_input(f"FV título {k+1}", min_value=0.0, value=15000.0, key=f"fv_{k}")
            n = st.number_input(f"prazo título {k+1}", min_value=0.0, value=float(5+k), key=f"n_{k}")
            D = fv * d/100 * n
            PV = fv - D
            total_d += D
            total_pv += PV
            linhas.append(f"título {k+1}: D={D:.2f}, PV={PV:.2f}")
        st.metric("desconto total", money(total_d))
        st.metric("valor recebido total", money(total_pv))
        formula_box("\n".join(linhas))

with tabs[3]:
    st.subheader("custo efetivo do desconto")
    FV = st.number_input("valor nominal / FV", min_value=0.0, value=25000.0)
    d = st.number_input("taxa de desconto comercial simples (%)", value=2.0)
    n = st.number_input("prazo em períodos", min_value=0.0, value=5.0)
    saldo_medio_pct = st.number_input("saldo médio retido (%)", min_value=0.0, value=30.0)
    desp_adm_pct = st.number_input("despesa administrativa (%)", min_value=0.0, value=0.0)

    D = FV * d/100 * n
    pv_sem = FV - D
    i_sem = (((FV/pv_sem)**(1/n))-1)*100 if pv_sem > 0 else None

    saldo = FV * saldo_medio_pct/100
    desp = FV * desp_adm_pct/100
    pv_com = pv_sem - saldo - desp
    fv_com = FV - saldo
    i_com = (((fv_com/pv_com)**(1/n))-1)*100 if pv_com > 0 and fv_com > 0 else None

    st.metric("valor líquido sem retenções", money(pv_sem))
    st.metric("taxa implícita sem retenções", pct(i_sem) if i_sem is not None else "indefinida")
    st.metric("valor líquido com retenções", money(pv_com))
    st.metric("taxa implícita com retenções", pct(i_com) if i_com is not None else "indefinida")

    formula_box(
        f"D = FV·d·n = {D:.6f}\n"
        f"PV sem retenções = FV - D = {pv_sem:.6f}\n"
        f"saldo médio = {saldo:.6f}\n"
        f"despesa administrativa = {desp:.6f}\n"
        f"PV com retenções = {pv_com:.6f}\n"
        f"FV líquido de quitação = {fv_com:.6f}"
    )

with tabs[4]:
    st.subheader("séries uniformes")
    tipo = st.radio("tipo de série", ["postecipada", "antecipada", "diferida / carência", "perpetuidade"], horizontal=True)

    if tipo in ["postecipada", "antecipada"]:
        due = "END" if tipo == "postecipada" else "BEG"
        alvo = st.selectbox("descobrir", ["PMT", "PV", "FV"])
        i = st.number_input("taxa por período (%)", value=1.8)
        n = st.number_input("número de períodos", min_value=1.0, value=36.0)
        if alvo == "PMT":
            pv = st.number_input("PV", min_value=0.0, value=36000.0)
            fv = st.number_input("FV", value=0.0)
            pmt = annuity_pmt(pv, i, n, due=due, fv=fv)
            st.metric("PMT", money(abs(pmt)))
            formula_box(f"PMT calculada para série {'postecipada' if due=='END' else 'antecipada'} = {abs(pmt):.6f}")
            hp_box(f"[g] {'END' if due=='END' else 'BEG'}\n{pv} PV\n{i} i\n{n} n\n{fv} FV\nPMT")
        elif alvo == "PV":
            pmt = st.number_input("PMT", min_value=0.0, value=15000.0)
            fv = st.number_input("FV", value=0.0, key="su_fv2")
            pv = annuity_pv(-pmt, i, n, due=due, fv=fv)
            st.metric("PV", money(abs(pv)))
            formula_box(f"PV calculado para série {'postecipada' if due=='END' else 'antecipada'} = {abs(pv):.6f}")
            hp_box(f"[g] {'END' if due=='END' else 'BEG'}\n{pmt} CHS PMT\n{i} i\n{n} n\n{fv} FV\nPV")
        else:
            pmt = st.number_input("PMT", min_value=0.0, value=1000.0)
            pv = st.number_input("PV", value=0.0, key="su_pv3")
            fv = annuity_fv(-pmt, i, n, due=due, pv=pv)
            st.metric("FV", money(abs(fv)))
            formula_box(f"FV calculado para série {'postecipada' if due=='END' else 'antecipada'} = {abs(fv):.6f}")
            hp_box(f"[g] {'END' if due=='END' else 'BEG'}\n{pmt} CHS PMT\n{i} i\n{n} n\n{pv} PV\nFV")

    elif tipo == "diferida / carência":
        pv = st.number_input("PV hoje", min_value=0.0, value=30000.0)
        i = st.number_input("taxa por período (%)", value=2.0, key="dif_i")
        car = st.number_input("carência em períodos", min_value=0.0, value=6.0)
        n = st.number_input("número de parcelas", min_value=1.0, value=12.0)
        pv_inicio_serie = pv * ((1+i/100)**car)
        pmt = annuity_pmt(pv_inicio_serie, i, n, due="END", fv=0.0)
        st.metric("PMT da série diferida", money(abs(pmt)))
        formula_box(
            f"1) levar PV até o início da série: {pv:.6f}(1+{i/100:.8f})^{car:.6f} = {pv_inicio_serie:.6f}\n"
            f"2) calcular PMT da série postecipada = {abs(pmt):.6f}"
        )
        hp_box("na hp12c, primeiro leva o valor pela carência; depois resolve a anuidade normal.")

    else:
        modo = st.radio("modo", ["achar PV", "achar PMT"], horizontal=True)
        i = st.number_input("taxa (%)", value=6.0, key="perp_i")
        if modo == "achar PV":
            pmt = st.number_input("PMT", min_value=0.0, value=12000.0)
            pv = pmt / (i/100)
            st.metric("PV da perpetuidade", money(pv))
            formula_box(f"PV = PMT / i = {pmt:.6f} / {i/100:.8f} = {pv:.6f}")
        else:
            pv = st.number_input("PV", min_value=0.0, value=200000.0)
            pmt = pv * (i/100)
            st.metric("PMT da perpetuidade", money(pmt))
            formula_box(f"PMT = PV · i = {pv:.6f} × {i/100:.8f} = {pmt:.6f}")

with tabs[5]:
    st.subheader("fluxo de caixa irregular — VPL / TIR")
    default = pd.DataFrame({
        "período": [0, 1, 2, 3, 4, 5, 6],
        "fluxo": [-1200, 300, 400, 400, 500, 500, 500]
    })
    df = st.data_editor(default, num_rows="dynamic", use_container_width=True)
    taxa = st.number_input("taxa para VPL (%)", value=20.0)

    if len(df) > 0:
        df2 = df.sort_values("período").reset_index(drop=True)
        maxp = int(df2["período"].max())
        cfs = [0.0] * (maxp + 1)
        for _, row in df2.iterrows():
            cfs[int(row["período"])] += float(row["fluxo"])

        vpl = npv(taxa, cfs)
        tir = irr(cfs)

        st.metric("VPL / NPV", money(vpl))
        st.metric("TIR / IRR", pct(tir) if tir is not None else "não encontrada")

        termo = "vale a pena" if (vpl > 0 and tir is not None and tir > taxa) else "não compensa"
        st.info(f"interpretação: {termo}")

        formula_box(
            "VPL = FC0 + FC1/(1+i)^1 + FC2/(1+i)^2 + ...\n"
            f"resultado do VPL = {vpl:.6f}\n"
            f"resultado da TIR = {tir if tir is not None else 'não encontrada'}"
        )
        hp_box(
            "f REG\n"
            "g CF0 para o fluxo do período 0\n"
            "g CFj para cada fluxo seguinte\n"
            "g Nj quando houver repetição\n"
            "i\n"
            "f NPV\n"
            "f IRR"
        )

with tabs[6]:
    st.subheader("comparar bancos")
    tipo = st.radio("comparar", ["financiamento", "investimento"], horizontal=True)

    taxaA = st.number_input("taxa banco A (% nominal)", value=35.0 if tipo=="financiamento" else 23.0)
    capA = st.selectbox("capitalização banco A", list(PER_YEAR.keys()), index=5 if tipo=="investimento" else 5)
    taxaB = st.number_input("taxa banco B (% nominal)", value=32.0 if tipo=="financiamento" else 20.0)
    capB = st.selectbox("capitalização banco B", list(PER_YEAR.keys()), index=1)

    effA_cap = effective_from_nominal(taxaA, "ano", capA)
    effB_cap = effective_from_nominal(taxaB, "ano", capB)
    effA_aa = annual_effective_from_rate(effA_cap, capA) * 100
    effB_aa = annual_effective_from_rate(effB_cap, capB) * 100

    st.metric("taxa efetiva anual A", pct(effA_aa))
    st.metric("taxa efetiva anual B", pct(effB_aa))

    if tipo == "financiamento":
        melhor = "Banco A" if effA_aa < effB_aa else "Banco B"
        st.success(f"menor custo para o empresário: {melhor}")
    else:
        melhor = "Banco A" if effA_aa > effB_aa else "Banco B"
        st.success(f"maior rendimento para o investidor: {melhor}")

    formula_box(
        f"A: taxa efetiva anual = {effA_aa:.6f}%\n"
        f"B: taxa efetiva anual = {effB_aa:.6f}%"
    )
