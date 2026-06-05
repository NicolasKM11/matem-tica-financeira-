
import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="matemática financeira v8", page_icon="💸", layout="centered")

# -----------------------------
# utilidades
# -----------------------------
TIME_FACTORS = {
    "dia corrido (360)": 1/360,
    "dia civil (365)": 1/365,
    "dia útil (252)": 1/252,
    "mês": 1/12,
    "bimestre": 1/6,
    "trimestre": 1/4,
    "semestre": 1/2,
    "ano": 1.0,
}
PER_YEAR = {
    "dia corrido (360)": 360,
    "dia civil (365)": 365,
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

def to_years(v, unit):
    return v * TIME_FACTORS[unit]

def years_to_unit(y, unit):
    return y / TIME_FACTORS[unit]

def convert_time(v, from_unit, to_unit):
    return years_to_unit(to_years(v, from_unit), to_unit)

def annual_nominal_from_simple(rate_pct, rate_unit):
    return (rate_pct / 100) * PER_YEAR[rate_unit]

def simple_proportional(rate_pct, from_unit, to_unit):
    return rate_pct * (PER_YEAR[from_unit] / PER_YEAR[to_unit])

def equivalent_rate(rate_pct, from_unit, to_unit):
    i = rate_pct / 100
    return (((1 + i) ** (PER_YEAR[to_unit] / PER_YEAR[from_unit])) - 1) * 100

def effective_from_nominal(nom_rate_pct, nominal_unit, cap_unit):
    # exemplo: 24% a.a. capitalizados mensalmente -> 24/12 = 2% a.m.
    return nom_rate_pct * (PER_YEAR[nominal_unit] / PER_YEAR[cap_unit])

def annual_effective_from_rate(rate_pct, unit):
    return ((1 + rate_pct / 100) ** PER_YEAR[unit]) - 1

def rate_real(gross_eff_pct, inflation_pct):
    return ((1 + gross_eff_pct/100) / (1 + inflation_pct/100) - 1) * 100

def gross_required_for_real(real_pct, inflation_pct):
    return (((1 + real_pct/100) * (1 + inflation_pct/100)) - 1) * 100

def solve_simple(C=None, i_pct=None, n=None, M=None):
    i = None if i_pct is None else i_pct / 100
    if C is None and None not in (i, n, M):
        C = M / (1 + i*n)
    elif i is None and None not in (C, n, M):
        i = (M/C - 1) / n
    elif n is None and None not in (C, i, M):
        n = (M/C - 1) / i
    elif M is None and None not in (C, i, n):
        M = C * (1 + i*n)
    J = None if None in (C, M) else M - C
    return C, None if i is None else i*100, n, M, J

def solve_compound(PV=None, i_pct=None, n=None, FV=None):
    i = None if i_pct is None else i_pct / 100
    if PV is None and None not in (i, n, FV):
        PV = FV / ((1+i)**n)
    elif i is None and None not in (PV, n, FV):
        i = (FV/PV)**(1/n) - 1
    elif n is None and None not in (PV, i, FV):
        n = math.log(FV/PV) / math.log(1+i)
    elif FV is None and None not in (PV, i, n):
        FV = PV * ((1+i)**n)
    J = None if None in (PV, FV) else FV - PV
    return PV, None if i is None else i*100, n, FV, J

def desconto_racional_simples(FV, i_pct, n):
    PV = FV / (1 + i_pct/100 * n)
    D = FV - PV
    return PV, D

def desconto_comercial_simples(FV, d_pct, n):
    D = FV * d_pct/100 * n
    PV = FV - D
    return PV, D

def desconto_racional_composto(FV, i_pct, n):
    PV = FV / ((1 + i_pct/100) ** n)
    D = FV - PV
    return PV, D

def desconto_comercial_composto(FV, d_pct, n):
    PV = FV * ((1 - d_pct/100) ** n)
    D = FV - PV
    return PV, D

def annuity_pmt(pv, i_pct, n, due="END", fv=0.0):
    i = i_pct/100
    if abs(i) < 1e-12:
        return -(pv + fv) / n
    factor = 1 if due == "END" else (1+i)
    return -((pv*(1+i)**n + fv) * i) / (((1+i)**n - 1) * factor)

def annuity_pv(pmt, i_pct, n, due="END", fv=0.0):
    i = i_pct/100
    if abs(i) < 1e-12:
        return -(pmt*n + fv)
    factor = 1 if due == "END" else (1+i)
    return -(((pmt*factor) * (((1+i)**n - 1)/i) + fv) / ((1+i)**n))

def annuity_fv(pmt, i_pct, n, due="END", pv=0.0):
    i = i_pct/100
    if abs(i) < 1e-12:
        return -(pv + pmt*n)
    factor = 1 if due == "END" else (1+i)
    return -pv*(1+i)**n - pmt*factor*(((1+i)**n - 1)/i)

def deferred_annuity_pmt(pv_now, i_pct, n_payments, deferral_periods, due="END"):
    i = i_pct/100
    pv_at_start = pv_now * ((1+i) ** deferral_periods)
    return annuity_pmt(pv_at_start, i_pct, n_payments, due=due, fv=0.0)

def perpetuity_pv(pmt, i_pct):
    return pmt / (i_pct/100)

def perpetuity_pmt(pv, i_pct):
    return pv * (i_pct/100)

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

def hp_box(title, lines):
    st.markdown(f"**{title}**")
    st.code("\n".join(lines))

def formula_box(text):
    st.markdown("**pela fórmula**")
    st.code(text)

# -----------------------------
# modo relógio
# -----------------------------
if "watch_mode" not in st.session_state:
    st.session_state.watch_mode = False
watch_mode = st.session_state.watch_mode

st.markdown("""
<style>
.block-container {max-width: 860px; padding-top: .45rem; padding-bottom: 2rem;}
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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="watch">' if st.session_state.watch_mode else '<div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-top">', unsafe_allow_html=True)
c1, c2 = st.columns([1.15, 1])
with c1:
    if not st.session_state.watch_mode:
        if st.button("⌚ ativar modo smartwatch", type="primary", use_container_width=True):
            st.session_state.watch_mode = True
            st.rerun()
    else:
        if st.button("💻 voltar para modo normal", type="primary", use_container_width=True):
            st.session_state.watch_mode = False
            st.rerun()
with c2:
    st.caption("modo relógio / normal")

st.title("matemática financeira aplicada — v8")
st.caption("versão mais completa, com abas separadas e blocos de fórmula e hp12c.")

with st.sidebar:
    st.subheader("configurações")
    show_formula = st.checkbox("mostrar fórmula", value=True)
    show_hp = st.checkbox("mostrar hp12c", value=True)

tabs = st.tabs([
    "início",
    "porcentagem e apoio",
    "taxas proporcionais",
    "taxas equivalentes",
    "taxa nominal x efetiva",
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

# 1
with tabs[0]:
    st.subheader("mapa do app")
    st.write("esta versão separa os cálculos por assunto:")
    st.write("- porcentagem e taxa real")
    st.write("- taxas proporcionais, equivalentes e nominal x efetiva")
    st.write("- juros simples e compostos")
    st.write("- descontos por dentro e por fora, simples e composto")
    st.write("- séries uniformes: postecipada, antecipada, diferida e perpetuidade")
    st.write("- entrada + parcelas / taxa implícita")
    st.write("- renegociação")
    st.write("- fluxo de caixa irregular: VPL/NPV e TIR/IRR")
    st.info("em questões com taxa nominal, primeiro encontre a taxa efetiva da capitalização. depois, se necessário, faça a equivalência.")

# 2
with tabs[1]:
    sub = st.radio("subaba", ["aumento/desconto", "percentuais sucessivos", "manutenção de receita", "taxa real"], horizontal=not watch_mode)
    if sub == "aumento/desconto":
        valor = st.number_input("valor inicial", min_value=0.0, value=500.0)
        taxa = st.number_input("percentual (%)", value=40.0)
        aumento = valor*(1+taxa/100)
        desconto = valor*(1-taxa/100)
        st.metric("com aumento", money(aumento))
        st.metric("com desconto", money(desconto))
        if show_formula:
            formula_box(
                f"aumento = {valor:.6f} × (1 + {taxa/100:.8f}) = {aumento:.6f}\n"
                f"desconto = {valor:.6f} × (1 - {taxa/100:.8f}) = {desconto:.6f}"
            )
    elif sub == "percentuais sucessivos":
        base = st.number_input("valor inicial", min_value=0.0, value=100.0)
        seq = st.text_input("taxas separadas por vírgula", value="-50, 100, -20, 30")
        atual = base
        steps = []
        for raw in seq.split(","):
            try:
                t = float(raw.strip())
                atual *= (1+t/100)
                steps.append(f"{t:+.4f}% → fator {(1+t/100):.6f} → {atual:.6f}")
            except:
                pass
        st.metric("valor final", money(atual))
        st.metric("variação total", pct((atual/base-1)*100 if base else 0))
        if show_formula:
            formula_box("\n".join(steps) if steps else "sem passos válidos.")
    elif sub == "manutenção de receita":
        queda = st.number_input("queda percentual da quantidade (%)", min_value=0.0, value=20.0)
        multiplicador = 100/(100-queda) if queda < 100 else float("inf")
        aumento = (multiplicador-1)*100 if queda < 100 else float("inf")
        st.metric("aumento necessário no preço", pct(aumento))
        if show_formula:
            formula_box(
                f"novo preço / preço antigo = 100 / (100 - {queda:.6f}) = {multiplicador:.6f}\n"
                f"aumento = ({multiplicador:.6f} - 1) × 100 = {aumento:.6f}%"
            )
    else:
        modo = st.radio("modo", ["achar taxa bruta necessária", "achar taxa real"], horizontal=not watch_mode)
        if modo == "achar taxa bruta necessária":
            real = st.number_input("taxa real desejada (%)", value=6.0)
            infl = st.number_input("inflação (%)", value=4.0)
            bruta = gross_required_for_real(real, infl)
            st.metric("taxa efetiva necessária", pct(bruta))
            if show_formula:
                formula_box(f"taxa bruta = (1+{real/100:.8f})(1+{infl/100:.8f}) - 1 = {bruta:.6f}%")
        else:
            gross = st.number_input("rendimento efetivo (%)", value=10.24)
            infl = st.number_input("inflação (%)", value=4.0)
            real = rate_real(gross, infl)
            st.metric("taxa real", pct(real))
            if show_formula:
                formula_box(f"taxa real = (1+{gross/100:.8f})/(1+{infl/100:.8f}) - 1 = {real:.6f}%")

# 3
with tabs[2]:
    st.subheader("taxas proporcionais")
    taxa = st.number_input("taxa de origem (%)", value=2.0)
    de = st.selectbox("de", list(PER_YEAR.keys()), index=3)
    para = st.selectbox("para", list(PER_YEAR.keys()), index=6)
    prop = simple_proportional(taxa, de, para)
    st.metric("taxa proporcional", pct(prop))
    if show_formula:
        formula_box(f"taxa destino = {taxa:.6f} × ({PER_YEAR[de]}/{PER_YEAR[para]}) = {prop:.6f}%")

# 4
with tabs[3]:
    st.subheader("taxas equivalentes")
    taxa = st.number_input("taxa efetiva de origem (%)", value=2.0, key="eq_rate")
    de = st.selectbox("de", list(PER_YEAR.keys()), index=3, key="eq_from")
    para = st.selectbox("para", list(PER_YEAR.keys()), index=6, key="eq_to")
    eq = equivalent_rate(taxa, de, para)
    st.metric("taxa equivalente", pct(eq))
    if show_formula:
        formula_box(
            f"i_destino = (1+{taxa/100:.8f})^({PER_YEAR[para]}/{PER_YEAR[de]}) - 1\n"
            f"i_destino = {eq:.6f}%"
        )
    if show_hp:
        hp_box("pela hp12c", [
            "truque usando valor base 100:",
            "100 CHS PV",
            f"{taxa:.10g} i",
            "0 PMT",
            f"{PER_YEAR[de]} n",
            "FV",
            "depois reinterpretar o montante para a unidade desejada"
        ])

# 5
with tabs[4]:
    st.subheader("taxa nominal x efetiva")
    nominal = st.number_input("taxa nominal (%)", value=12.0)
    un_taxa = st.selectbox("unidade da taxa nominal", list(PER_YEAR.keys()), index=6)
    cap = st.selectbox("capitalização", list(PER_YEAR.keys()), index=3)
    eff_cap = effective_from_nominal(nominal, un_taxa, cap)
    st.metric("taxa efetiva na unidade da capitalização", f"{pct(eff_cap)} {cap}")
    if show_formula:
        formula_box(
            f"taxa efetiva da capitalização = {nominal:.6f} × ({PER_YEAR[un_taxa]}/{PER_YEAR[cap]}) = {eff_cap:.6f}% {cap}"
        )
    if show_hp:
        hp_box("pela hp12c", [
            "converter primeiro a taxa nominal na unidade da capitalização",
            f"{nominal:.10g} × ({PER_YEAR[un_taxa]}/{PER_YEAR[cap]})",
            f"resultado = {eff_cap:.10g}% {cap}"
        ])

# 6
with tabs[5]:
    st.subheader("juros simples")
    alvo = st.selectbox("descobrir", ["M", "J", "C", "i", "n"])
    C = None if alvo == "C" else st.number_input("capital C", min_value=0.0, value=50000.0)
    taxa = None if alvo == "i" else st.number_input("taxa (%)", min_value=0.0, value=5.0)
    un_taxa = st.selectbox("unidade da taxa", list(PER_YEAR.keys()), index=3)
    tempo = None if alvo == "n" else st.number_input("tempo", min_value=0.0, value=9.0)
    un_tempo = st.selectbox("unidade do tempo", list(TIME_FACTORS.keys()), index=3)
    M = None if alvo in ["M", "J"] else st.number_input("montante M", min_value=0.0, value=72500.0)

    taxa_unificada = None if taxa is None else simple_proportional(taxa, un_taxa, un_tempo)
    C_res, i_res, n_res, M_res, J_res = solve_simple(C, taxa_unificada, tempo, M)

    if None not in (C_res, M_res):
        st.metric("capital", money(C_res))
        st.metric("montante", money(M_res))
        st.metric("juros", money(J_res))
        if show_formula:
            formula_box(
                f"J = C·i·n\n"
                f"M = C + J = C(1+i·n)\n"
                f"resultado: C={C_res:.6f}, i={i_res:.6f}%, n={n_res:.6f}, M={M_res:.6f}, J={J_res:.6f}"
            )
        if show_hp:
            hp_box("pela hp12c", [
                "f REG",
                f"{C_res:.10g} CHS PV",
                f"{i_res:.10g} i",
                f"{n_res:.10g} n",
                "FV"
            ])

# 7
with tabs[6]:
    st.subheader("juros compostos")
    alvo = st.selectbox("descobrir", ["FV", "PV", "i", "n"], key="jc_alvo")
    PV = None if alvo == "PV" else st.number_input("PV", min_value=0.0, value=1000.0)
    taxa = None if alvo == "i" else st.number_input("taxa efetiva (%)", min_value=0.0, value=20.0)
    un_taxa = st.selectbox("unidade da taxa", list(PER_YEAR.keys()), index=6, key="jc_unit")
    tempo = None if alvo == "n" else st.number_input("tempo", min_value=0.0, value=3.0)
    un_tempo = st.selectbox("unidade do tempo", list(TIME_FACTORS.keys()), index=6, key="jc_tempo")
    FV = None if alvo == "FV" else st.number_input("FV", min_value=0.0, value=1728.0)

    n_periods = None if tempo is None else convert_time(tempo, un_tempo, un_taxa)
    PV_res, i_res, n_res, FV_res, J_res = solve_compound(PV, taxa, n_periods, FV)

    if None not in (PV_res, FV_res):
        st.metric("PV", money(PV_res))
        st.metric("FV", money(FV_res))
        st.metric("juros", money(J_res))
        if show_formula:
            formula_box(
                f"FV = PV(1+i)^n ou PV = FV/(1+i)^n\n"
                f"resultado: PV={PV_res:.6f}, i={i_res:.6f}%, n={n_res:.6f}, FV={FV_res:.6f}, J={J_res:.6f}"
            )
        if show_hp:
            hp_box("pela hp12c", [
                "f REG",
                f"{PV_res:.10g} CHS PV",
                f"{i_res:.10g} i",
                f"{n_res:.10g} n",
                "FV"
            ])

# 8
with tabs[7]:
    st.subheader("desconto racional simples — por dentro")
    modo = st.selectbox("descobrir", ["PV e D", "i", "n"])
    FV = st.number_input("FV / valor nominal", min_value=0.0, value=65000.0)
    if modo == "PV e D":
        i = st.number_input("taxa i (%)", value=3.0)
        n = st.number_input("prazo n", value=8.0)
        PV, D = desconto_racional_simples(FV, i, n)
        st.metric("PV", money(PV))
        st.metric("D", money(D))
        if show_formula:
            formula_box(f"PV = FV/(1+i·n) = {PV:.6f}\nD = FV - PV = {D:.6f}")
    elif modo == "i":
        PV = st.number_input("PV", min_value=0.0, value=9600.0)
        n = st.number_input("prazo n", value=5.0)
        i = ((FV/PV)-1)/n*100
        st.metric("taxa i", pct(i))
    else:
        PV = st.number_input("PV", min_value=0.0, value=52419.35)
        i = st.number_input("taxa i (%)", value=3.0)
        n = ((FV/PV)-1)/(i/100)
        st.metric("prazo n", f"{n:.6f} períodos")

# 9
with tabs[8]:
    st.subheader("desconto comercial simples — por fora")
    modo = st.selectbox("descobrir", ["PV e D", "d", "vários títulos"], key="dcs_m")
    if modo == "PV e D":
        FV = st.number_input("FV", min_value=0.0, value=65000.0, key="dcs_fv")
        d = st.number_input("taxa d (%)", value=3.0, key="dcs_d")
        n = st.number_input("prazo n", value=8.0, key="dcs_n")
        PV, D = desconto_comercial_simples(FV, d, n)
        st.metric("D", money(D))
        st.metric("PV", money(PV))
        if show_formula:
            formula_box(f"D = FV·d·n = {D:.6f}\nPV = FV - D = {PV:.6f}")
    elif modo == "d":
        FV = st.number_input("FV", min_value=0.0, value=12000.0, key="dcs_fv2")
        PV = st.number_input("PV", min_value=0.0, value=9600.0, key="dcs_pv2")
        n = st.number_input("prazo n", value=5.0, key="dcs_n2")
        D = FV - PV
        d = D/(FV*n)*100
        st.metric("D", money(D))
        st.metric("taxa d", pct(d))
    else:
        qtd = st.number_input("quantidade de títulos", min_value=2, max_value=10, value=2)
        d = st.number_input("taxa d (%)", value=15.0, key="dcs_d3")
        total_pv, total_d = 0.0, 0.0
        for k in range(int(qtd)):
            fv = st.number_input(f"FV {k+1}", min_value=0.0, value=8000.0 if k == 0 else 12000.0, key=f"fv_t{k}")
            dias = st.number_input(f"prazo em dias {k+1}", min_value=0.0, value=43.0 if k == 0 else 58.0, key=f"n_t{k}")
            base_days = 360
            n = dias / base_days
            PV, D = desconto_comercial_simples(fv, d, n)
            total_pv += PV
            total_d += D
        st.metric("desconto total", money(total_d))
        st.metric("valor recebido total", money(total_pv))

# 10
with tabs[9]:
    st.subheader("desconto racional composto — por dentro")
    modo = st.selectbox("descobrir", ["PV e D", "i"], key="drc_m")
    FV = st.number_input("FV", min_value=0.0, value=12000.0, key="drc_fv")
    if modo == "PV e D":
        i = st.number_input("taxa i (%)", value=4.56, key="drc_i")
        n = st.number_input("prazo n", value=5.0, key="drc_n")
        PV, D = desconto_racional_composto(FV, i, n)
        st.metric("PV", money(PV))
        st.metric("D", money(D))
        if show_formula:
            formula_box(f"PV = FV/(1+i)^n = {PV:.6f}\nD = FV - PV = {D:.6f}")
    else:
        PV = st.number_input("PV", min_value=0.0, value=9600.0, key="drc_pv2")
        n = st.number_input("prazo n", value=5.0, key="drc_n2")
        i = (((FV/PV)**(1/n))-1)*100
        st.metric("taxa i", pct(i))

# 11
with tabs[10]:
    st.subheader("desconto comercial composto — por fora")
    modo = st.selectbox("descobrir", ["PV e D", "d"], key="dcc_m")
    FV = st.number_input("FV", min_value=0.0, value=65000.0, key="dcc_fv")
    if modo == "PV e D":
        d = st.number_input("taxa d (%)", value=3.0, key="dcc_d")
        n = st.number_input("prazo n", value=8.0, key="dcc_n")
        PV, D = desconto_comercial_composto(FV, d, n)
        st.metric("PV", money(PV))
        st.metric("D", money(D))
        if show_formula:
            formula_box(f"PV = FV(1-d)^n = {PV:.6f}\nD = FV - PV = {D:.6f}")
    else:
        PV = st.number_input("PV", min_value=0.0, value=50943.32, key="dcc_pv2")
        n = st.number_input("prazo n", value=8.0, key="dcc_n2")
        d = (1 - (PV/FV)**(1/n))*100
        st.metric("taxa d", pct(d))

# 12
with tabs[11]:
    st.subheader("custo efetivo no desconto")
    FV = st.number_input("valor nominal / FV", min_value=0.0, value=25000.0)
    d = st.number_input("taxa de desconto comercial simples (%)", value=2.0)
    n = st.number_input("prazo (períodos)", min_value=0.0, value=5.0)
    saldo_medio_pct = st.number_input("saldo médio retido (%)", min_value=0.0, value=30.0)
    desp_adm_pct = st.number_input("despesa administrativa (%)", min_value=0.0, value=0.0)
    D = FV*d/100*n
    pv_sem = FV - D
    i_sem = (((FV/pv_sem)**(1/n))-1)*100 if pv_sem > 0 else None
    pv_com = pv_sem - FV*saldo_medio_pct/100 - FV*desp_adm_pct/100
    fv_com = FV - FV*saldo_medio_pct/100
    i_com = (((fv_com/pv_com)**(1/n))-1)*100 if pv_com > 0 and fv_com > 0 else None
    st.metric("valor líquido sem retenções", money(pv_sem))
    st.metric("taxa implícita sem retenções", pct(i_sem) if i_sem is not None else "indefinida")
    st.metric("valor líquido com retenções", money(pv_com))
    st.metric("taxa implícita com retenções", pct(i_com) if i_com is not None else "indefinida")
    if show_formula:
        formula_box(
            f"D = FV·d·n = {D:.6f}\n"
            f"PV sem retenções = {pv_sem:.6f}\n"
            f"PV com retenções = {pv_com:.6f}\n"
            f"FV líquido de quitação = {fv_com:.6f}"
        )

# 13
with tabs[12]:
    st.subheader("séries uniformes")
    sub = st.radio("tipo", ["postecipada", "antecipada", "diferida / carência", "perpetuidade"], horizontal=not watch_mode)
    if sub in ["postecipada", "antecipada"]:
        due = "END" if sub == "postecipada" else "BEG"
        alvo = st.selectbox("descobrir", ["PMT", "PV", "FV"])
        i = st.number_input("taxa por período (%)", value=1.8, key=f"su_i_{sub}")
        n = st.number_input("número de períodos", min_value=1.0, value=36.0, key=f"su_n_{sub}")
        if alvo == "PMT":
            pv = st.number_input("PV", min_value=0.0, value=36000.0, key=f"su_pv_{sub}")
            fv = st.number_input("FV", value=0.0, key=f"su_fv_{sub}")
            pmt = annuity_pmt(pv, i, n, due=due, fv=fv)
            st.metric("PMT", money(abs(pmt)))
        elif alvo == "PV":
            pmt = st.number_input("PMT", min_value=0.0, value=15000.0 if sub == "postecipada" else 1000.0, key=f"su_pmt_{sub}")
            fv = st.number_input("FV", value=0.0, key=f"su_fv2_{sub}")
            pv = annuity_pv(-pmt, i, n, due=due, fv=fv)
            st.metric("PV", money(abs(pv)))
        else:
            pmt = st.number_input("PMT", min_value=0.0, value=1000.0, key=f"su_pmt3_{sub}")
            pv = st.number_input("PV", value=0.0, key=f"su_pv3_{sub}")
            fv = annuity_fv(-pmt, i, n, due=due, pv=pv)
            st.metric("FV", money(abs(fv)))
        if show_hp:
            hp_box("pela hp12c", [f"[g] {'END' if due=='END' else 'BEG'}", f"{i:.10g} i", f"{n:.10g} n", "usar PV/FV/PMT conforme o alvo"])
    elif sub == "diferida / carência":
        pv = st.number_input("PV hoje", min_value=0.0, value=20000.0)
        i = st.number_input("taxa por período (%)", value=3.0, key="dif_i")
        car = st.number_input("carência", min_value=0.0, value=2.0)
        n = st.number_input("número de parcelas", min_value=1.0, value=6.0)
        pmt = deferred_annuity_pmt(pv, i, n, car, due="END")
        st.metric("PMT da série diferida", money(abs(pmt)))
        if show_formula:
            formula_box(
                f"1) levar o PV até o início da série: PV_série = {pv:.6f}(1+{i/100:.8f})^{car:.6f}\n"
                f"2) calcular anuidade postecipada\nPMT = {pmt:.6f}"
            )
    else:
        modo = st.radio("modo", ["achar PV", "achar PMT"], horizontal=not watch_mode)
        i = st.number_input("taxa (%)", value=6.0, key="perp_i")
        if modo == "achar PV":
            pmt = st.number_input("PMT", min_value=0.0, value=12000.0, key="perp_p")
            pv = perpetuity_pv(pmt, i)
            st.metric("PV da perpetuidade", money(pv))
        else:
            pv = st.number_input("PV", min_value=0.0, value=200000.0, key="perp_pv")
            pmt = perpetuity_pmt(pv, i)
            st.metric("PMT da perpetuidade", money(pmt))

# 14
with tabs[13]:
    st.subheader("entrada + parcelas / taxa implícita")
    preco_prazo = st.number_input("preço a prazo", min_value=0.0, value=3000.0)
    desconto_avista_pct = st.number_input("desconto à vista (%)", min_value=0.0, value=5.0)
    entrada = st.number_input("entrada hoje", min_value=0.0, value=0.0)
    pmt = st.number_input("parcela", min_value=0.0, value=750.0)
    n = st.number_input("número de parcelas", min_value=1.0, value=4.0)
    pv_fin = preco_prazo*(1-desconto_avista_pct/100) - entrada
    lo, hi = 0.0, 5.0
    mid = 0.0
    for _ in range(120):
        mid = (lo+hi)/2
        v = annuity_pv(-pmt, mid*100, n, due="END", fv=0.0)
        if v > pv_fin:
            lo = mid
        else:
            hi = mid
    taxa_impl = mid*100
    st.metric("PV financiado", money(pv_fin))
    st.metric("taxa implícita por período", pct(taxa_impl))

# 15
with tabs[14]:
    st.subheader("renegociação")
    pmt_antiga = st.number_input("prestação antiga", min_value=0.0, value=4727.98)
    restam = st.number_input("parcelas restantes", min_value=1.0, value=6.0)
    i = st.number_input("taxa (%)", value=2.0)
    novas = st.number_input("quantidade de novas parcelas", min_value=1.0, value=18.0)
    saldo = annuity_pv(-pmt_antiga, i, restam, due="END", fv=0.0)
    nova = annuity_pmt(abs(saldo), i, novas, due="END", fv=0.0)
    st.metric("saldo devedor", money(abs(saldo)))
    st.metric("nova prestação", money(abs(nova)))
    if show_hp:
        hp_box("pela hp12c", [
            "[g] END",
            f"{pmt_antiga:.10g} CHS PMT",
            f"{restam:.10g} n",
            f"{i:.10g} i",
            "0 FV",
            "PV",
            "",
            "[g] END",
            f"{abs(saldo):.10g} PV",
            f"{novas:.10g} n",
            f"{i:.10g} i",
            "0 FV",
            "PMT"
        ])

# 16
with tabs[15]:
    st.subheader("fluxo de caixa irregular — VPL / TIR / CF0, CFj, Nj")
    st.caption("você pode adicionar linhas novas. linhas vazias ou incompletas são ignoradas.")

    default = pd.DataFrame({
        "período": [0, 1, 2, 3, 4, 5, 6],
        "fluxo": [-1200, 300, 400, 400, 500, 500, 500]
    })

    df = st.data_editor(
        default,
        num_rows="dynamic",
        use_container_width=True,
        key="fc_editor"
    )

    taxa = st.number_input("taxa para VPL (%)", value=20.0)

    if len(df) > 0:
        df2 = df.copy()

        # remove linhas totalmente vazias
        df2 = df2.dropna(how="all")

        # remove linhas com campos vazios
        if "período" in df2.columns and "fluxo" in df2.columns:
            df2 = df2.dropna(subset=["período", "fluxo"])

            # converte com segurança
            df2["período"] = pd.to_numeric(df2["período"], errors="coerce")
            df2["fluxo"] = pd.to_numeric(df2["fluxo"], errors="coerce")

            # remove inválidos
            df2 = df2.dropna(subset=["período", "fluxo"])

            # força período inteiro e não negativo
            df2["período"] = df2["período"].astype(int)
            df2 = df2[df2["período"] >= 0]

            if len(df2) == 0:
                st.warning("preencha pelo menos um período e um fluxo válidos.")
            else:
                df2 = df2.sort_values("período").reset_index(drop=True)

                maxp = int(df2["período"].max())
                cfs = [0.0] * (maxp + 1)

                for _, row in df2.iterrows():
                    cfs[int(row["período"])] += float(row["fluxo"])

                v = npv(taxa, cfs)
                r = irr(cfs)

                st.metric("VPL / NPV", money(v))
                st.metric("TIR / IRR", pct(r) if r is not None else "não encontrada")

                with st.expander("ver fluxos consolidados"):
                    st.dataframe(pd.DataFrame({
                        "período": list(range(len(cfs))),
                        "fluxo consolidado": cfs
                    }), use_container_width=True)

                if show_hp:
                    hp_box("pela hp12c", [
                        "f REG",
                        "g CF0 para o fluxo do período 0",
                        "g CFj para cada fluxo",
                        "g Nj para repetições",
                        f"{taxa:.10g} i",
                        "f NPV",
                        "f IRR"
                    ])

# 17
with tabs[16]:
    st.subheader("comparador de alternativas")
    tipo = st.radio("comparar", ["financiamentos", "investimentos"], horizontal=not watch_mode)
    if tipo == "financiamentos":
        taxaA = st.number_input("banco A (% nominal)", value=35.0)
        capA = st.selectbox("capitalização A", list(PER_YEAR.keys()), index=6)
        taxaB = st.number_input("banco B (% nominal)", value=32.0)
        capB = st.selectbox("capitalização B", list(PER_YEAR.keys()), index=3)
        effA = annual_effective_from_rate(effective_from_nominal(taxaA, "ano", capA), capA)*100
        effB = annual_effective_from_rate(effective_from_nominal(taxaB, "ano", capB), capB)*100
        melhor = "Banco A" if effA < effB else "Banco B"
        st.metric("taxa efetiva anual A", pct(effA))
        st.metric("taxa efetiva anual B", pct(effB))
        st.success(f"melhor para financiar: {melhor}")
    else:
        taxaA = st.number_input("investimento A (% nominal)", value=23.0, key="ca1")
        capA = st.selectbox("capitalização A", list(PER_YEAR.keys()), index=6, key="ca2")
        taxaB = st.number_input("investimento B (% nominal)", value=20.0, key="cb1")
        capB = st.selectbox("capitalização B", list(PER_YEAR.keys()), index=3, key="cb2")
        effA = annual_effective_from_rate(effective_from_nominal(taxaA, "ano", capA), capA)*100
        effB = annual_effective_from_rate(effective_from_nominal(taxaB, "ano", capB), capB)*100
        melhor = "Banco A" if effA > effB else "Banco B"
        st.metric("taxa efetiva anual A", pct(effA))
        st.metric("taxa efetiva anual B", pct(effB))
        st.success(f"melhor para investir: {melhor}")


with tabs[17]:
    st.subheader("página simples")
    st.caption("atalho com só os tipos de exercício que você mais usa.")
    modo = st.radio(
        "tipo de exercício",
        [
            "taxa proporcional",
            "taxa equivalente",
            "taxa nominal → efetiva",
            "taxa real",
            "desconto comercial simples (por fora)",
            "desconto racional composto (por dentro)",
            "série uniforme",
            "fluxo de caixa irregular (VPL / TIR)",
        ],
        horizontal=not watch_mode
    )

    if modo == "taxa proporcional":
        taxa = st.number_input("taxa de origem (%)", value=2.0, key="sim_prop1")
        de = st.selectbox("de", list(PER_YEAR.keys()), index=3, key="sim_prop2")
        para = st.selectbox("para", list(PER_YEAR.keys()), index=6, key="sim_prop3")
        prop = simple_proportional(taxa, de, para)
        st.metric("taxa proporcional", f"{pct(prop)} {para}")
        if show_formula:
            formula_box(f"taxa destino = {taxa:.6f} × ({PER_YEAR[de]}/{PER_YEAR[para]}) = {prop:.6f}% {para}")

    elif modo == "taxa equivalente":
        taxa = st.number_input("taxa efetiva de origem (%)", value=2.0, key="sim_eq1")
        de = st.selectbox("de", list(PER_YEAR.keys()), index=3, key="sim_eq2")
        para = st.selectbox("para", list(PER_YEAR.keys()), index=6, key="sim_eq3")
        taxa_equiv = equivalent_rate(taxa, de, para)
        st.metric("taxa equivalente", f"{pct(taxa_equiv)} {para}")
        if show_formula:
            formula_box(
                f"taxa equivalente = (1+{taxa/100:.8f})^({PER_YEAR[para]}/{PER_YEAR[de]}) - 1 = {taxa_equiv:.6f}% {para}"
            )
        if show_hp:
            hp_box("pela hp12c", [
                f"1 + {taxa/100:.10g}",
                f"ENTER {PER_YEAR[para]/PER_YEAR[de]:.10g}",
                "y^x",
                "1 -"
            ])

    elif modo == "taxa nominal → efetiva":
        taxa_nom = st.number_input("taxa nominal (%)", value=24.0, key="sim_nom1")
        un_nom = st.selectbox("unidade da taxa nominal", list(PER_YEAR.keys()), index=6, key="sim_nom2")
        cap = st.selectbox("capitalização", list(PER_YEAR.keys()), index=3, key="sim_nom3")
        taxa_eff_cap = effective_from_nominal(taxa_nom, un_nom, cap)
        st.metric("taxa efetiva na unidade da capitalização", f"{pct(taxa_eff_cap)} {cap}")
        if show_formula:
            formula_box(
                f"taxa efetiva da capitalização = {taxa_nom:.6f} × ({PER_YEAR[un_nom]}/{PER_YEAR[cap]}) = {taxa_eff_cap:.6f}% {cap}"
            )
        if show_hp:
            hp_box("pela hp12c", [
                f"{taxa_nom:.10g} × ({PER_YEAR[un_nom]}/{PER_YEAR[cap]})",
                f"resultado = {taxa_eff_cap:.10g}% {cap}"
            ])

    elif modo == "taxa real":
        sub = st.radio("o que descobrir", ["taxa bruta necessária", "taxa real embutida"], horizontal=not watch_mode, key="sim_real_sub")
        if sub == "taxa bruta necessária":
            real = st.number_input("taxa real desejada (%)", value=6.0, key="sim_real_1")
            infl = st.number_input("inflação (%)", value=4.0, key="sim_real_2")
            bruta = gross_required_for_real(real, infl)
            st.metric("rentabilidade efetiva necessária", pct(bruta))
            if show_formula:
                formula_box(f"(1+real)(1+inflação)-1 = (1+{real/100:.8f})(1+{infl/100:.8f})-1 = {bruta:.6f}%")
        else:
            bruto = st.number_input("rendimento efetivo (%)", value=10.24, key="sim_real_3")
            infl = st.number_input("inflação (%)", value=4.0, key="sim_real_4")
            real = rate_real(bruto, infl)
            st.metric("taxa real", pct(real))
            if show_formula:
                formula_box(f"(1+efetiva)/(1+inflação)-1 = (1+{bruto/100:.8f})/(1+{infl/100:.8f})-1 = {real:.6f}%")

    elif modo == "desconto comercial simples (por fora)":
        alvo = st.radio("descobrir", ["valor recebido e desconto", "taxa mensal de desconto"], horizontal=not watch_mode, key="sim_dcs_sub")
        if alvo == "valor recebido e desconto":
            FV = st.number_input("valor nominal / FV", min_value=0.0, value=65000.0, key="sim_dcs_1")
            d = st.number_input("taxa de desconto (%)", min_value=0.0, value=3.0, key="sim_dcs_2")
            n = st.number_input("prazo n", min_value=0.0, value=8.0, key="sim_dcs_3")
            PV, D = desconto_comercial_simples(FV, d, n)
            st.metric("desconto D", money(D))
            st.metric("valor antecipado / recebido", money(PV))
            if show_formula:
                formula_box(f"D = FV·d·n = {FV:.6f}×{d/100:.8f}×{n:.6f} = {D:.6f}\nPV = FV-D = {PV:.6f}")
        else:
            FV = st.number_input("valor nominal / FV", min_value=0.0, value=12000.0, key="sim_dcs_4")
            PV = st.number_input("valor antecipado / PV", min_value=0.0, value=9600.0, key="sim_dcs_5")
            n = st.number_input("prazo n", min_value=0.0, value=5.0, key="sim_dcs_6")
            D = FV - PV
            d = D/(FV*n)*100
            st.metric("desconto D", money(D))
            st.metric("taxa d", pct(d))

    elif modo == "desconto racional composto (por dentro)":
        FV = st.number_input("valor futuro / FV", min_value=0.0, value=1000.0, key="sim_drc_1")
        i = st.number_input("taxa efetiva (%)", min_value=0.0, value=13.87, key="sim_drc_2")
        n = st.number_input("prazo n", min_value=0.0, value=2.0, key="sim_drc_3")
        PV, D = desconto_racional_composto(FV, i, n)
        st.metric("valor presente / preço do título", money(PV))
        st.metric("desconto D", money(D))
        if show_formula:
            formula_box(f"PV = FV/(1+i)^n = {FV:.6f}/(1+{i/100:.8f})^{n:.6f} = {PV:.6f}\nD = FV-PV = {D:.6f}")

    elif modo == "série uniforme":
        subtipo = st.radio("subtipo", ["postecipada", "antecipada"], horizontal=not watch_mode, key="sim_su_sub")
        alvo = st.radio("descobrir", ["PMT", "PV", "FV"], horizontal=not watch_mode, key="sim_su_sub2")
        due = "END" if subtipo == "postecipada" else "BEG"
        i = st.number_input("taxa por período (%)", min_value=0.0, value=1.8 if subtipo=="postecipada" else 1.0, key="sim_su_1")
        n = st.number_input("número de períodos", min_value=1.0, value=36.0 if subtipo=="postecipada" else 360.0, key="sim_su_2")

        if alvo == "PMT":
            pv = st.number_input("PV", min_value=0.0, value=36000.0, key="sim_su_3")
            fv = st.number_input("FV", value=0.0, key="sim_su_4")
            pmt = annuity_pmt(pv, i, n, due=due, fv=fv)
            st.metric("PMT", money(abs(pmt)))
        elif alvo == "PV":
            pmt = st.number_input("PMT", min_value=0.0, value=15000.0, key="sim_su_5")
            fv = st.number_input("FV", value=0.0, key="sim_su_6")
            pv = annuity_pv(-pmt, i, n, due=due, fv=fv)
            st.metric("PV", money(abs(pv)))
        else:
            pmt = st.number_input("PMT", min_value=0.0, value=1000.0, key="sim_su_7")
            pv = st.number_input("PV", value=0.0, key="sim_su_8")
            fv = annuity_fv(-pmt, i, n, due=due, pv=pv)
            st.metric("FV", money(abs(fv)))

        if show_hp:
            hp_box("pela hp12c", [
                f"[g] {'END' if due=='END' else 'BEGIN'}",
                "preencher PV, FV, i, n e PMT conforme o alvo"
            ])

    else:
        st.markdown("**digite só os fluxos usados. linhas vazias são ignoradas.**")
        df_simple = st.data_editor(
            pd.DataFrame({"período":[0,1,2,3,4,5,6], "fluxo":[-1200,300,400,400,500,500,500]}),
            num_rows="dynamic",
            use_container_width=True,
            key="fc_editor_simple"
        )
        taxa = st.number_input("taxa para VPL (%)", value=20.0, key="sim_fc_taxa")

        if len(df_simple) > 0:
            df2 = df_simple.copy()
            df2 = df2.dropna(how="all")
            df2 = df2.dropna(subset=["período", "fluxo"])
            df2["período"] = pd.to_numeric(df2["período"], errors="coerce")
            df2["fluxo"] = pd.to_numeric(df2["fluxo"], errors="coerce")
            df2 = df2.dropna(subset=["período", "fluxo"])
            df2["período"] = df2["período"].astype(int)
            df2 = df2[df2["período"] >= 0]

            if len(df2) == 0:
                st.warning("preencha pelo menos um período e um fluxo válidos.")
            else:
                df2 = df2.groupby("período", as_index=False)["fluxo"].sum().sort_values("período")
                maxp = int(df2["período"].max())
                cfs = [0.0]*(maxp+1)
                for _, row in df2.iterrows():
                    cfs[int(row["período"])] = float(row["fluxo"])

                v = npv(taxa, cfs)
                r = irr(cfs)
                st.metric("VPL / NPV", money(v))
                st.metric("TIR / IRR", pct(r) if r is not None else "não encontrada")

                st.dataframe(df2, use_container_width=True, hide_index=True)
                if show_hp:
                    hp_box("pela hp12c", [
                        "f REG",
                        "g CF0",
                        "g CFj",
                        "g Nj",
                        f"{taxa:.10g} i",
                        "f NPV",
                        "f IRR"
                    ])


st.markdown("</div>", unsafe_allow_html=True)

