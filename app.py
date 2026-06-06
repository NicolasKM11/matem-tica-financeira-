
import math
from typing import List, Tuple
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="matemática financeira aplicada — v8 fórmula + hp12c", layout="wide")

UNIT_FACTORS = {
    "dia útil (252)": 252,
    "dia civil (365)": 365,
    "dia comercial (360)": 360,
    "mês": 12,
    "bimestre": 6,
    "trimestre": 4,
    "semestre": 2,
    "ano": 1,
}
SHORT = {
    "dia útil (252)": "a.d.u.",
    "dia civil (365)": "a.d.c.",
    "dia comercial (360)": "a.d.c.(360)",
    "mês": "a.m.",
    "bimestre": "a.b.",
    "trimestre": "a.t.",
    "semestre": "a.s.",
    "ano": "a.a.",
}

def periods_per_year(unit: str) -> float:
    return UNIT_FACTORS[unit]

def fmt_pct_decimal(x: float, casas: int = 6) -> str:
    return f"{x*100:.{casas}f}%".replace(".", ",")

def fmt_pct_value(x: float, casas: int = 6) -> str:
    return f"{x:.{casas}f}%".replace(".", ",")

def fmt_num(x: float, casas: int = 2) -> str:
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        if isinstance(x, str) and x.strip() == "":
            return default
        return float(x)
    except Exception:
        return default

def styled_result(label: str, value: str):
    st.markdown(f"**{label}**")
    st.markdown(f"<div style='font-size:1.7rem;font-weight:700;margin-bottom:.8rem'>{value}</div>", unsafe_allow_html=True)

def show_formula(title: str, text: str, show: bool):
    if show:
        with st.expander(f"{title} — pela fórmula", expanded=True):
            st.code(text)

def show_hp(title: str, text: str, show: bool):
    if show:
        with st.expander(f"{title} — pela hp12c", expanded=False):
            st.code(text)

def proportional_rate(rate: float, from_unit: str, to_unit: str) -> float:
    return rate * periods_per_year(to_unit) / periods_per_year(from_unit)

def equivalent_rate(rate: float, from_unit: str, to_unit: str) -> float:
    return (1 + rate) ** (periods_per_year(to_unit) / periods_per_year(from_unit)) - 1

def nominal_to_effective_same_cap(rate_nom: float, nominal_unit: str, cap_unit: str) -> float:
    return proportional_rate(rate_nom, nominal_unit, cap_unit)

def nominal_to_effective_target(rate_nom: float, nominal_unit: str, cap_unit: str, target_unit: str) -> Tuple[float, float]:
    i_cap = nominal_to_effective_same_cap(rate_nom, nominal_unit, cap_unit)
    i_target = equivalent_rate(i_cap, cap_unit, target_unit)
    return i_cap, i_target

def real_rate_from_effective(i_eff: float, infl: float) -> float:
    return (1 + i_eff) / (1 + infl) - 1

def effective_from_real(i_real: float, infl: float) -> float:
    return (1 + i_real) * (1 + infl) - 1

def simple_amount(c: float, i: float, n: float) -> float:
    return c * (1 + i * n)

def compound_amount(c: float, i: float, n: float) -> float:
    return c * (1 + i) ** n

def pmt_end(pv: float, i: float, n: int, fv: float = 0.0) -> float:
    if abs(i) < 1e-12:
        return -(pv + fv) / n
    return -(pv * i * (1 + i) ** n + fv * i) / ((1 + i) ** n - 1)

def pmt_begin(pv: float, i: float, n: int, fv: float = 0.0) -> float:
    if abs(i) < 1e-12:
        return -(pv + fv) / n
    return pmt_end(pv, i, n, fv) / (1 + i)

def pv_end(pmt: float, i: float, n: int, fv: float = 0.0) -> float:
    if abs(i) < 1e-12:
        return -(pmt * n + fv)
    return -pmt * (1 - (1 + i) ** -n) / i - fv / (1 + i) ** n

def pv_begin(pmt: float, i: float, n: int, fv: float = 0.0) -> float:
    if abs(i) < 1e-12:
        return -(pmt * n + fv)
    return pv_end(pmt * (1 + i), i, n, fv)

def fv_end(pv: float, pmt: float, i: float, n: int) -> float:
    if abs(i) < 1e-12:
        return -(pv + pmt * n)
    return -(pv * (1 + i) ** n + pmt * (((1 + i) ** n - 1) / i))

