import math
from typing import List, Optional

import pandas as pd
import streamlit as st

st.set_page_config(page_title="matemática financeira v8", page_icon="💸", layout="centered")

# =============================
# constantes e helpers
# =============================
UNITS = [
    "dia corrido (360)",
    "dia civil (365)",
    "dia útil (252)",
    "mês",
    "bimestre",
    "trimestre",
    "semestre",
    "ano",
]

TIME_FACTORS = {
    "dia corrido (360)": 1 / 360,
    "dia civil (365)": 1 / 365,
    "dia útil (252)": 1 / 252,
    "mês": 1 / 12,
    "bimestre": 1 / 6,
    "trimestre": 1 / 4,
    "semestre": 1 / 2,
    "ano": 1.0,
}
PER_YEAR = {k: 1 / v for k, v in TIME_FACTORS.items()}


def money(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v: float, d: int = 4) -> str:
    return f"{v:.{d}f}%".replace(".", ",")


def nz(v, default=0.0):
    if v is None:
        return default
    if isinstance(v, float) and math.isnan(v):
        return default
    return v


def to_years(value: float, unit: str) -> float:
    return value * TIME_FACTORS[unit]


def years_to_unit(years: float, unit: str) -> float:
    return years / TIME_FACTORS[unit]


def convert_time(value: float, from_unit: str, to_unit: str) -> float:
    return years_to_unit(to_years(value, from_unit), to_unit)


def simple_proportional(rate_pct: float, from_unit: str, to_unit: str) -> float:
    return rate_pct * (PER_YEAR[from_unit] / PER_YEAR[to_unit])


def equivalent_rate(rate_pct: float, from_unit: str, to_unit: str) -> float:
    i = rate_pct / 100
    expo = TIME_FACTORS[to_unit] / TIME_FACTORS[from_unit]
    return (((1 + i) ** expo) - 1) * 100


def effective_from_nominal(nom_rate_pct: float, nominal_unit: str, cap_unit: str) -> float:
    # taxa nominal -> taxa efetiva na unidade da capitalização
    return nom_rate_pct * (TIME_FACTORS[cap_unit] / TIME_FACTORS[nominal_unit])


def annual_effective_from_effective(rate_pct: float, unit: str) -> float:
    return (((1 + rate_pct / 100) ** PER_YEAR[unit]) - 1) * 100


def annual_effective_from_nominal(nom_rate_pct: float, nominal_unit: str, cap_unit: str) -> float:
    eff_cap = effective_from_nominal(nom_rate_pct, nominal_unit, cap_unit)
    return annual_effective_from_effective(eff_cap, cap_unit)


def rate_real_from_gross(gross_eff_pct: float, inflation_pct: float) -> float:
    return (((1 + gross_eff_pct / 100) / (1 + inflation_pct / 100)) - 1) * 100


def gross_required_for_real(real_pct: float, inflation_pct: float) -> float:
    return (((1 + real_pct / 100) * (1 + inflation_pct / 100)) - 1) * 100


# =============================
# juros simples e compostos
# =============================
def solve_simple(C=None, i_pct=None, n=None, M=None):
    i = None if i_pct is None else i_pct / 100
    if C is None and None not in (i, n, M):
        C = M / (1 + i * n)
    elif i is None and None not in (C, n, M):
        i = (M / C - 1) / n
    elif n is None and None not in (C, i, M):
        n = (M / C - 1) / i
    elif M is None and None not in (C, i, n):
        M = C * (1 + i * n)
    J = None if None in (C, M) else M - C
    return C, None if i is None else i * 100, n, M, J


def solve_compound(PV=None, i_pct=None, n=None, FV=None):
    i = None if i_pct is None else i_pct / 100
    if PV is None and None not in (i, n, FV):
        PV = FV / ((1 + i) ** n)
    elif i is None and None not in (PV, n, FV):
        i = (FV / PV) ** (1 / n) - 1
    elif n is None and None not in (PV, i, FV):
        n = math.log(FV / PV) / math.log(1 + i)
    elif FV is None and None not in (PV, i, n):
        FV = PV * ((1 + i) ** n)
    J = None if None in (PV, FV) else FV - PV
    return PV, None if i is None else i * 100, n, FV, J


# =============================
# descontos
# =============================
def desconto_racional_simples(FV: float, i_pct: float, n: float):
    PV = FV / (1 + i_pct / 100 * n)
    D = FV - PV
    return PV, D


def desconto_comercial_simples(FV: float, d_pct: float, n: float):
    D = FV * d_pct / 100 * n
    PV = FV - D
    return PV, D


def desconto_racional_composto(FV: float, i_pct: float, n: float):
    PV = FV / ((1 + i_pct / 100) ** n)
    D = FV - PV
    return PV, D


def desconto_comercial_composto(FV: float, d_pct: float, n: float):
    PV = FV * ((1 - d_pct / 100) ** n)
    D = FV - PV
    return PV, D


def implied_effective_rate_from_pv_fv(PV: float, FV: float, n: float) -> float:
    return (((FV / PV) ** (1 / n)) - 1) * 100


def effective_discount_cost(
    FV: float,
    n: float,
    mode: str,
    rate_pct: float,
    saldo_medio_pct: float = 0.0,
    despesa_pct: float = 0.0,
    remun_saldo_pct: float = 0.0,
):
    if mode == "desconto racional simples":
        pv_base, d_val = desconto_racional_simples(FV, rate_pct, n)
    elif mode == "desconto comercial simples":
        pv_base, d_val = desconto_comercial_simples(FV, rate_pct, n)
    elif mode == "desconto racional composto":
        pv_base, d_val = desconto_racional_composto(FV, rate_pct, n)
    else:
        pv_base, d_val = desconto_comercial_composto(FV, rate_pct, n)

    saldo_retido = FV * saldo_medio_pct / 100
    despesa = FV * despesa_pct / 100
    pv_liquido = pv_base - saldo_retido - despesa
    saldo_no_venc = saldo_retido * ((1 + remun_saldo_pct / 100) ** n)
    fv_liquido = FV - saldo_no_venc
    i_eff = implied_effective_rate_from_pv_fv(pv_liquido, fv_liquido, n)
    return {
        "pv_base": pv_base,
        "desconto": d_val,
        "saldo_retido": saldo_retido,
        "despesa": despesa,
        "pv_liquido": pv_liquido,
        "saldo_no_venc": saldo_no_venc,
        "fv_liquido": fv_liquido,
        "i_eff_pct": i_eff,
    }


# =============================
# séries uniformes
# =============================
def annuity_pmt(pv: float, i_pct: float, n: float, due: str = "END", fv: float = 0.0) -> float:
    i = i_pct / 100
    if abs(i) < 1e-12:
        return - (pv + fv) / n
    factor = 1 if due == "END" else (1 + i)
    return -((pv * (1 + i) ** n + fv) * i) / (((1 + i) ** n - 1) * factor)


def annuity_pv(pmt: float, i_pct: float, n: float, due: str = "END", fv: float = 0.0) -> float:
    i = i_pct / 100
    if abs(i) < 1e-12:
        return -(pmt * n + fv)
    factor = 1 if due == "END" else (1 + i)
    return -(((pmt * factor) * (((1 + i) ** n - 1) / i) + fv) / ((1 + i) ** n))


def annuity_fv(pmt: float, i_pct: float, n: float, due: str = "END", pv: float = 0.0) -> float:
    i = i_pct / 100
    if abs(i) < 1e-12:
        return -(pv + pmt * n)
    factor = 1 if due == "END" else (1 + i)
    return -pv * (1 + i) ** n - pmt * factor * (((1 + i) ** n - 1) / i)


def annuity_rate_bisect(pv: float, pmt: float, n: int, due: str = "END", fv: float = 0.0) -> Optional[float]:
    def func(i):
        factor = 1 if due == "END" else (1 + i)
        if abs(i) < 1e-12:
            return pv + pmt * n + fv
        return pv + (pmt * factor) * ((1 - (1 + i) ** (-n)) / i) + fv / ((1 + i) ** n)

    lo, hi = -0.9999, 5.0
    flo, fhi = func(lo), func(hi)
    tries = 0
    while flo * fhi > 0 and tries < 60:
        hi *= 2
        fhi = func(hi)
        tries += 1
    if flo * fhi > 0:
        return None
    for _ in range(250):
        mid = (lo + hi) / 2
        fmid = func(mid)
        if abs(fmid) < 1e-12:
            return mid * 100
        if flo * fmid <= 0:
            hi = mid
            fhi = fmid
        else:
            lo = mid
            flo = fmid
    return mid * 100


def perpetuity_pv(pmt: float, i_pct: float) -> float:
    return pmt / (i_pct / 100)


def perpetuity_pmt(pv: float, i_pct: float) -> float:
    return pv * (i_pct / 100)


def pmt_with_entry(entry: float, cash_price: float, i_pct: float, n: int, due: str = "END") -> float:
    financed = cash_price - entry
    return annuity_pmt(financed, i_pct, n, due=due, fv=0.0)


def implied_rate_with_entry(entry: float, cash_price: float, pmt: float, n: int, due: str = "END") -> Optional[float]:
    financed = cash_price - entry
    return annuity_rate_bisect(financed, pmt, n, due=due, fv=0.0)