def fv_begin(pv: float, pmt: float, i: float, n: int) -> float:
    if abs(i) < 1e-12:
        return -(pv + pmt * n)
    return -(pv * (1 + i) ** n + pmt * (1 + i) * (((1 + i) ** n - 1) / i))

def npv(rate: float, cashflows: List[float]) -> float:
    return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))

def irr_bisect(cashflows: List[float], low: float = -0.9999, high: float = 10.0, steps: int = 800):
    def f(r):
        return npv(r, cashflows)
    grid = np.linspace(low, high, steps)
    vals = [f(x) for x in grid]
    for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if abs(fa) < 1e-12:
            return a
        if fa * fb < 0:
            lo, hi = a, b
            for _ in range(120):
                mid = (lo + hi) / 2
                fm = f(mid)
                if abs(fm) < 1e-12:
                    return mid
                if fa * fm < 0:
                    hi, fb = mid, fm
                else:
                    lo, fa = mid, fm
            return (lo + hi) / 2
    return None

with st.sidebar:
    show_formula_flag = st.checkbox("mostrar fórmula", True)
    show_hp_flag = st.checkbox("mostrar hp12c", True)
    st.caption("em todas as abas, a unidade é escolhida pelo usuário.")

st.title("matemática financeira aplicada — v8 fórmula + hp12c")
st.caption("esta versão mostra o resultado, a fórmula e como fazer na hp12c em todas as abas.")

tabs = st.tabs([
    "início","taxas proporcionais","taxas equivalentes","taxa nominal x efetiva","taxa real",
    "comparador de taxas","juros simples","juros compostos","desconto comercial simples",
    "desconto racional simples","desconto comercial composto","desconto racional composto",
    "custo efetivo no desconto","séries uniformes","perpetuidade","entrada + parcelas / taxa implícita",
    "renegociação","fluxo de caixa irregular"
])

with tabs[0]:
    st.write("versão focada em mostrar como o cálculo é feito pela fórmula e pela hp12c.")
    st.write("todas as abas deixam você escolher as unidades da taxa e do tempo, sem pressupor mês, ano ou semestre.")

with tabs[1]:
    c1, c2, c3 = st.columns(3)
    with c1:
        i = st.number_input("taxa de origem (%)", value=2.0, step=0.1) / 100
    with c2:
        u1 = st.selectbox("de", list(UNIT_FACTORS.keys()), index=3, key="p1")
    with c3:
        u2 = st.selectbox("para", list(UNIT_FACTORS.keys()), index=7, key="p2")
    res = proportional_rate(i, u1, u2)
    styled_result("taxa proporcional", f"{fmt_pct_decimal(res)} {u2}")
    show_formula(
        "taxa proporcional",
        f"i2 = i1 × (períodos de {u2} / períodos de {u1})\n"
        f"i2 = {i:.8f} × ({periods_per_year(u2):.0f}/{periods_per_year(u1):.0f})\n"
        f"i2 = {res:.8f}\n"
        f"i2 = {fmt_pct_decimal(res)} {u2}",
        show_formula_flag,
    )
    show_hp(
        "taxa proporcional",
        "na hp12c, a conversão proporcional é feita por conta direta:\n"
        f"{i*100:.10g} ENTER {periods_per_year(u2):.10g} × {periods_per_year(u1):.10g} ÷\n"
        f"resultado = {res*100:.10g}%",
        show_hp_flag,
    )

with tabs[2]:
    c1, c2, c3 = st.columns(3)
    with c1:
        i = st.number_input("taxa efetiva de origem (%)", value=18.0, step=0.1, key="e1") / 100
    with c2:
        u1 = st.selectbox("de", list(UNIT_FACTORS.keys()), index=7, key="e2")
    with c3:
        u2 = st.selectbox("para", list(UNIT_FACTORS.keys()), index=5, key="e3")
    res = equivalent_rate(i, u1, u2)
    expo = periods_per_year(u2) / periods_per_year(u1)
    styled_result("taxa equivalente", fmt_pct_decimal(res))
    show_formula(
        "taxa equivalente",
        f"i2 = (1 + i1)^({periods_per_year(u2):.0f}/{periods_per_year(u1):.0f}) - 1\n"
        f"i2 = (1 + {i:.8f})^{expo:.8f} - 1\n"
        f"i2 = {res:.8f}\n"
        f"i2 = {fmt_pct_decimal(res)} {u2}",
        show_formula_flag,
    )
    show_hp(
        "taxa equivalente",
        f"truque usando base 1:\n1 ENTER {i:.10g} +\n{expo:.10g} y^x\n1 -\n"
        f"ou usando taxa decimal com conta equivalente\n"
        f"resultado = {res*100:.10g}%",
        show_hp_flag,
    )