def renegociation_new_pmt(old_pmt: float, old_rate_pct: float, rem_n: int, new_rate_pct: float, new_n: int) -> float:
    debt_now = annuity_pv(old_pmt, old_rate_pct, rem_n, due="END", fv=0.0)
    return annuity_pmt(debt_now, new_rate_pct, new_n, due="END", fv=0.0)


# =============================
# fluxo irregular
# =============================
def npv_periodic(rate_pct: float, cashflows: List[float]) -> float:
    r = rate_pct / 100
    return sum(cf / ((1 + r) ** t) for t, cf in enumerate(cashflows))


def irr_periodic(cashflows: List[float]) -> Optional[float]:
    def f(r):
        return sum(cf / ((1 + r) ** t) for t, cf in enumerate(cashflows))

    lo, hi = -0.9999, 10.0
    flo, fhi = f(lo), f(hi)
    tries = 0
    while flo * fhi > 0 and tries < 60:
        hi *= 2
        fhi = f(hi)
        tries += 1
    if flo * fhi > 0:
        return None
    for _ in range(300):
        mid = (lo + hi) / 2
        fmid = f(mid)
        if abs(fmid) < 1e-12:
            return mid * 100
        if flo * fmid <= 0:
            hi = mid
        else:
            lo = mid
            flo = fmid
    return mid * 100


def aggregate_cashflows(df: pd.DataFrame) -> List[float]:
    if df.empty:
        return []
    periods = []
    flows = []
    for _, row in df.iterrows():
        p = nz(row.get("período"), None)
        f = nz(row.get("fluxo"), None)
        if p is None or f is None:
            continue
        try:
            p = int(float(p))
            f = float(f)
        except Exception:
            continue
        periods.append(p)
        flows.append(f)
    if not periods:
        return []
    max_p = max(periods)
    cfs = [0.0] * (max_p + 1)
    for p, f in zip(periods, flows):
        cfs[p] += f
    return cfs


# =============================
# UI helpers
# =============================
def formula_box(title: str, text: str):
    st.markdown(f"**{title}**")
    st.code(text)


def hp_box(title: str, lines: List[str]):
    st.markdown(f"**{title}**")
    st.code("\n".join(lines))


def rate_to_payment_period(rate_pct: float, rate_unit: str, payment_unit: str) -> float:
    if rate_unit == payment_unit:
        return rate_pct
    return equivalent_rate(rate_pct, rate_unit, payment_unit)


def title_small(s: str):
    st.markdown(f"### {s}")


# =============================
# layout / watch mode
# =============================
if "watch_mode" not in st.session_state:
    st.session_state.watch_mode = False