with tabs[3]:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        j = st.number_input("taxa nominal (%)", value=24.0, step=0.1, key="n1") / 100
    with c2:
        un_nom = st.selectbox("unidade da taxa nominal", list(UNIT_FACTORS.keys()), index=7, key="n2")
    with c3:
        cap = st.selectbox("capitalização", list(UNIT_FACTORS.keys()), index=3, key="n3")
    with c4:
        target = st.selectbox("quero a resposta em", list(UNIT_FACTORS.keys()), index=3, key="n4")
    i_cap, i_target = nominal_to_effective_target(j, un_nom, cap, target)
    styled_result("taxa efetiva na capitalização", fmt_pct_decimal(i_cap))
    styled_result("taxa efetiva na unidade desejada", fmt_pct_decimal(i_target))
    show_formula(
        "taxa nominal x efetiva",
        f"1) efetiva na capitalização:\n"
        f"i_cap = j × ({periods_per_year(cap):.0f}/{periods_per_year(un_nom):.0f})\n"
        f"i_cap = {j:.8f} × ({periods_per_year(cap):.0f}/{periods_per_year(un_nom):.0f}) = {i_cap:.8f}\n"
        f"i_cap = {fmt_pct_decimal(i_cap)} {cap}\n\n"
        f"2) equivalente na unidade desejada:\n"
        f"i_alvo = (1 + i_cap)^({periods_per_year(target):.0f}/{periods_per_year(cap):.0f}) - 1\n"
        f"i_alvo = (1 + {i_cap:.8f})^({periods_per_year(target):.0f}/{periods_per_year(cap):.0f}) - 1 = {i_target:.8f}\n"
        f"i_alvo = {fmt_pct_decimal(i_target)} {target}",
        show_formula_flag,
    )
    show_hp(
        "taxa nominal x efetiva",
        f"passo 1 — taxa efetiva da capitalização:\n"
        f"{j*100:.10g} ENTER {periods_per_year(cap):.10g} × {periods_per_year(un_nom):.10g} ÷\n"
        f"= {i_cap*100:.10g}%\n\n"
        f"passo 2 — equivalente para {target}:\n"
        f"1 ENTER {i_cap:.10g} +\n"
        f"{periods_per_year(target)/periods_per_year(cap):.10g} y^x\n1 -\n"
        f"= {i_target*100:.10g}%",
        show_hp_flag,
    )

with tabs[4]:
    modo = st.radio("o que deseja descobrir?", ["taxa real", "taxa efetiva necessária"], horizontal=True)
    if modo == "taxa real":
        a, b = st.columns(2)
        with a:
            i_eff = st.number_input("rendimento efetivo (%)", value=10.24, step=0.1) / 100
        with b:
            infl = st.number_input("inflação (%)", value=4.0, step=0.1) / 100
        res = real_rate_from_effective(i_eff, infl)
        styled_result("taxa real", fmt_pct_decimal(res))
        show_formula(
            "taxa real",
            f"i_real = ((1 + i_efetiva) / (1 + inflação)) - 1\n"
            f"i_real = ((1 + {i_eff:.8f}) / (1 + {infl:.8f})) - 1\n"
            f"i_real = {res:.8f}\n"
            f"i_real = {fmt_pct_decimal(res)}",
            show_formula_flag,
        )
        show_hp(
            "taxa real",
            f"1 ENTER {i_eff:.10g} +\n"
            f"1 ENTER {infl:.10g} + ÷\n"
            f"1 -\n"
            f"= {res*100:.10g}%",
            show_hp_flag,
        )
    else:
        a, b = st.columns(2)
        with a:
            i_real = st.number_input("taxa real desejada (%)", value=6.0, step=0.1) / 100
        with b:
            infl = st.number_input("inflação (%)", value=4.0, step=0.1, key="tr2") / 100
        res = effective_from_real(i_real, infl)
        styled_result("taxa efetiva necessária", fmt_pct_decimal(res))
        show_formula(
            "taxa efetiva necessária",
            f"i_efetiva = (1 + i_real)(1 + inflação) - 1\n"
            f"i_efetiva = (1 + {i_real:.8f})(1 + {infl:.8f}) - 1\n"
            f"i_efetiva = {res:.8f}\n"
            f"i_efetiva = {fmt_pct_decimal(res)}",
            show_formula_flag,
        )
        show_hp(
            "taxa efetiva necessária",
            f"1 ENTER {i_real:.10g} +\n"
            f"1 ENTER {infl:.10g} + ×\n"
            f"1 -\n"
            f"= {res*100:.10g}%",
            show_hp_flag,
        )

with tabs[5]:
    finalidade = st.radio("finalidade", ["empréstimo", "investimento"], horizontal=True)
    a1, a2, a3 = st.columns(3)
    b1, b2, b3 = st.columns(3)
    with a1:
        ta = st.number_input("taxa A (%)", value=35.0, step=0.1) / 100
    with a2:
        ua = st.selectbox("unidade A", list(UNIT_FACTORS.keys()), index=7, key="ca1")
    with a3:
        ca = st.selectbox("capitalização A", list(UNIT_FACTORS.keys()), index=7, key="ca2")
    with b1:
        tb = st.number_input("taxa B (%)", value=32.0, step=0.1, key="cb0") / 100
    with b2:
        ub = st.selectbox("unidade B", list(UNIT_FACTORS.keys()), index=7, key="cb1")
    with b3:
        cb = st.selectbox("capitalização B", list(UNIT_FACTORS.keys()), index=3, key="cb2")
    ea = nominal_to_effective_target(ta, ua, ca, "ano")[1]
    eb = nominal_to_effective_target(tb, ub, cb, "ano")[1]
    melhor = "Banco A" if (ea < eb if finalidade == "empréstimo" else ea > eb) else "Banco B"
    styled_result("efetiva anual A", fmt_pct_decimal(ea))
    styled_result("efetiva anual B", fmt_pct_decimal(eb))
    st.success(melhor)
    show_formula(
        "comparador de taxas",
        f"converter A para efetiva anual = {fmt_pct_decimal(ea)}\n"
        f"converter B para efetiva anual = {fmt_pct_decimal(eb)}\n"
        f"comparar: {'menor é melhor para empréstimo' if finalidade == 'empréstimo' else 'maior é melhor para investimento'}\n"
        f"resultado: {melhor}",
        show_formula_flag,
    )
    show_hp(
        "comparador de taxas",
        "na hp12c, primeiro transforme cada taxa para efetiva anual.\n"
        "depois compare os dois resultados anuais efetivos.",
        show_hp_flag,
    )

with tabs[6]:
    a, b, c, d = st.columns(4)
    with a:
        cap = st.number_input("capital", value=50000.0, step=100.0)
    with b:
        i = st.number_input("taxa (%)", value=5.0, step=0.1, key="js") / 100
    with c:
        n = st.number_input("prazo", value=9.0, step=1.0)
    with d:
        unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=3, key="jsu")
    juros = cap * i * n
    mont = cap + juros
    styled_result("juros", f"R$ {fmt_num(juros)}")
    styled_result("montante", f"R$ {fmt_num(mont)}")
    show_formula(
        "juros simples",
        f"J = C · i · n\n"
        f"J = {cap:.6f} × {i:.8f} × {n:.6f} = {juros:.6f}\n\n"
        f"M = C + J = {cap:.6f} + {juros:.6f} = {mont:.6f}",
        show_formula_flag,
    )
    show_hp(
        "juros simples",
        f"f REG\n{cap:.10g} CHS PV\n{i*100:.10g} i\n{n:.10g} n\nFV\n"
        f"unidade: {unidade}",
        show_hp_flag,
    )

with tabs[7]:
    a, b, c, d = st.columns(4)
    with a:
        cap = st.number_input("capital inicial", value=1000.0, step=100.0, key="jc1")
    with b:
        i = st.number_input("taxa efetiva (%)", value=20.0, step=0.1, key="jc2") / 100
    with c:
        n = st.number_input("prazo", value=3.0, step=1.0, key="jc3")
    with d:
        unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=7, key="jc4")
    mont = compound_amount(cap, i, n)
    styled_result("montante", f"R$ {fmt_num(mont)}")
    show_formula(
        "juros compostos",
        f"M = C(1+i)^n\n"
        f"M = {cap:.6f}(1+{i:.8f})^{n:.6f}\n"
        f"M = {mont:.6f}",
        show_formula_flag,
    )
    show_hp(
        "juros compostos",
        f"f REG\n{cap:.10g} CHS PV\n{i*100:.10g} i\n{n:.10g} n\nFV\n"
        f"unidade: {unidade}",
        show_hp_flag,
    )