st.markdown(
    """
<style>
.block-container {max-width: 920px; padding-top: .45rem; padding-bottom: 2rem;}
.sticky-top {
    position: sticky; top: 0; z-index: 999;
    background: rgba(14,17,23,.96);
    padding: .35rem 0 .65rem 0;
    border-bottom: 1px solid rgba(255,255,255,.08);
    margin-bottom: .6rem;
}
.watch h1 {font-size: 1.45rem !important;}
.watch h2, .watch h3 {font-size: 1.08rem !important;}
.watch p, .watch label, .watch .stCaption {font-size: .82rem !important;}
.watch code, .watch pre {font-size: .72rem !important;}
.watch div[data-testid="stMetricValue"] {font-size: 1.02rem !important;}
.watch div[data-testid="stMetricLabel"] {font-size: .72rem !important;}
.small-note {opacity: .8; font-size: .92rem;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="watch">' if st.session_state.watch_mode else '<div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-top">', unsafe_allow_html=True)
c1, c2 = st.columns([1.15, 1])
with c1:
    label = "💻 voltar para modo normal" if st.session_state.watch_mode else "⌚ ativar modo smartwatch"
    if st.button(label, type="primary", use_container_width=True):
        st.session_state.watch_mode = not st.session_state.watch_mode
        st.rerun()
with c2:
    st.caption("modo relógio / normal")

st.title("matemática financeira aplicada — v8")
st.caption("versão completa, com abas separadas, fórmulas, hp12c e unidades escolhidas pelo usuário.")

with st.sidebar:
    st.subheader("configurações")
    show_formula = st.checkbox("mostrar fórmula", value=True)
    show_hp = st.checkbox("mostrar hp12c", value=True)


# =============================
# abas
# =============================
tabs = st.tabs([
    "início",
    "porcentagem e apoio",
    "taxas proporcionais",
    "taxas equivalentes",
    "taxa nominal x efetiva",
    "taxa real",
    "juros simples",
    "juros compostos",
    "desconto racional simples",
    "desconto comercial simples",
    "desconto racional composto",
    "desconto comercial composto",
    "custo efetivo no desconto",
    "séries uniformes",
    "entrada + parcelas / taxa implícita",
    "renegociação",
    "fluxo de caixa irregular",
    "comparador",
    "página simples",
])

# início
with tabs[0]:
    st.subheader("o que esta versão calcula")
    st.write("- porcentagem, aumento, desconto, percentuais sucessivos e manutenção de receita")
    st.write("- taxas proporcionais, equivalentes, nominal x efetiva e taxa real")
    st.write("- juros simples e compostos")
    st.write("- desconto racional e comercial, simples e composto")
    st.write("- custo efetivo do desconto com saldo médio e despesa")
    st.write("- séries uniformes: postecipada, antecipada, diferida / carência, perpetuidade")
    st.write("- entrada + parcelas / taxa implícita")
    st.write("- renegociação")
    st.write("- fluxo de caixa irregular: VPL / TIR / CF0 / CFj / Nj")
    st.write("- comparador de taxas / bancos")
    st.info("em todas as partes importantes do app, a unidade da taxa e do tempo é escolhida pelo usuário. o app não deve presumir o período.")

# porcentagem e apoio
with tabs[1]:
    sub = st.radio("subaba", ["aumento/desconto", "percentuais sucessivos", "manutenção de receita"], horizontal=True)
    if sub == "aumento/desconto":
        base = st.number_input("valor base", value=500.0, step=100.0)
        var = st.number_input("variação (%)", value=40.0, step=1.0)
        aum = base * (1 + var / 100)
        des = base * (1 - var / 100)
        st.metric("valor com aumento", money(aum))
        st.metric("valor com desconto", money(des))
        if show_formula:
            formula_box("pela fórmula", f"aumento: {base:.6f} × (1 + {var/100:.6f}) = {aum:.6f}\ndesconto: {base:.6f} × (1 - {var/100:.6f}) = {des:.6f}")
    elif sub == "percentuais sucessivos":
        base = st.number_input("valor inicial", value=100.0, step=50.0)
        seq_txt = st.text_input("sequência de percentuais separados por vírgula", value="-50, 100, -20, 30")
        vals = []
        try:
            vals = [float(x.strip().replace(",", ".")) for x in seq_txt.split(";") if x.strip()] if ";" in seq_txt else [float(x.strip().replace(",", ".")) for x in seq_txt.split(",") if x.strip()]
        except Exception:
            vals = []
        final = base
        factors = []
        for v in vals:
            factor = 1 + v / 100
            factors.append(factor)
            final *= factor
        total_pct = (final / base - 1) * 100 if base != 0 else 0.0
        st.metric("valor final", money(final))
        st.metric("variação total", pct(total_pct))
        if show_formula and vals:
            parts = [f"{base:.6f}"] + [f"× {f:.6f}" for f in factors]
            formula_box("pela fórmula", " ".join(parts) + f" = {final:.6f}\nvariação total = ({final:.6f}/{base:.6f} - 1) × 100 = {total_pct:.6f}%")
        if show_hp and vals:
            hp_box("pela hp12c", ["para percentuais sucessivos, multiplique os fatores em sequência.", f"fatores: {', '.join(f'{f:.6f}' for f in factors)}", f"resultado final = {final:.6f}"])
    else:
        reducao = st.number_input("redução da quantidade (%)", value=20.0, step=1.0)
        fator = 100 / (100 - reducao) if reducao < 100 else float("inf")
        aumento = (fator - 1) * 100 if reducao < 100 else float("inf")
        st.metric("multiplicador da nova mensalidade", f"{fator:.4f}x" if math.isfinite(fator) else "∞")
        st.metric("aumento necessário", pct(aumento) if math.isfinite(aumento) else "∞")
        if show_formula and reducao < 100:
            formula_box("pela fórmula", f"fator = 100 / (100 - {reducao:.6f}) = {fator:.6f}\naumento = ({fator:.6f} - 1) × 100 = {aumento:.6f}%")

# taxas proporcionais
with tabs[2]:
    rate = st.number_input("taxa de origem (%)", value=24.0, step=0.5)
    from_unit = st.selectbox("de", UNITS, index=7, key="prop_from")
    to_unit = st.selectbox("para", UNITS, index=3, key="prop_to")
    out = simple_proportional(rate, from_unit, to_unit)
    st.metric("taxa proporcional", f"{pct(out)} {to_unit}")
    if show_formula:
        formula_box("pela fórmula", f"i_destino = {rate:.6f} × ({PER_YEAR[from_unit]:.6f}/{PER_YEAR[to_unit]:.6f}) = {out:.6f}%")
    if show_hp:
        hp_box("pela hp12c", [
            "para taxa proporcional, use a lógica de regra de três / proporcionalidade.",
            f"ex.: {rate} {from_unit} -> {to_unit}",
            f"resultado = {out:.6f}%",
        ])

# taxas equivalentes
with tabs[3]:
    rate = st.number_input("taxa efetiva de origem (%)", value=18.0, step=0.5, key="eq_rate")
    from_unit = st.selectbox("de", UNITS, index=7, key="eq_from")
    to_unit = st.selectbox("para", UNITS, index=5, key="eq_to")
    out = equivalent_rate(rate, from_unit, to_unit)
    st.metric("taxa equivalente", f"{pct(out)} {to_unit}")
    if show_formula:
        expo = TIME_FACTORS[to_unit] / TIME_FACTORS[from_unit]
        formula_box("pela fórmula", f"i_destino = (1 + {rate/100:.6f})^({expo:.6f}) - 1\ni_destino = {out:.6f}%")
    if show_hp:
        hp_box("pela hp12c", [
            "truque usando valor base 100:",
            "100 CHS PV",
            f"{rate} i",
            "0 PMT",
            f"1 n  -> unidade de origem",
            f"FV = 100 × (1+i_origem)",
            f"depois encontrar i na unidade destino equivalente",
            f"resultado: {out:.6f}% {to_unit}",
        ])

# nominal x efetiva
with tabs[4]:
    nom = st.number_input("taxa nominal (%)", value=24.0, step=0.5)
    nominal_unit = st.selectbox("unidade anunciada da taxa nominal", UNITS, index=7, key="nominal_unit")
    cap_unit = st.selectbox("capitalização", UNITS, index=3, key="cap_unit")
    eff_cap = effective_from_nominal(nom, nominal_unit, cap_unit)
    annual_eff = annual_effective_from_effective(eff_cap, cap_unit)
    st.metric("taxa efetiva na unidade de capitalização", f"{pct(eff_cap)} {cap_unit}")
    st.metric("taxa efetiva anual", pct(annual_eff))
    if show_formula:
        formula_box("pela fórmula", f"taxa efetiva na capitalização = {nom:.6f} × ({TIME_FACTORS[cap_unit]:.6f}/{TIME_FACTORS[nominal_unit]:.6f}) = {eff_cap:.6f}%\n"
                                     f"taxa efetiva anual = (1 + {eff_cap/100:.6f})^{PER_YEAR[cap_unit]:.6f} - 1 = {annual_eff:.6f}%")
    if show_hp:
        hp_box("pela hp12c", [
            "1) transformar a taxa nominal em taxa efetiva na unidade da capitalização por proporção",
            f"{nom} {nominal_unit} -> {eff_cap:.6f}% {cap_unit}",
            "2) usar valor base 100 para levar à taxa efetiva anual",
            "100 CHS PV",
            f"{eff_cap:.6f} i",
            "0 PMT",
            f"{int(round(PER_YEAR[cap_unit]))} n",
            "FV",
            f"resultado anual efetivo = {annual_eff:.6f}%",
        ])

# taxa real
with tabs[5]:
    mode = st.radio("o que você quer descobrir?", ["taxa real embutida", "taxa bruta necessária"], horizontal=True)
    if mode == "taxa real embutida":
        gross = st.number_input("rendimento efetivo (%)", value=10.24, step=0.1)
        infl = st.number_input("inflação (%)", value=4.0, step=0.1)
        real = rate_real_from_gross(gross, infl)
        st.metric("taxa real", pct(real))
        if show_formula:
            formula_box("pela fórmula", f"i_real = (1 + {gross/100:.6f}) / (1 + {infl/100:.6f}) - 1 = {real:.6f}%")
        if show_hp:
            hp_box("pela hp12c", [
                "não há tecla direta de taxa real; faça pela expressão equivalente.",
                f"1 + i_bruta = {1 + gross/100:.6f}",
                f"1 + inflação = {1 + infl/100:.6f}",
                f"dividir: {(1 + gross/100):.6f} / {(1 + infl/100):.6f} = {((1 + gross/100)/(1 + infl/100)):.6f}",
                f"tirar 1 -> {real:.6f}%",
            ])
    else:
        real = st.number_input("taxa real desejada (%)", value=6.0, step=0.1)
        infl = st.number_input("inflação (%)", value=4.0, step=0.1, key="tr_infl")
        gross = gross_required_for_real(real, infl)
        st.metric("taxa bruta necessária", pct(gross))
        if show_formula:
            formula_box("pela fórmula", f"i_bruta = (1 + {real/100:.6f}) × (1 + {infl/100:.6f}) - 1 = {gross:.6f}%")
        if show_hp:
            hp_box("pela hp12c", [
                "não há tecla direta de taxa real; use o produto dos fatores.",
                f"1 + i_real = {1 + real/100:.6f}",
                f"1 + inflação = {1 + infl/100:.6f}",
                f"multiplicar: {(1 + real/100):.6f} × {(1 + infl/100):.6f} = {((1 + real/100)*(1 + infl/100)):.6f}",
                f"tirar 1 -> {gross:.6f}%",
            ])

# juros simples
with tabs[6]:
    what = st.selectbox("descobrir", ["montante (M)", "capital (C)", "taxa (i)", "tempo (n)"])
    rate_unit = st.selectbox("unidade da taxa", UNITS, index=3, key="js_rate_unit")
    time_unit = st.selectbox("unidade do tempo informado", UNITS, index=3, key="js_time_unit")
    C = st.number_input("capital C", value=50000.0, step=1000.0) if what != "capital (C)" else None
    i_pct = st.number_input("taxa (%)", value=5.0, step=0.1) if what != "taxa (i)" else None
    n_in = st.number_input("tempo", value=9.0, step=1.0) if what != "tempo (n)" else None
    M = st.number_input("montante M", value=72500.0, step=1000.0) if what != "montante (M)" else None
    n_rate = convert_time(n_in, time_unit, rate_unit) if n_in is not None else None
    C2, i2, n2, M2, J2 = solve_simple(C, i_pct, n_rate, M)
    st.metric("capital", money(C2))
    st.metric("taxa", pct(i2))
    if what == "tempo (n)" and n2 is not None:
        st.metric(f"tempo em {rate_unit}", f"{n2:.6f}")
        st.metric(f"tempo em {time_unit}", f"{convert_time(n2, rate_unit, time_unit):.6f}")
    else:
        st.metric("montante", money(M2))
    st.metric("juros", money(J2))
    if show_formula:
        if what == "montante (M)":
            formula_box("pela fórmula", f"M = C × (1 + i × n)\nM = {C2:.6f} × (1 + {i2/100:.6f} × {n2:.6f}) = {M2:.6f}")
        elif what == "capital (C)":
            formula_box("pela fórmula", f"C = M / (1 + i × n)\nC = {M2:.6f} / (1 + {i2/100:.6f} × {n2:.6f}) = {C2:.6f}")
        elif what == "taxa (i)":
            formula_box("pela fórmula", f"i = (M/C - 1) / n\ni = ({M2:.6f}/{C2:.6f} - 1) / {n2:.6f} = {i2/100:.6f} = {i2:.6f}%")
        else:
            formula_box("pela fórmula", f"n = (M/C - 1) / i\nn = ({M2:.6f}/{C2:.6f} - 1) / {i2/100:.6f} = {n2:.6f} {rate_unit}")
    if show_hp:
        hp_box("pela hp12c", [
            "juros simples não usam diretamente as 5 teclas financeiras da hp12c.",
            "faça pela fórmula ou por proporcionalidade.",
            f"C = {money(C2)}",
            f"i = {pct(i2)} por {rate_unit}",
            f"n = {n2:.6f} {rate_unit}",
            f"M = {money(M2)}",
        ])

# juros compostos
with tabs[7]:
    what = st.selectbox("descobrir", ["valor futuro (FV)", "valor presente (PV)", "taxa (i)", "tempo (n)"])
    rate_unit = st.selectbox("unidade da taxa", UNITS, index=7, key="jc_rate_unit")
    time_unit = st.selectbox("unidade do tempo informado", UNITS, index=7, key="jc_time_unit")
    PV = st.number_input("valor presente PV", value=1000.0, step=100.0) if what != "valor presente (PV)" else None
    i_pct = st.number_input("taxa (%)", value=20.0, step=0.1) if what != "taxa (i)" else None
    n_in = st.number_input("tempo", value=3.0, step=0.5) if what != "tempo (n)" else None
    FV = st.number_input("valor futuro FV", value=1728.0, step=100.0) if what != "valor futuro (FV)" else None
    n_rate = convert_time(n_in, time_unit, rate_unit) if n_in is not None else None
    PV2, i2, n2, FV2, J2 = solve_compound(PV, i_pct, n_rate, FV)
    st.metric("valor presente", money(PV2))
    st.metric("taxa", pct(i2))
    if what == "tempo (n)" and n2 is not None:
        st.metric(f"tempo em {rate_unit}", f"{n2:.6f}")
        st.metric(f"tempo em {time_unit}", f"{convert_time(n2, rate_unit, time_unit):.6f}")
    else:
        st.metric("valor futuro", money(FV2))
    st.metric("juros acumulados", money(J2))
    if show_formula:
        if what == "valor futuro (FV)":
            formula_box("pela fórmula", f"FV = PV × (1 + i)^n\nFV = {PV2:.6f} × (1 + {i2/100:.6f})^{n2:.6f} = {FV2:.6f}")
        elif what == "valor presente (PV)":
            formula_box("pela fórmula", f"PV = FV / (1 + i)^n\nPV = {FV2:.6f} / (1 + {i2/100:.6f})^{n2:.6f} = {PV2:.6f}")
        elif what == "taxa (i)":
            formula_box("pela fórmula", f"i = (FV/PV)^(1/n) - 1\ni = ({FV2:.6f}/{PV2:.6f})^(1/{n2:.6f}) - 1 = {i2:.6f}%")
        else:
            formula_box("pela fórmula", f"n = ln(FV/PV) / ln(1+i)\nn = ln({FV2:.6f}/{PV2:.6f}) / ln(1 + {i2/100:.6f}) = {n2:.6f} {rate_unit}")
    if show_hp:
        hp_box("pela hp12c", [
            f"{abs(PV2):.2f} PV",
            f"{abs(FV2):.2f} {'CHS ' if FV2<0 else ''}FV",
            "0 PMT",
            f"{n2:.6f} n",
            f"{i2:.6f} i",
            "resolver a incógnita desejada",
        ])

# descontos simples/compostos helpers UI

def render_discount_page(kind: str):
    c1, c2 = st.columns(2)
    with c1:
        solve_for = st.selectbox("descobrir", ["valor presente (PV)", "desconto (D)", "taxa", "valor futuro (FV)"], key=f"sf_{kind}")
        FV = st.number_input("valor futuro / nominal (FV)", value=65000.0, step=1000.0, key=f"fv_{kind}") if solve_for != "valor futuro (FV)" else None
        rate = st.number_input("taxa (%)", value=3.0, step=0.1, key=f"rate_{kind}") if solve_for != "taxa" else None
    with c2:
        rate_unit = st.selectbox("unidade da taxa", UNITS, index=3, key=f"ru_{kind}")
        time_value = st.number_input("tempo", value=8.0, step=1.0, key=f"tv_{kind}")
        time_unit = st.selectbox("unidade do tempo", UNITS, index=3, key=f"tu_{kind}")
    n = convert_time(time_value, time_unit, rate_unit)

    def calc(fv, rt, nn):
        if kind == "racional simples":
            return desconto_racional_simples(fv, rt, nn)
        if kind == "comercial simples":
            return desconto_comercial_simples(fv, rt, nn)
        if kind == "racional composto":
            return desconto_racional_composto(fv, rt, nn)
        return desconto_comercial_composto(fv, rt, nn)

    if solve_for in ["valor presente (PV)", "desconto (D)"]:
        pv, d = calc(FV, rate, n)
        st.metric("valor presente / antecipado", money(pv))
        st.metric("desconto", money(d))
        if show_formula:
            if kind == "racional simples":
                formula_box("pela fórmula", f"PV = FV / (1 + i·n)\nPV = {FV:.6f} / (1 + {rate/100:.6f}×{n:.6f}) = {pv:.6f}\nD = FV - PV = {FV:.6f} - {pv:.6f} = {d:.6f}")
            elif kind == "comercial simples":
                formula_box("pela fórmula", f"D = FV·d·n\nD = {FV:.6f}×{rate/100:.6f}×{n:.6f} = {d:.6f}\nPV = FV - D = {FV:.6f} - {d:.6f} = {pv:.6f}")
            elif kind == "racional composto":
                formula_box("pela fórmula", f"PV = FV / (1+i)^n\nPV = {FV:.6f} / (1 + {rate/100:.6f})^{n:.6f} = {pv:.6f}\nD = FV - PV = {FV:.6f} - {pv:.6f} = {d:.6f}")
            else:
                formula_box("pela fórmula", f"PV = FV·(1-d)^n\nPV = {FV:.6f}×(1-{rate/100:.6f})^{n:.6f} = {pv:.6f}\nD = FV - PV = {FV:.6f} - {pv:.6f} = {d:.6f}")
        if show_hp:
            if kind == "racional simples":
                hp_box("pela hp12c", ["para racional simples, usar a conta direta:", "PV = FV ÷ (1 + i×n)", f"unidades convertidas: n = {n:.6f} {rate_unit}"])
            elif kind == "comercial simples":
                hp_box("pela hp12c", [f"D = FV×d×n = {FV:.6f}×{rate/100:.6f}×{n:.6f}", "PV = FV - D", f"unidades convertidas: n = {n:.6f} {rate_unit}"])
            elif kind == "racional composto":
                hp_box("pela hp12c", ["f REG", f"{FV:.10g} FV", f"{rate:.10g} i", f"{n:.10g} n", "PV"])
            else:
                hp_box("pela hp12c", ["1 ENTER d -", "n y^x", "× FV", "resultado = PV"])
    elif solve_for == "taxa":
        target = st.number_input("valor presente / antecipado (PV)", value=49400.0 if "simples" in kind else 51311.60, step=100.0, key=f"target_{kind}")
        if kind == "racional simples":
            i = ((FV / target) - 1) / n * 100
            pv, d = desconto_racional_simples(FV, i, n)
        elif kind == "comercial simples":
            d_pct = (FV - target) / (FV * n) * 100
            i = d_pct
            pv, d = desconto_comercial_simples(FV, i, n)
        elif kind == "racional composto":
            i = ((FV / target) ** (1 / n) - 1) * 100
            pv, d = desconto_racional_composto(FV, i, n)
        else:
            i = (1 - (target / FV) ** (1 / n)) * 100
            pv, d = desconto_comercial_composto(FV, i, n)
        st.metric("taxa", pct(i))
        st.metric("desconto", money(d))
        if show_formula:
            if kind == "racional simples":
                formula_box("pela fórmula", f"i = ((FV/PV) - 1) / n\ni = (({FV:.6f}/{target:.6f}) - 1) / {n:.6f} = {i/100:.8f}\ni = {i:.6f}%")
            elif kind == "comercial simples":
                formula_box("pela fórmula", f"d = (FV - PV) / (FV·n)\nd = ({FV:.6f} - {target:.6f}) / ({FV:.6f}×{n:.6f}) = {i/100:.8f}\nd = {i:.6f}%")
            elif kind == "racional composto":
                formula_box("pela fórmula", f"i = (FV/PV)^(1/n) - 1\ni = ({FV:.6f}/{target:.6f})^(1/{n:.6f}) - 1 = {i/100:.8f}\ni = {i:.6f}%")
            else:
                formula_box("pela fórmula", f"d = 1 - (PV/FV)^(1/n)\nd = 1 - ({target:.6f}/{FV:.6f})^(1/{n:.6f}) = {i/100:.8f}\nd = {i:.6f}%")
        if show_hp:
            hp_box("pela hp12c", [f"use FV = {FV:.6f}, PV = {target:.6f}, n = {n:.6f}", "e resolva a taxa pela relação correspondente ao tipo de desconto."])
    else:  # solve FV
        target = st.number_input("valor presente / antecipado (PV)", value=9600.0, step=100.0, key=f"pvsolve_{kind}")
        if kind == "racional simples":
            fv = target * (1 + rate / 100 * n)
            pv, d = desconto_racional_simples(fv, rate, n)
        elif kind == "comercial simples":
            fv = target / (1 - rate / 100 * n)
            pv, d = desconto_comercial_simples(fv, rate, n)
        elif kind == "racional composto":
            fv = target * ((1 + rate / 100) ** n)
            pv, d = desconto_racional_composto(fv, rate, n)
        else:
            fv = target / ((1 - rate / 100) ** n)
            pv, d = desconto_comercial_composto(fv, rate, n)
        st.metric("valor futuro / nominal", money(fv))
        st.metric("desconto", money(d))
        if show_formula:
            if kind == "racional simples":
                formula_box("pela fórmula", f"FV = PV·(1+i·n)\nFV = {target:.6f}×(1+{rate/100:.6f}×{n:.6f}) = {fv:.6f}")
            elif kind == "comercial simples":
                formula_box("pela fórmula", f"FV = PV / (1-d·n)\nFV = {target:.6f} / (1-{rate/100:.6f}×{n:.6f}) = {fv:.6f}")
            elif kind == "racional composto":
                formula_box("pela fórmula", f"FV = PV·(1+i)^n\nFV = {target:.6f}×(1+{rate/100:.6f})^{n:.6f} = {fv:.6f}")
            else:
                formula_box("pela fórmula", f"FV = PV / (1-d)^n\nFV = {target:.6f} / (1-{rate/100:.6f})^{n:.6f} = {fv:.6f}")
        if show_hp:
            hp_box("pela hp12c", [f"use PV = {target:.6f}, taxa = {rate:.6f}%, n = {n:.6f}", "e isole FV pela relação do tipo de desconto."])

    if show_formula:
        if solve_for in ["valor presente (PV)", "desconto (D)"]:
            if kind == "racional simples":
                formula_box("pela fórmula", f"PV = FV / (1 + i × n)\nPV = {FV:.6f} / (1 + {rate/100:.6f} × {n:.6f}) = {pv:.6f}\nD = FV - PV = {d:.6f}")
            elif kind == "comercial simples":
                formula_box("pela fórmula", f"D = FV × d × n\nD = {FV:.6f} × {rate/100:.6f} × {n:.6f} = {d:.6f}\nPV = FV - D = {pv:.6f}")
            elif kind == "racional composto":
                formula_box("pela fórmula", f"PV = FV / (1 + i)^n\nPV = {FV:.6f} / (1 + {rate/100:.6f})^{n:.6f} = {pv:.6f}\nD = FV - PV = {d:.6f}")
            else:
                formula_box("pela fórmula", f"PV = FV × (1 - d)^n\nPV = {FV:.6f} × (1 - {rate/100:.6f})^{n:.6f} = {pv:.6f}\nD = FV - PV = {d:.6f}")
        elif solve_for == "taxa":
            if kind == "racional simples":
                formula_box("pela fórmula", f"i = (FV/PV - 1) / n\ni = ({FV:.6f}/{target:.6f} - 1) / {n:.6f} = {i:.6f}%")
            elif kind == "comercial simples":
                formula_box("pela fórmula", f"d = (FV - PV) / (FV × n)\nd = ({FV:.6f} - {target:.6f}) / ({FV:.6f} × {n:.6f}) = {i:.6f}%")
            elif kind == "racional composto":
                formula_box("pela fórmula", f"i = (FV/PV)^(1/n) - 1\ni = ({FV:.6f}/{target:.6f})^(1/{n:.6f}) - 1 = {i:.6f}%")
            else:
                formula_box("pela fórmula", f"d = 1 - (PV/FV)^(1/n)\nd = 1 - ({target:.6f}/{FV:.6f})^(1/{n:.6f}) = {i:.6f}%")
        else:
            if kind == "racional simples":
                formula_box("pela fórmula", f"FV = PV × (1 + i × n)\nFV = {target:.6f} × (1 + {rate/100:.6f} × {n:.6f}) = {fv:.6f}")
            elif kind == "comercial simples":
                formula_box("pela fórmula", f"FV = PV / (1 - d × n)\nFV = {target:.6f} / (1 - {rate/100:.6f} × {n:.6f}) = {fv:.6f}")
            elif kind == "racional composto":
                formula_box("pela fórmula", f"FV = PV × (1 + i)^n\nFV = {target:.6f} × (1 + {rate/100:.6f})^{n:.6f} = {fv:.6f}")
            else:
                formula_box("pela fórmula", f"FV = PV / (1 - d)^n\nFV = {target:.6f} / (1 - {rate/100:.6f})^{n:.6f} = {fv:.6f}")
    if show_hp:
        hp_lines = ["0 PMT"]
        if solve_for in ["valor presente (PV)", "desconto (D)"]:
            hp_lines = [f"{abs(FV):.2f} CHS FV", f"{rate:.6f} i", f"{n:.6f} n", "PV"]
        elif solve_for == "taxa":
            hp_lines = [f"{abs(target):.2f} PV", f"{abs(FV):.2f} CHS FV", "0 PMT", f"{n:.6f} n", "i"]
        else:
            hp_lines = [f"{abs(target):.2f} PV", f"{rate:.6f} i", "0 PMT", f"{n:.6f} n", "FV"]
        hp_box("pela hp12c", hp_lines)

with tabs[8]:
    title_small("desconto racional simples (por dentro)")
    render_discount_page("racional simples")

with tabs[9]:
    title_small("desconto comercial simples (por fora)")
    render_discount_page("comercial simples")

with tabs[10]:
    title_small("desconto racional composto (por dentro)")
    render_discount_page("racional composto")

with tabs[11]:
    title_small("desconto comercial composto (por fora)")
    render_discount_page("comercial composto")

with tabs[12]:
    mode = st.selectbox("modalidade base", [
        "desconto racional simples",
        "desconto comercial simples",
        "desconto racional composto",
        "desconto comercial composto",
    ])
    c1, c2 = st.columns(2)
    with c1:
        FV = st.number_input("valor futuro / nominal (FV)", value=25000.0, step=1000.0)
        rate = st.number_input("taxa da operação (%)", value=2.0, step=0.1)
        rate_unit = st.selectbox("unidade da taxa", UNITS, index=3)
    with c2:
        time_value = st.number_input("tempo", value=5.0, step=1.0)
        time_unit = st.selectbox("unidade do tempo", UNITS, index=3)
        n = convert_time(time_value, time_unit, rate_unit)
    saldo_medio_pct = st.number_input("saldo médio retido (%)", value=0.0, step=1.0)
    remun_saldo_pct = st.number_input("remuneração do saldo médio (%)", value=0.0, step=0.1)
    despesa_pct = st.number_input("despesa administrativa (%)", value=0.0, step=0.5)
    out = effective_discount_cost(FV, n, mode, rate, saldo_medio_pct, despesa_pct, remun_saldo_pct)
    st.metric("valor presente base", money(out["pv_base"]))
    st.metric("desconto", money(out["desconto"]))
    st.metric("valor líquido liberado hoje", money(out["pv_liquido"]))
    st.metric("valor líquido pago no vencimento", money(out["fv_liquido"]))
    st.metric(f"custo efetivo em {rate_unit}", pct(out["i_eff_pct"]))
    annual_cost = annual_effective_from_effective(out["i_eff_pct"], rate_unit)
    st.metric("custo efetivo anual", pct(annual_cost))
    if show_formula:
        formula_box("pela fórmula", f"PV líquido = PV base - saldo retido - despesa\n"
                                     f"PV líquido = {out['pv_base']:.6f} - {out['saldo_retido']:.6f} - {out['despesa']:.6f} = {out['pv_liquido']:.6f}\n"
                                     f"FV líquido = FV - saldo no vencimento = {FV:.6f} - {out['saldo_no_venc']:.6f} = {out['fv_liquido']:.6f}\n"
                                     f"i efetiva = (FV líquido / PV líquido)^(1/n) - 1 = {out['i_eff_pct']:.6f}%")
    if show_hp:
        hp_box("pela hp12c", [
            f"{out['pv_liquido']:.2f} PV",
            f"{out['fv_liquido']:.2f} CHS FV",
            "0 PMT",
            f"{n:.6f} n",
            "i",
            f"resultado = {out['i_eff_pct']:.6f}% por {rate_unit}",
        ])

with tabs[13]:
    sub = st.radio("tipo", ["postecipada", "antecipada", "diferida / carência", "perpetuidade", "resolver taxa implícita"], horizontal=True)
    if sub in ["postecipada", "antecipada", "diferida / carência"]:
        due = "END" if sub == "postecipada" else "BEG"
        what = st.selectbox("descobrir", ["PMT", "PV", "FV"])
        c1, c2 = st.columns(2)
        with c1:
            rate = st.number_input("taxa informada (%)", value=1.8 if sub != "perpetuidade" else 6.0, step=0.1)
            rate_unit = st.selectbox("unidade da taxa", UNITS, index=3, key=f"su_rate_{sub}")
            payment_unit = st.selectbox("periodicidade dos pagamentos", UNITS, index=3, key=f"su_pay_{sub}")
            i_pay = rate_to_payment_period(rate, rate_unit, payment_unit)
        with c2:
            n = st.number_input("número de pagamentos", value=36 if sub != "diferida / carência" else 6, step=1)
            car = st.number_input("carência (em períodos de pagamento)", value=2 if sub == "diferida / carência" else 0, step=1)
            pv = st.number_input("PV", value=36000.0 if what == "PMT" else 0.0, step=1000.0)
            fv = st.number_input("FV", value=0.0, step=1000.0)
            pmt = st.number_input("PMT", value=1000.0, step=100.0) if what != "PMT" else 0.0
        if sub == "diferida / carência":
            due = "END"
            if what == "PMT":
                pv_at_start = pv * ((1 + i_pay / 100) ** car)
                result = annuity_pmt(pv_at_start, i_pay, int(n), due="END", fv=fv)
                st.metric("PMT", money(abs(result)))
            elif what == "PV":
                pv_at_start = annuity_pv(-abs(pmt), i_pay, int(n), due="END", fv=fv)
                result = pv_at_start / ((1 + i_pay / 100) ** car)
                st.metric("PV hoje", money(abs(result)))
            else:
                result = annuity_fv(-abs(pmt), i_pay, int(n), due="END", pv=0.0)
                st.metric("FV da série", money(abs(result)))
        else:
            if what == "PMT":
                result = annuity_pmt(pv, i_pay, int(n), due=due, fv=fv)
            elif what == "PV":
                result = annuity_pv(-abs(pmt), i_pay, int(n), due=due, fv=fv)
            else:
                result = annuity_fv(-abs(pmt), i_pay, int(n), due=due, pv=pv)
            st.metric(what, money(abs(result)))
        st.caption(f"taxa equivalente por período de pagamento = {pct(i_pay)} {payment_unit}")
        if show_formula:
            if sub == "diferida / carência":
                if what == "PMT":
                    formula_box("pela fórmula", f"PV no início da série = PV hoje × (1+i)^carência\nPV série = {pv:.6f} × (1 + {i_pay/100:.6f})^{car:.6f} = {pv_at_start:.6f}\n"
                                                 f"PMT = {result:.6f}")
                elif what == "PV":
                    formula_box("pela fórmula", f"PV no início da série = PMT × [1-(1+i)^(-n)]/i\n"
                                                 f"PV hoje = PV início / (1+i)^carência = {result:.6f}")
                else:
                    formula_box("pela fórmula", f"FV = PMT × [((1+i)^n -1)/i] = {result:.6f}")
            else:
                if what == "PMT":
                    formula_box("pela fórmula", f"PMT = -[(PV×(1+i)^n + FV)×i] / [((1+i)^n-1)×fator]\nPMT = {result:.6f}")
                elif what == "PV":
                    formula_box("pela fórmula", f"PV = -[((PMT×fator)×(((1+i)^n-1)/i)+FV)/(1+i)^n]\nPV = {result:.6f}")
                else:
                    formula_box("pela fórmula", f"FV = -PV×(1+i)^n - PMT×fator×[((1+i)^n-1)/i]\nFV = {result:.6f}")
        if show_hp:
            hp_mode = "END" if due == "END" else "BEG"
            hp_lines = [f"g {hp_mode}" if hp_mode=="BEG" else "g END"]
            if what != "PV":
                hp_lines.append(f"{abs(pv):.2f} PV")
            if what != "PMT":
                hp_lines.append(f"{abs(pmt):.2f} CHS PMT")
            hp_lines.append(f"{i_pay:.6f} i")
            hp_lines.append(f"{int(n)} n")
            if what != "FV":
                hp_lines.append(f"{abs(fv):.2f} FV")
            hp_lines.append(what)
            hp_box("pela hp12c", hp_lines)
    elif sub == "perpetuidade":
        what = st.selectbox("descobrir", ["PV", "PMT"])
        rate = st.number_input("taxa (%)", value=6.0, step=0.1)
        rate_unit = st.selectbox("unidade da taxa", UNITS, index=7, key="perp_unit")
        if what == "PV":
            pmt = st.number_input("PMT", value=12000.0, step=1000.0)
            out = perpetuity_pv(pmt, rate)
        else:
            pv = st.number_input("PV", value=200000.0, step=1000.0)
            out = perpetuity_pmt(pv, rate)
        st.metric(what, money(out) if what == "PV" else money(out))
        st.caption(f"resultado na periodicidade da taxa: {rate_unit}")
        if show_formula:
            if what == "PV":
                formula_box("pela fórmula", f"PV = PMT / i\nPV = {pmt:.6f} / {rate/100:.6f} = {out:.6f}")
            else:
                formula_box("pela fórmula", f"PMT = PV × i\nPMT = {pv:.6f} × {rate/100:.6f} = {out:.6f}")
        if show_hp:
            hp_box("pela hp12c", [
                "aproximação de perpetuidade usando n muito alto, por exemplo 100.",
                f"{pmt if what=='PV' else pv:.2f} {'CHS ' if what=='PV' else ''}{'PMT' if what=='PV' else 'PV'}",
                f"{rate:.6f} i",
                "100 n",
                "0 FV",
                f"{what}",
            ])
    else:
        pv = st.number_input("PV / preço à vista", value=10000.0, step=1000.0)
        pmt = st.number_input("PMT", value=1000.0, step=100.0)
        n = st.number_input("número de pagamentos", value=12, step=1)
        due_txt = st.selectbox("tipo da série", ["postecipada", "antecipada"])
        due = "END" if due_txt == "postecipada" else "BEG"
        i = annuity_rate_bisect(pv, -abs(pmt), int(n), due=due, fv=0.0)
        st.metric("taxa implícita por período", pct(i) if i is not None else "não encontrada")
        if i is not None and show_formula:
            formula_box("pela fórmula", f"resolver numericamente a equação da anuidade para PV={pv:.6f}, PMT={abs(pmt):.6f}, n={int(n)}\nresultado: i = {i:.6f}%")
        if i is not None and show_hp:
            hp_box("pela hp12c", [
                f"g {'END' if due=='END' else 'BEG'}",
                f"{pv:.2f} PV",
                f"{abs(pmt):.2f} CHS PMT",
                "0 FV",
                f"{int(n)} n",
                "i",
            ])

with tabs[14]:
    sub = st.radio("caso", ["entrada + parcelas", "taxa implícita com entrada"], horizontal=True)
    cash_price = st.number_input("valor à vista / preço de referência", value=3000.0, step=100.0)
    entry = st.number_input("entrada paga hoje", value=0.0, step=100.0)
    n = st.number_input("número de parcelas", value=4, step=1)
    due_txt = st.selectbox("tipo", ["postecipada", "antecipada"], key="ep_due")
    due = "END" if due_txt == "postecipada" else "BEG"
    if sub == "entrada + parcelas":
        rate = st.number_input("taxa informada (%)", value=2.0, step=0.1)
        rate_unit = st.selectbox("unidade da taxa", UNITS, index=3, key="ep_ru")
        payment_unit = st.selectbox("periodicidade das parcelas", UNITS, index=3, key="ep_pu")
        i_pay = rate_to_payment_period(rate, rate_unit, payment_unit)
        pmt = pmt_with_entry(entry, cash_price, i_pay, int(n), due=due)
        st.metric("valor da parcela", money(abs(pmt)))
        st.caption(f"taxa equivalente por parcela = {pct(i_pay)} {payment_unit}")
        if show_formula:
            formula_box("pela fórmula", f"valor financiado = preço à vista - entrada = {cash_price:.6f} - {entry:.6f} = {cash_price-entry:.6f}\nPMT = {pmt:.6f}")
        if show_hp:
            hp_box("pela hp12c", [
                f"g {'END' if due=='END' else 'BEG'}",
                f"{cash_price-entry:.2f} PV",
                f"{i_pay:.6f} i",
                f"{int(n)} n",
                "0 FV",
                "PMT",
            ])
    else:
        pmt = st.number_input("valor da parcela", value=750.0, step=50.0)
        rate = implied_rate_with_entry(entry, cash_price, -abs(pmt), int(n), due=due)
        st.metric("taxa implícita por parcela", pct(rate) if rate is not None else "não encontrada")
        if rate is not None and show_formula:
            formula_box("pela fórmula", f"valor financiado = {cash_price:.6f} - {entry:.6f} = {cash_price-entry:.6f}\nresolver numericamente a anuidade\nresultado: i = {rate:.6f}%")
        if rate is not None and show_hp:
            hp_box("pela hp12c", [
                f"g {'END' if due=='END' else 'BEG'}",
                f"{cash_price-entry:.2f} PV",
                f"{abs(pmt):.2f} CHS PMT",
                "0 FV",
                f"{int(n)} n",
                "i",
            ])

with tabs[15]:
    sub = st.radio("caso", ["trocar parcelas remanescentes", "substituir dívidas irregulares por parcelas iguais"], horizontal=True)
    if sub == "trocar parcelas remanescentes":
        old_pmt = st.number_input("parcela antiga", value=4727.98, step=100.0)
        old_rate = st.number_input("taxa antiga (%)", value=2.0, step=0.1)
        old_unit = st.selectbox("unidade da taxa antiga", UNITS, index=3)
        rem_n = st.number_input("parcelas antigas restantes", value=6, step=1)
        new_rate = st.number_input("taxa nova (%)", value=2.0, step=0.1)
        new_unit = st.selectbox("unidade da taxa nova", UNITS, index=3)
        new_n = st.number_input("novas parcelas", value=18, step=1)
        # mesma periodicidade mensal por padrão na renegociação de parcelas
        old_i = rate_to_payment_period(old_rate, old_unit, "mês")
        new_i = rate_to_payment_period(new_rate, new_unit, "mês")
        debt = annuity_pv(-abs(old_pmt), old_i, int(rem_n), due="END", fv=0.0)
        new_pmt = annuity_pmt(debt, new_i, int(new_n), due="END", fv=0.0)
        st.metric("dívida no momento da renegociação", money(abs(debt)))
        st.metric("nova parcela", money(abs(new_pmt)))
        if show_formula:
            formula_box("pela fórmula", f"1) dívida no momento da renegociação = valor presente das parcelas restantes = {debt:.6f}\n2) nova PMT calculada sobre essa dívida = {new_pmt:.6f}")
        if show_hp:
            hp_box("pela hp12c", [
                "passo 1 - achar a dívida atual",
                f"{abs(old_pmt):.2f} CHS PMT",
                f"{old_i:.6f} i",
                f"{int(rem_n)} n",
                "0 FV",
                "PV",
                "passo 2 - recalcular a nova PMT",
                f"{abs(debt):.2f} PV",
                f"{new_i:.6f} i",
                f"{int(new_n)} n",
                "0 FV",
                "PMT",
            ])
    else:
        st.caption("informe as dívidas futuras e o app traz a valor presente para calcular parcelas iguais.")
        rate = st.number_input("taxa (%)", value=24.0, step=0.1)
        rate_unit = st.selectbox("unidade da taxa", UNITS, index=7, key="ren_irreg_ru")
        payment_unit = st.selectbox("periodicidade das novas parcelas", UNITS, index=3, key="ren_irreg_pu")
        i_pay = rate_to_payment_period(rate, rate_unit, payment_unit)
        rows = int(st.number_input("quantidade de dívidas", value=3, step=1, min_value=1, max_value=20))
        base_df = pd.DataFrame({"período": list(range(1, rows + 1)), "valor": [0.0] * rows})
        df = st.data_editor(base_df, num_rows="fixed", use_container_width=True, key="ren_df")
        new_n = int(st.number_input("quantidade de novas parcelas iguais", value=4, step=1, key="ren_n"))
        first_when = st.selectbox("primeira nova parcela", ["1 período após hoje", "hoje"], key="ren_first")
        due = "END" if first_when == "1 período após hoje" else "BEG"
        pv_total = 0.0
        for _, row in df.iterrows():
            t = int(float(nz(row["período"], 0)))
            val = float(nz(row["valor"], 0.0))
            pv_total += val / ((1 + i_pay / 100) ** t)
        new_pmt = annuity_pmt(pv_total, i_pay, new_n, due=due, fv=0.0)
        st.metric("valor presente das dívidas", money(pv_total))
        st.metric("nova parcela", money(abs(new_pmt)))
        if show_formula:
            formula_box("pela fórmula", f"1) trazer cada dívida a valor presente na taxa {i_pay:.6f}%\n2) somar os valores presentes = {pv_total:.6f}\n3) recalcular a PMT uniforme = {new_pmt:.6f}")
        if show_hp:
            hp_box("pela hp12c", [
                "primeiro, trazer as dívidas a valor presente uma a uma e somar.",
                f"PV total = {pv_total:.2f}",
                f"g {'END' if due=='END' else 'BEG'}",
                f"{pv_total:.2f} PV",
                f"{i_pay:.6f} i",
                f"{int(new_n)} n",
                "0 FV",
                "PMT",
            ])

with tabs[16]:
    period_unit = st.selectbox("unidade dos períodos do fluxo", UNITS, index=7)
    rate = st.number_input("taxa para VPL (%)", value=10.0, step=0.1)
    rate_unit = st.selectbox("unidade da taxa informada", UNITS, index=7)
    rows = int(st.number_input("quantidade de linhas do fluxo", value=7, step=1, min_value=2, max_value=60))
    df0 = pd.DataFrame({"período": list(range(rows)), "fluxo": [0.0] * rows})
    if rows >= 7:
        df0.loc[0, "fluxo"] = -1200.0
        df0.loc[1, "fluxo"] = 300.0
        df0.loc[2, "fluxo"] = 400.0
        df0.loc[3, "fluxo"] = 400.0
        df0.loc[4, "fluxo"] = 500.0
        df0.loc[5, "fluxo"] = 500.0
        df0.loc[6, "fluxo"] = 500.0
    df = st.data_editor(df0, num_rows="fixed", use_container_width=True, key="fc_df")
    cfs = aggregate_cashflows(df)
    i_period = rate_to_payment_period(rate, rate_unit, period_unit)
    if cfs:
        vpl = npv_periodic(i_period, cfs)
        tir = irr_periodic(cfs)
        st.metric(f"VPL na taxa de {pct(i_period)} por {period_unit}", money(vpl))
        st.metric(f"TIR por {period_unit}", pct(tir) if tir is not None else "não encontrada")
        annual_tir = annual_effective_from_effective(tir, period_unit) if tir is not None else None
        if annual_tir is not None:
            st.metric("TIR efetiva anual", pct(annual_tir))
        if show_formula:
            terms = []
            for t, cf in enumerate(cfs):
                if t == 0:
                    terms.append(f"{cf:.6f}")
                else:
                    terms.append(f"{cf:.6f}/(1+{i_period/100:.6f})^{t}")
            formula_box("pela fórmula", "VPL = " + " + ".join(terms) + f"\nVPL = {vpl:.6f}\nTIR = taxa que zera o VPL = {tir:.6f}%" if tir is not None else "TIR não encontrada")
        if show_hp:
            hp_lines = ["f REG"]
            prev = None
            count = 0
            for idx, cf in enumerate(cfs):
                if idx == 0:
                    hp_lines.append(f"{abs(cf):.2f} {'CHS ' if cf < 0 else ''}g CF0")
                else:
                    if prev is None or abs(cf - prev) > 1e-12:
                        hp_lines.append(f"{abs(cf):.2f} {'CHS ' if cf < 0 else ''}g CFj")
                        count = 1
                        prev = cf
                    else:
                        count += 1
                        hp_lines[-1] = hp_lines[-1]  # mantém CFj anterior
                # simplificado; Nj mostrado abaixo quando houver repetição
            # construir versão com Nj
            hp_lines = ["f REG"]
            hp_lines.append(f"{abs(cfs[0]):.2f} {'CHS ' if cfs[0] < 0 else ''}g CF0")
            i = 1
            while i < len(cfs):
                cf = cfs[i]
                j = i
                while j + 1 < len(cfs) and abs(cfs[j + 1] - cf) < 1e-12:
                    j += 1
                hp_lines.append(f"{abs(cf):.2f} {'CHS ' if cf < 0 else ''}g CFj")
                if j > i:
                    hp_lines.append(f"{j - i + 1} g Nj")
                i = j + 1
            hp_lines.append(f"{i_period:.6f} i")
            hp_lines.append("f NPV")
            hp_lines.append("f IRR")
            hp_box("sequência hp12c aproximada", hp_lines)

with tabs[17]:
    st.subheader("comparador de bancos / taxas")
    obj = st.radio("objetivo", ["financiamento (menor taxa efetiva anual)", "investimento (maior taxa efetiva anual)"], horizontal=True)
    cols = st.columns(2)
    results = []
    for idx, col in enumerate(cols, start=1):
        with col:
            st.markdown(f"**opção {idx}**")
            kind = st.selectbox("tipo de taxa", ["efetiva", "nominal"], key=f"cmp_kind_{idx}")
            rate = st.number_input("taxa (%)", value=35.0 if idx == 1 else 32.0, step=0.1, key=f"cmp_rate_{idx}")
            rate_unit = st.selectbox("unidade anunciada", UNITS, index=7, key=f"cmp_ru_{idx}")
            cap_unit = st.selectbox("capitalização", UNITS, index=7 if idx == 1 else 3, key=f"cmp_cu_{idx}")
            if kind == "efetiva":
                eff_cap = rate
                eff_ann = annual_effective_from_effective(rate, rate_unit)
            else:
                eff_cap = effective_from_nominal(rate, rate_unit, cap_unit)
                eff_ann = annual_effective_from_effective(eff_cap, cap_unit)
            st.metric("efetiva anual", pct(eff_ann))
            results.append((idx, eff_ann))
    if len(results) == 2:
        if obj.startswith("financiamento"):
            best = min(results, key=lambda x: x[1])
        else:
            best = max(results, key=lambda x: x[1])
        st.success(f"melhor opção: opção {best[0]}")
        if show_formula:
            formula_box("pela fórmula", f"comparar as taxas efetivas anuais calculadas\nopção 1 = {results[0][1]:.6f}%\nopção 2 = {results[1][1]:.6f}%\nresultado: opção {best[0]}")
        if show_hp:
            hp_box("pela hp12c", ["1) transformar cada opção em taxa efetiva anual", "2) comparar os dois resultados", f"melhor opção: {best[0]}"])

with tabs[18]:
    st.subheader("página simples")
    st.caption("esta aba simplifica a entrada. para ver os detalhes completos pela fórmula e hp12c, use a aba específica do tema.")
    sec = st.radio(
        "tema",
        [
            "taxa proporcional",
            "taxa equivalente",
            "nominal x efetiva",
            "taxa real",
            "desconto comercial simples",
            "desconto racional composto",
            "séries uniformes",
            "custo efetivo do desconto",
            "VPL / TIR",
        ],
        horizontal=False,
    )
    if sec == "taxa proporcional":
        rate = st.number_input("taxa (%)", value=24.0, step=0.1, key="simp_prop_r")
        from_u = st.selectbox("de", UNITS, index=7, key="simp_prop_f")
        to_u = st.selectbox("para", UNITS, index=3, key="simp_prop_t")
        out = simple_proportional(rate, from_u, to_u)
        st.metric("resultado", f"{pct(out)} {to_u}")
        if show_formula:
            formula_box("pela fórmula", f"i_destino = (1 + {rate/100:.6f})^({TIME_FACTORS[to_u]/TIME_FACTORS[from_u]:.6f}) - 1 = {out:.6f}%")
        if show_hp:
            hp_box("pela hp12c", [f"usar base 100 e equivalência composta -> resultado = {out:.6f}% {to_u}"])
        if show_formula:
            formula_box("pela fórmula", f"i_destino = {rate:.6f} × ({PER_YEAR[from_u]:.6f}/{PER_YEAR[to_u]:.6f}) = {out:.6f}%")
        if show_hp:
            hp_box("pela hp12c", [f"regra de três proporcional -> resultado = {out:.6f}% {to_u}"])
    elif sec == "taxa equivalente":
        rate = st.number_input("taxa efetiva (%)", value=18.0, step=0.1, key="simp_eq_r")
        from_u = st.selectbox("de", UNITS, index=7, key="simp_eq_f")
        to_u = st.selectbox("para", UNITS, index=5, key="simp_eq_t")
        out = equivalent_rate(rate, from_u, to_u)
        st.metric("resultado", f"{pct(out)} {to_u}")
    elif sec == "nominal x efetiva":
        rate = st.number_input("taxa nominal (%)", value=24.0, step=0.1, key="simp_nom_r")
        nom_u = st.selectbox("unidade nominal", UNITS, index=7, key="simp_nom_u")
        cap_u = st.selectbox("capitalização", UNITS, index=3, key="simp_nom_c")
        eff = effective_from_nominal(rate, nom_u, cap_u)
        annual = annual_effective_from_effective(eff, cap_u)
        st.metric("efetiva na capitalização", f"{pct(eff)} {cap_u}")
        st.metric("efetiva anual", pct(annual))
        if show_formula:
            formula_box("pela fórmula", f"efetiva na capitalização = {rate:.6f} × ({TIME_FACTORS[cap_u]:.6f}/{TIME_FACTORS[nom_u]:.6f}) = {eff:.6f}%\nefetiva anual = (1 + {eff/100:.6f})^{PER_YEAR[cap_u]:.6f} - 1 = {annual:.6f}%")
        if show_hp:
            hp_box("pela hp12c", [f"taxa efetiva na capitalização = {eff:.6f}% {cap_u}", f"taxa efetiva anual = {annual:.6f}%"])
    elif sec == "taxa real":
        mode = st.selectbox("modo", ["taxa real embutida", "taxa bruta necessária"], key="simp_real_m")
        if mode == "taxa real embutida":
            gross = st.number_input("rendimento efetivo (%)", value=10.24, step=0.1, key="simp_real_g")
            infl = st.number_input("inflação (%)", value=4.0, step=0.1, key="simp_real_i")
            real_out = rate_real_from_gross(gross, infl)
            st.metric("taxa real", pct(real_out))
            if show_formula:
                formula_box("pela fórmula", f"i_real = (1 + {gross/100:.6f})/(1 + {infl/100:.6f}) - 1 = {real_out:.6f}%")
            if show_hp:
                hp_box("pela hp12c", [f"fator bruto / fator inflação - 1 = {real_out:.6f}%"])
        else:
            real = st.number_input("taxa real desejada (%)", value=6.0, step=0.1, key="simp_real_r")
            infl = st.number_input("inflação (%)", value=4.0, step=0.1, key="simp_real_i2")
            gross_out = gross_required_for_real(real, infl)
            st.metric("taxa bruta necessária", pct(gross_out))
            if show_formula:
                formula_box("pela fórmula", f"i_bruta = (1 + {real/100:.6f})×(1 + {infl/100:.6f}) - 1 = {gross_out:.6f}%")
            if show_hp:
                hp_box("pela hp12c", [f"fator real × fator inflação - 1 = {gross_out:.6f}%"])
    elif sec == "desconto comercial simples":
        FV = st.number_input("FV", value=65000.0, step=1000.0, key="simp_dcs_fv")
        d = st.number_input("taxa (%)", value=3.0, step=0.1, key="simp_dcs_d")
        rate_u = st.selectbox("unidade da taxa", UNITS, index=3, key="simp_dcs_ru")
        t = st.number_input("tempo", value=8.0, step=1.0, key="simp_dcs_t")
        time_u = st.selectbox("unidade do tempo", UNITS, index=3, key="simp_dcs_tu")
        n = convert_time(t, time_u, rate_u)
        pv, desc = desconto_comercial_simples(FV, d, n)
        st.metric("PV", money(pv))
        st.metric("D", money(desc))
        if show_formula:
            formula_box("pela fórmula", f"PV = FV/(1+i)^n\nPV = {FV:.6f}/(1 + {i/100:.6f})^{n:.6f} = {pv:.6f}\nD = FV - PV = {desc:.6f}")
        if show_hp:
            hp_box("pela hp12c", [f"{FV:.2f} CHS FV", f"{i:.6f} i", f"{n:.6f} n", "0 PMT", "PV"])
        if show_formula:
            formula_box("pela fórmula", f"D = FV × d × n\nD = {FV:.6f} × {d/100:.6f} × {n:.6f} = {desc:.6f}\nPV = FV - D = {pv:.6f}")
        if show_hp:
            hp_box("pela hp12c", [f"{FV:.2f} CHS FV", f"{d:.6f} i", f"{n:.6f} n", "0 PMT", "PV"])
    elif sec == "desconto racional composto":
        FV = st.number_input("FV", value=1000.0, step=100.0, key="simp_drc_fv")
        i = st.number_input("taxa (%)", value=13.87, step=0.01, key="simp_drc_i")
        rate_u = st.selectbox("unidade da taxa", UNITS, index=7, key="simp_drc_ru")
        t = st.number_input("tempo", value=2.0, step=0.5, key="simp_drc_t")
        time_u = st.selectbox("unidade do tempo", UNITS, index=7, key="simp_drc_tu")
        n = convert_time(t, time_u, rate_u)
        pv, desc = desconto_racional_composto(FV, i, n)
        st.metric("PV", money(pv))
        st.metric("D", money(desc))
    elif sec == "séries uniformes":
        mode = st.selectbox("tipo", ["postecipada", "antecipada", "diferida / carência", "perpetuidade"], key="simp_su_mode")
        if mode == "perpetuidade":
            what = st.selectbox("descobrir", ["PV", "PMT"], key="simp_perp_what")
            i = st.number_input("taxa (%)", value=6.0, step=0.1, key="simp_perp_i")
            if what == "PV":
                pmt = st.number_input("PMT", value=12000.0, step=100.0, key="simp_perp_pmt")
                st.metric("PV", money(perpetuity_pv(pmt, i)))
            else:
                pv = st.number_input("PV", value=200000.0, step=1000.0, key="simp_perp_pv")
                st.metric("PMT", money(perpetuity_pmt(pv, i)))
        else:
            pv = st.number_input("PV", value=36000.0, step=1000.0, key="simp_su_pv")
            i = st.number_input("taxa (%)", value=1.8, step=0.1, key="simp_su_i")
            n = st.number_input("n", value=36, step=1, key="simp_su_n")
            car = st.number_input("carência", value=2 if mode == "diferida / carência" else 0, step=1, key="simp_su_car")
            due = "END" if mode == "postecipada" else "BEG"
            if mode == "diferida / carência":
                pv_at_start = pv * ((1 + i / 100) ** car)
                pmt = annuity_pmt(pv_at_start, i, int(n), due="END")
            else:
                pmt = annuity_pmt(pv, i, int(n), due=due)
            st.metric("PMT", money(abs(pmt)))
            if show_formula:
                formula_box("pela fórmula", f"PMT = {pmt:.6f}")
            if show_hp:
                hp_box("pela hp12c", [f"g {'END' if mode=='postecipada' else 'BEG' if mode=='antecipada' else 'END'}", f"{pv:.2f} PV", f"{i:.6f} i", f"{int(n)} n", "0 FV", "PMT"])
    elif sec == "custo efetivo do desconto":
        FV = st.number_input("FV", value=25000.0, step=1000.0, key="simp_ced_fv")
        d = st.number_input("taxa base (%)", value=2.0, step=0.1, key="simp_ced_d")
        n = st.number_input("n", value=5.0, step=0.5, key="simp_ced_n")
        saldo = st.number_input("saldo médio (%)", value=30.0, step=1.0, key="simp_ced_s")
        desp = st.number_input("despesa (%)", value=0.0, step=0.5, key="simp_ced_de")
        out = effective_discount_cost(FV, n, "desconto comercial simples", d, saldo, desp, 0.0)
        st.metric("PV líquido hoje", money(out["pv_liquido"]))
        st.metric("FV líquido no vencimento", money(out["fv_liquido"]))
        st.metric("custo efetivo por período", pct(out["i_eff_pct"]))
        if show_formula:
            formula_box("pela fórmula", f"PV líquido = {out['pv_liquido']:.6f}\nFV líquido = {out['fv_liquido']:.6f}\ni = (FV/PV)^(1/n)-1 = {out['i_eff_pct']:.6f}%")
        if show_hp:
            hp_box("pela hp12c", [f"{out['pv_liquido']:.2f} PV", f"{out['fv_liquido']:.2f} CHS FV", f"{n:.6f} n", "0 PMT", "i"])
    else:
        rate = st.number_input("taxa para VPL (%)", value=20.0, step=0.1, key="simp_fc_r")
        rows = int(st.number_input("linhas do fluxo", value=7, step=1, min_value=2, max_value=40, key="simp_fc_rows"))
        base = pd.DataFrame({"período": list(range(rows)), "fluxo": [0.0] * rows})
        if rows >= 7:
            preset = [-1200, 300, 400, 400, 500, 500, 500]
            for i, val in enumerate(preset):
                base.loc[i, "fluxo"] = val
        df = st.data_editor(base, num_rows="fixed", use_container_width=True, key="simp_fc_df")
        cfs = aggregate_cashflows(df)
        if cfs:
            st.metric("VPL", money(npv_periodic(rate, cfs)))
            tir = irr_periodic(cfs)
            st.metric("TIR", pct(tir) if tir is not None else "não encontrada")
            if show_formula:
                formula_box("pela fórmula", f"VPL calculado por soma dos fluxos descontados = {npv_periodic(rate, cfs):.6f}\nTIR = taxa que zera o VPL")
            if show_hp:
                hp_box("pela hp12c", ["f REG", "g CF0 / g CFj / g Nj", f"{rate:.6f} i", "f NPV", "f IRR"])

st.markdown('</div>', unsafe_allow_html=True)