with tabs[8]:
    a, b, c, d = st.columns(4)
    with a:
        fv = st.number_input("FV", value=65000.0, step=100.0, key="dcs1")
    with b:
        tax = st.number_input("taxa de desconto (%)", value=3.0, step=0.1, key="dcs2") / 100
    with c:
        n = st.number_input("prazo", value=8.0, step=1.0, key="dcs3")
    with d:
        unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=3, key="dcs4")
    disc = fv * tax * n
    pv = fv - disc
    styled_result("desconto", f"R$ {fmt_num(disc)}")
    styled_result("PV", f"R$ {fmt_num(pv)}")
    show_formula(
        "desconto comercial simples",
        f"D = FV · d · n\n"
        f"D = {fv:.6f} × {tax:.8f} × {n:.6f} = {disc:.6f}\n\n"
        f"PV = FV - D = {fv:.6f} - {disc:.6f} = {pv:.6f}",
        show_formula_flag,
    )
    show_hp(
        "desconto comercial simples",
        f"na hp12c, faça a conta direta do desconto:\n"
        f"{fv:.10g} ENTER {tax*100:.10g}% ENTER {n:.10g}\n"
        f"D = FV×d×n\n"
        f"PV = FV - D\n"
        f"unidade: {unidade}",
        show_hp_flag,
    )

with tabs[9]:
    a, b, c, d = st.columns(4)
    with a:
        fv = st.number_input("FV", value=100000.0, step=100.0, key="drs1")
    with b:
        i = st.number_input("taxa (%)", value=2.0, step=0.1, key="drs2") / 100
    with c:
        n = st.number_input("prazo", value=6.0, step=1.0, key="drs3")
    with d:
        unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=3, key="drs4")
    pv = fv / (1 + i * n)
    disc = fv - pv
    styled_result("PV", f"R$ {fmt_num(pv)}")
    styled_result("desconto", f"R$ {fmt_num(disc)}")
    show_formula(
        "desconto racional simples",
        f"PV = FV / (1 + i·n)\n"
        f"PV = {fv:.6f} / (1 + {i:.8f}×{n:.6f}) = {pv:.6f}\n\n"
        f"D = FV - PV = {fv:.6f} - {pv:.6f} = {disc:.6f}",
        show_formula_flag,
    )
    show_hp(
        "desconto racional simples",
        f"na hp12c, para achar PV com juros simples:\n"
        f"PV = FV ÷ (1 + i·n)\n"
        f"unidade: {unidade}",
        show_hp_flag,
    )

with tabs[10]:
    a, b, c, d = st.columns(4)
    with a:
        fv = st.number_input("FV", value=65000.0, step=100.0, key="dcc1")
    with b:
        tax = st.number_input("taxa de desconto (%)", value=3.0, step=0.1, key="dcc2") / 100
    with c:
        n = st.number_input("prazo", value=8.0, step=1.0, key="dcc3")
    with d:
        unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=3, key="dcc4")
    pv = fv * ((1 - tax) ** n)
    disc = fv - pv
    styled_result("PV", f"R$ {fmt_num(pv)}")
    styled_result("desconto", f"R$ {fmt_num(disc)}")
    show_formula(
        "desconto comercial composto",
        f"PV = FV(1-d)^n\n"
        f"PV = {fv:.6f}(1-{tax:.8f})^{n:.6f} = {pv:.6f}\n\n"
        f"D = FV - PV = {fv:.6f} - {pv:.6f} = {disc:.6f}",
        show_formula_flag,
    )
    show_hp(
        "desconto comercial composto",
        f"1 ENTER {tax:.10g} -\n{n:.10g} y^x\n{fv:.10g} ×\n"
        f"resultado = PV\n"
        f"unidade: {unidade}",
        show_hp_flag,
    )

with tabs[11]:
    a, b, c, d = st.columns(4)
    with a:
        fv = st.number_input("FV", value=1000.0, step=100.0, key="drc1")
    with b:
        i = st.number_input("taxa efetiva (%)", value=13.87, step=0.01, key="drc2") / 100
    with c:
        n = st.number_input("prazo", value=2.0, step=1.0, key="drc3")
    with d:
        unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=7, key="drc4")
    pv = fv / ((1 + i) ** n)
    disc = fv - pv
    styled_result("PV", f"R$ {fmt_num(pv, 4)}")
    styled_result("desconto", f"R$ {fmt_num(disc, 4)}")
    show_formula(
        "desconto racional composto",
        f"PV = FV/(1+i)^n\n"
        f"PV = {fv:.6f}/(1+{i:.8f})^{n:.6f} = {pv:.6f}\n\n"
        f"D = FV - PV = {fv:.6f} - {pv:.6f} = {disc:.6f}",
        show_formula_flag,
    )
    show_hp(
        "desconto racional composto",
        f"f REG\n{fv:.10g} FV\n{i*100:.10g} i\n{n:.10g} n\nPV\n"
        f"unidade: {unidade}",
        show_hp_flag,
    )

with tabs[12]:
    a, b, c = st.columns(3)
    with a:
        fv = st.number_input("FV / valor nominal", value=25000.0, step=100.0, key="ce1")
        d = st.number_input("taxa de desconto (%)", value=2.0, step=0.1, key="ce2") / 100
    with b:
        n = st.number_input("prazo", value=5.0, step=1.0, key="ce3")
        saldo_med = st.number_input("saldo médio retido (%)", value=30.0, step=1.0, key="ce4") / 100
    with c:
        desp = st.number_input("despesa administrativa (%)", value=0.0, step=0.1, key="ce5") / 100
        rem_saldo = st.number_input("remuneração do saldo médio (%)", value=0.0, step=0.1, key="ce6") / 100
    desconto = fv * d * n
    pv_base = fv - desconto
    saldo = fv * saldo_med
    pv_liq = pv_base - saldo - fv * desp
    fv_liq = fv - saldo * ((1 + rem_saldo) ** n)
    taxa = (fv_liq / pv_liq) ** (1 / n) - 1 if pv_liq > 0 else float("nan")
    styled_result("valor líquido hoje", f"R$ {fmt_num(pv_liq)}")
    styled_result("taxa implícita efetiva", fmt_pct_decimal(taxa) if math.isfinite(taxa) else "inválida")
    show_formula(
        "custo efetivo no desconto",
        f"D = FV·d·n = {fv:.6f}×{d:.8f}×{n:.6f} = {desconto:.6f}\n"
        f"PV base = FV - D = {pv_base:.6f}\n"
        f"saldo médio = FV×{saldo_med:.8f} = {saldo:.6f}\n"
        f"PV líquido = {pv_base:.6f} - {saldo:.6f} - {fv*desp:.6f} = {pv_liq:.6f}\n"
        f"FV líquido = {fv:.6f} - {saldo:.6f}×(1+{rem_saldo:.8f})^{n:.6f} = {fv_liq:.6f}\n"
        f"i = (FVliq/PVliq)^(1/n) - 1 = {taxa:.8f}",
        show_formula_flag,
    )
    show_hp(
        "custo efetivo no desconto",
        "na hp12c, primeiro calcule PV líquido e FV líquido.\n"
        "depois resolva i pela relação composta entre PV líquido e FV líquido.",
        show_hp_flag,
    )

with tabs[13]:
    tipo = st.radio("tipo da série", ["postecipada", "antecipada", "diferida / carência"], horizontal=True)
    descobrir = st.selectbox("o que descobrir?", ["PMT", "PV", "FV"])
    a, b, c, d, e = st.columns(5)
    with a:
        pv = st.number_input("PV", value=36000.0, step=100.0, key="su1")
    with b:
        pmt = st.number_input("PMT", value=1000.0, step=100.0, key="su2")
    with c:
        fv = st.number_input("FV", value=0.0, step=100.0, key="su3")
    with d:
        i = st.number_input("taxa (%)", value=1.8, step=0.1, key="su4") / 100
    with e:
        n = int(st.number_input("n", value=36, step=1, key="su5"))
    unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=3, key="su6")
    car = 0
    if tipo == "diferida / carência":
        car = int(st.number_input("carência em períodos", value=2, step=1, key="su7"))
    if descobrir == "PMT":
        res = pmt_end(pv, i, n, fv) if tipo == "postecipada" else pmt_begin(pv, i, n, fv) if tipo == "antecipada" else pmt_end(pv * ((1 + i) ** car), i, n, fv)
        styled_result("PMT", f"R$ {fmt_num(abs(res))}")
    elif descobrir == "PV":
        res = pv_end(pmt, i, n, fv) if tipo == "postecipada" else pv_begin(pmt, i, n, fv) if tipo == "antecipada" else pv_end(pmt, i, n, fv) / ((1 + i) ** car)
        styled_result("PV", f"R$ {fmt_num(abs(res))}")
    else:
        res = fv_end(pv, pmt, i, n) if tipo == "postecipada" else fv_begin(pv, pmt, i, n) if tipo == "antecipada" else fv_end(pv * ((1 + i) ** car), pmt, i, n)
        styled_result("FV", f"R$ {fmt_num(abs(res))}")
    show_formula(
        "séries uniformes",
        f"tipo = {tipo}\n"
        f"descobrir = {descobrir}\n"
        f"i = {i:.8f}, n = {n}, unidade = {unidade}\n"
        f"carência = {car}\n"
        f"use a fórmula da anuidade correspondente (END/BEGIN ou diferida)",
        show_formula_flag,
    )
    hp_mode = "END" if tipo == "postecipada" else "BEGIN" if tipo == "antecipada" else "END com deslocamento"
    show_hp(
        "séries uniformes",
        f"[g] {hp_mode}\n"
        f"{i*100:.10g} i\n{n} n\n"
        f"usar PV, PMT e FV conforme a incógnita\n"
        f"unidade: {unidade}",
        show_hp_flag,
    )

with tabs[14]:
    modo = st.radio("o que descobrir?", ["PV", "PMT"], horizontal=True)
    a, b, c = st.columns(3)
    with a:
        pv = st.number_input("PV", value=200000.0, step=100.0, key="pe1")
    with b:
        pmt = st.number_input("PMT", value=12000.0, step=100.0, key="pe2")
    with c:
        i = st.number_input("taxa efetiva (%)", value=6.0, step=0.1, key="pe3") / 100
    unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=7, key="pe4")
    if modo == "PV":
        res = pmt / i if i != 0 else float("nan")
        styled_result("PV da perpetuidade", f"R$ {fmt_num(res)}")
        show_formula("perpetuidade", f"PV = PMT / i = {pmt:.6f} / {i:.8f} = {res:.6f}", show_formula_flag)
    else:
        res = pv * i
        styled_result("PMT da perpetuidade", f"R$ {fmt_num(res)}")
        show_formula("perpetuidade", f"PMT = PV · i = {pv:.6f} × {i:.8f} = {res:.6f}", show_formula_flag)
    show_hp("perpetuidade", f"na hp12c, use a conta direta com i em {unidade}.", show_hp_flag)

with tabs[15]:
    modo = st.radio("resolver", ["taxa implícita", "valor da parcela"], horizontal=True)
    a, b, c, d, e = st.columns(5)
    with a:
        preco = st.number_input("preço do bem", value=3000.0, step=100.0, key="en1")
    with b:
        desc_av = st.number_input("desconto à vista (%)", value=5.0, step=0.1, key="en2") / 100
    with c:
        entrada = st.number_input("entrada", value=0.0, step=100.0, key="en3")
    with d:
        pmt = st.number_input("parcela", value=750.0, step=100.0, key="en4")
    with e:
        n = int(st.number_input("n parcelas", value=4, step=1, key="en5"))
    unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=3, key="en6")
    pv_fin = preco * (1 - desc_av) - entrada
    if modo == "valor da parcela":
        i = st.number_input("taxa (%)", value=2.0, step=0.1, key="en7") / 100
        res = abs(pmt_end(pv_fin, i, n, 0.0))
        styled_result("parcela", f"R$ {fmt_num(res)}")
        show_formula(
            "entrada + parcelas",
            f"PV financiado = preço(1-desconto) - entrada = {pv_fin:.6f}\n"
            f"PMT = fórmula da anuidade postecipada\n"
            f"resultado = {res:.6f}",
            show_formula_flag,
        )
        show_hp(
            "entrada + parcelas",
            f"[g] END\n{pv_fin:.10g} PV\n{i*100:.10g} i\n{n} n\n0 FV\nPMT\n"
            f"unidade: {unidade}",
            show_hp_flag,
        )
    else:
        def f(r):
            return pv_end(-pmt, r, n, 0.0) - pv_fin
        rate = None
        grid = np.linspace(-0.95, 5.0, 1000)
        vals = [f(x) for x in grid]
        for aa, bb, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
            if fa * fb < 0:
                lo, hi = aa, bb
                for _ in range(80):
                    mid = (lo + hi) / 2
                    fm = f(mid)
                    if fa * fm < 0:
                        hi, fb = mid, fm
                    else:
                        lo, fa = mid, fm
                rate = (lo + hi) / 2
                break
        styled_result("taxa implícita", fmt_pct_decimal(rate) if rate is not None else "não encontrada")
        show_formula(
            "entrada + parcelas",
            f"PV financiado = preço(1-desconto) - entrada = {pv_fin:.6f}\n"
            f"resolver i na equação da anuidade para PMT = {pmt:.6f}, n = {n}\n"
            f"resultado = {rate if rate is not None else 'não encontrada'}",
            show_formula_flag,
        )
        show_hp("entrada + parcelas", f"na hp12c, use PV, PMT, FV=0 e n para resolver i em {unidade}.", show_hp_flag)

with tabs[16]:
    a, b, c = st.columns(3)
    with a:
        pmt_ant = st.number_input("prestação antiga", value=4727.98, step=100.0, key="re1")
        n_rest = int(st.number_input("n restante antigo", value=6, step=1, key="re2"))
    with b:
        i = st.number_input("taxa (%)", value=2.0, step=0.1, key="re3") / 100
        n_novo = int(st.number_input("novo n", value=18, step=1, key="re4"))
    with c:
        unidade = st.selectbox("unidade", list(UNIT_FACTORS.keys()), index=3, key="re5")
        tipo = st.selectbox("nova série", ["postecipada", "antecipada"], key="re6")
    saldo = abs(pv_end(-pmt_ant, i, n_rest, 0.0))
    nova = abs(pmt_end(saldo, i, n_novo, 0.0) if tipo == "postecipada" else pmt_begin(saldo, i, n_novo, 0.0))
    styled_result("saldo renegociado", f"R$ {fmt_num(saldo)}")
    styled_result("nova prestação", f"R$ {fmt_num(nova)}")
    show_formula(
        "renegociação",
        f"1) saldo devedor = PV das parcelas restantes = {saldo:.6f}\n"
        f"2) nova série ({tipo}) com PV = {saldo:.6f}, i = {i:.8f}, n = {n_novo}\n"
        f"3) nova prestação = {nova:.6f}",
        show_formula_flag,
    )
    show_hp(
        "renegociação",
        f"passo 1: calcular PV das parcelas restantes\n"
        f"passo 2: usar esse PV na nova série {'BEGIN' if tipo == 'antecipada' else 'END'}\n"
        f"unidade: {unidade}",
        show_hp_flag,
    )

with tabs[17]:
    st.caption("linhas vazias viram zero.")
    default_df = pd.DataFrame({"período": list(range(10)), "fluxo": [-750, -500, 0, 0, 100, 200, 300, 300, 300, 400]})
    df = st.data_editor(default_df, num_rows="dynamic", use_container_width=True, key="fc_editor")
    taxa_vpl = st.number_input("taxa para VPL (%)", value=1.0, step=0.1, key="fc_tax") / 100
    cleaned = []
    for _, row in df.iterrows():
        p = safe_float(row.get("período"), 0)
        f = safe_float(row.get("fluxo"), 0)
        if p < 0:
            continue
        cleaned.append((int(round(p)), f))
    if not cleaned:
        cleaned = [(0, 0.0)]
    max_p = max(p for p, _ in cleaned)
    cfs = [0.0] * (max_p + 1)
    for p, f in cleaned:
        cfs[p] += f
    vpl = npv(taxa_vpl, cfs)
    tir = irr_bisect(cfs)
    styled_result("VPL / NPV", f"R$ {fmt_num(vpl)}")
    styled_result("TIR / IRR", fmt_pct_decimal(tir) if tir is not None else "não encontrada")
    formula_lines = ["VPL = CF0"]
    for t, cf in enumerate(cfs[1:], start=1):
        formula_lines.append(f"+ {cf:.6f}/(1+{taxa_vpl:.8f})^{t}")
    show_formula("fluxo de caixa irregular", "\n".join(formula_lines) + f"\n\nVPL = {vpl:.6f}", show_formula_flag)
    show_hp(
        "fluxo de caixa irregular",
        "f REG\n"
        "g CF0 para o fluxo do período 0\n"
        "g CFj para cada fluxo seguinte\n"
        "g Nj para repetições quando houver\n"
        f"{taxa_vpl*100:.10g} i\n"
        "f NPV\n"
        "f IRR",
        show_hp_flag,
    )
