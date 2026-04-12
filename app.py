
import math
import streamlit as st

st.set_page_config(page_title="matemática financeira v7", page_icon="⌚", layout="centered")

TIME_UNITS = {
    "dias corridos (360)": {"years_factor": 1/360},
    "dias úteis (252)": {"years_factor": 1/252},
    "meses": {"years_factor": 1/12},
    "bimestres": {"years_factor": 1/6},
    "trimestres": {"years_factor": 1/4},
    "semestres": {"years_factor": 1/2},
    "anos": {"years_factor": 1.0},
}

RATE_UNITS = {
    "ao dia corrido (360)": 360,
    "ao dia útil (252)": 252,
    "ao mês": 12,
    "ao bimestre": 6,
    "ao trimestre": 4,
    "ao semestre": 2,
    "ao ano": 1,
}

RATE_TO_TIME = {
    "ao dia corrido (360)": "dias corridos (360)",
    "ao dia útil (252)": "dias úteis (252)",
    "ao mês": "meses",
    "ao bimestre": "bimestres",
    "ao trimestre": "trimestres",
    "ao semestre": "semestres",
    "ao ano": "anos",
}

SECTIONS = [
    "percentuais",
    "conversão de tempo",
    "taxas proporcionais",
    "taxas equivalentes",
    "juros simples",
    "juros compostos",
    "capitalização diferente",
    "valor presente / futuro",
    "capitalização mista",
]

def money(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(v: float, digs: int = 6) -> str:
    return f"{v:.{digs}f}%".replace(".", ",")

def to_years(value: float, unit_label: str) -> float:
    return value * TIME_UNITS[unit_label]["years_factor"]

def years_to_time(years: float, unit_label: str) -> float:
    return years / TIME_UNITS[unit_label]["years_factor"]

def convert_time(value: float, from_unit: str, to_unit: str) -> float:
    return years_to_time(to_years(value, from_unit), to_unit)

def annual_nominal_from_simple(rate_pct: float, rate_unit: str) -> float:
    return (rate_pct / 100) * RATE_UNITS[rate_unit]

def simple_proportional(rate_pct: float, from_unit: str, to_unit: str) -> float:
    annual_nom = annual_nominal_from_simple(rate_pct, from_unit)
    return (annual_nom / RATE_UNITS[to_unit]) * 100

def compound_effective_to_effective(rate_pct: float, from_unit: str, to_unit: str) -> float:
    i_from = rate_pct / 100
    annual_eff = (1 + i_from) ** RATE_UNITS[from_unit] - 1
    i_to = (1 + annual_eff) ** (1 / RATE_UNITS[to_unit]) - 1
    return i_to * 100

def solve_simple(C=None, i=None, t=None, M=None):
    if C is None and None not in (i, t, M):
        C = M / (1 + i * t)
    elif i is None and None not in (C, t, M):
        i = (M / C - 1) / t
    elif t is None and None not in (C, i, M):
        t = (M / C - 1) / i
    elif M is None and None not in (C, i, t):
        M = C * (1 + i * t)
    J = None if None in (C, M) else M - C
    return C, i, t, M, J

def solve_compound(C=None, i=None, t=None, M=None):
    if C is None and None not in (i, t, M):
        C = M / ((1 + i) ** t)
    elif i is None and None not in (C, t, M):
        i = (M / C) ** (1 / t) - 1
    elif t is None and None not in (C, i, M):
        t = math.log(M / C) / math.log(1 + i)
    elif M is None and None not in (C, i, t):
        M = C * ((1 + i) ** t)
    J = None if None in (C, M) else M - C
    return C, i, t, M, J

def mixed_capitalization(C: float, i_per_period: float, n_periods: float) -> float:
    n_int = math.floor(n_periods)
    frac = n_periods - n_int
    return C * ((1 + i_per_period) ** n_int) * (1 + i_per_period * frac)

def rate_to_effective_annual(rate_pct: float, unit_label: str) -> float:
    return (1 + rate_pct / 100) ** RATE_UNITS[unit_label] - 1

def annual_eff_to_rate(annual_eff: float, unit_label: str) -> float:
    return ((1 + annual_eff) ** (1 / RATE_UNITS[unit_label]) - 1) * 100

def show_formula_block(text: str):
    st.markdown("**pela fórmula**")
    st.code(text)

def show_hp_block(text: str):
    st.markdown("**pela hp12c**")
    st.code(text)

def hp_simple_for_MJ(C, taxa_pct_unidade, i_unit, tempo_unidade, t_unit, M, J):
    return "\n".join([
        "f REG",
        f"{C:.10g} CHS PV",
        f"{taxa_pct_unidade:.10g} i",
        f"{tempo_unidade:.10g} n",
        "FV",
        f"FV = {M:.10g}",
        f"J = FV - PV = {J:.10g}",
        f"obs.: taxa em {i_unit} e prazo em {t_unit}"
    ])

def hp_simple_for_C(M, taxa_pct_unidade, tempo_unidade, C):
    return "\n".join([
        "f REG",
        f"{M:.10g} FV",
        f"{taxa_pct_unidade:.10g} i",
        f"{tempo_unidade:.10g} n",
        "PV",
        f"PV = {-C:.10g}",
        f"capital = {C:.10g}"
    ])

def hp_simple_for_i(C, M, tempo_unidade, i_pct):
    return "\n".join([
        "f REG",
        f"{C:.10g} CHS PV",
        f"{M:.10g} FV",
        f"{tempo_unidade:.10g} n",
        "i",
        f"i = {i_pct:.10g}%"
    ])

def hp_simple_for_t(C, M, taxa_pct_unidade, t):
    return "\n".join([
        "f REG",
        f"{C:.10g} CHS PV",
        f"{M:.10g} FV",
        f"{taxa_pct_unidade:.10g} i",
        "n",
        f"n = {t:.10g}"
    ])

def hp_compound_for_MJ(C, taxa_pct_unidade, tempo_unidade, t_unit, M, J):
    return "\n".join([
        "f REG",
        f"{C:.10g} CHS PV",
        f"{taxa_pct_unidade:.10g} i",
        f"{tempo_unidade:.10g} n",
        "FV",
        f"FV = {M:.10g}",
        f"J = FV - PV = {J:.10g}",
        f"obs.: prazo em {t_unit}"
    ])

def hp_compound_for_C(M, taxa_pct_unidade, tempo_unidade, C):
    return "\n".join([
        "f REG",
        f"{M:.10g} FV",
        f"{taxa_pct_unidade:.10g} i",
        f"{tempo_unidade:.10g} n",
        "PV",
        f"PV = {-C:.10g}",
        f"capital = {C:.10g}"
    ])

def hp_compound_for_i(C, M, tempo_unidade, i_pct):
    return "\n".join([
        "f REG",
        f"{C:.10g} CHS PV",
        f"{M:.10g} FV",
        f"{tempo_unidade:.10g} n",
        "i",
        f"i = {i_pct:.10g}%"
    ])

def hp_compound_for_t(C, M, taxa_pct_unidade, t):
    return "\n".join([
        "f REG",
        f"{C:.10g} CHS PV",
        f"{M:.10g} FV",
        f"{taxa_pct_unidade:.10g} i",
        "n",
        f"n = {t:.10g}"
    ])

st.markdown("""
<style>
.block-container {padding-top: .55rem; padding-bottom: 2rem; max-width: 680px;}
div[data-testid="stMetric"] {background: rgba(255,255,255,0.03); padding: .55rem .7rem; border-radius: 12px;}
.sticky-top {
    position: sticky; top: 0; z-index: 999;
    background: rgba(14,17,23,0.96);
    backdrop-filter: blur(8px);
    padding: .35rem 0 .65rem 0;
    margin-bottom: .6rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.big-note {
    font-size: 0.95rem; font-weight: 700; text-align: center;
    padding: .35rem .5rem; border-radius: 14px;
    background: rgba(255,255,255,0.04); margin-bottom: .4rem;
}
.watch-mode h1 {font-size: 1.45rem !important;}
.watch-mode h2, .watch-mode h3 {font-size: 1.05rem !important;}
.watch-mode p, .watch-mode label, .watch-mode .stCaption, .watch-mode div[data-testid="stMarkdownContainer"] p {
    font-size: 0.82rem !important;
}
.watch-mode div[data-testid="stMetricValue"] {font-size: 1.05rem !important;}
.watch-mode div[data-testid="stMetricLabel"] {font-size: 0.72rem !important;}
.watch-mode input, .watch-mode select, .watch-mode textarea {font-size: 0.82rem !important;}
.watch-mode button[kind], .watch-mode .stButton button {
    font-size: 0.82rem !important;
    padding-top: 0.35rem !important; padding-bottom: 0.35rem !important;
}
.watch-mode pre, .watch-mode code {font-size: 0.72rem !important; line-height: 1.2 !important;}
</style>
""", unsafe_allow_html=True)

if "watch_mode" not in st.session_state:
    st.session_state.watch_mode = False

st.markdown('<div class="watch-mode">' if st.session_state.watch_mode else '<div>', unsafe_allow_html=True)

st.markdown('<div class="sticky-top">', unsafe_allow_html=True)
st.markdown(
    '<div class="big-note">⌚ modo smartwatch ligado</div>' if st.session_state.watch_mode else '<div class="big-note">💻 modo normal</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns([1.2, 1])
with col1:
    if not st.session_state.watch_mode:
        if st.button("⌚ ativar modo smartwatch", use_container_width=True, type="primary"):
            st.session_state.watch_mode = True
            st.rerun()
    else:
        if st.button("💻 voltar para modo normal", use_container_width=True, type="primary"):
            st.session_state.watch_mode = False
            st.rerun()
with col2:
    st.caption("botão fixo no topo")
st.markdown('</div>', unsafe_allow_html=True)

watch_mode = st.session_state.watch_mode

st.title("matemática financeira")
st.caption("modo compacto para relógio" if watch_mode else "modo normal")

def render_percentuais():
    st.subheader("percentuais")
    base = st.number_input("valor inicial", min_value=0.0, value=500.0, step=100.0, key="p_base")
    taxa = st.number_input("percentual (%)", value=40.0, step=0.1, key="p_taxa")
    valor_pct = base * taxa / 100
    aumento = base * (1 + taxa / 100)
    desconto = base * (1 - taxa / 100)
    st.metric("x% do valor", money(valor_pct))
    st.metric("com aumento", money(aumento))
    st.metric("com desconto", money(desconto))
    show_formula_block(
        f"{taxa:.6f}% de {base:.6f} = {base:.6f} × {taxa/100:.6f} = {valor_pct:.6f}\n"
        f"aumento = {base:.6f} × (1 + {taxa/100:.6f}) = {aumento:.6f}\n"
        f"desconto = {base:.6f} × (1 - {taxa/100:.6f}) = {desconto:.6f}"
    )

def render_conversao():
    st.subheader("conversão de tempo")
    t_val = st.number_input("tempo", min_value=0.0, value=15.0, step=1.0, key="c_val")
    t_from = st.selectbox("de", list(TIME_UNITS.keys()), index=0, key="c_from")
    t_to = st.selectbox("para", list(TIME_UNITS.keys()), index=2, key="c_to")
    conv = convert_time(t_val, t_from, t_to)
    st.success(f"{t_val} {t_from} = {conv:.6f} {t_to}")
    show_formula_block(
        f"converter para anos:\n"
        f"{t_val:.6f} {t_from} = {to_years(t_val, t_from):.8f} anos\n\n"
        f"converter para destino:\n"
        f"{to_years(t_val, t_from):.8f} anos = {conv:.6f} {t_to}"
    )

def render_prop():
    st.subheader("taxas proporcionais")
    r = st.number_input("taxa (%)", value=2.0, step=0.1, key="tp_r")
    r_from = st.selectbox("unidade atual", list(RATE_UNITS.keys()), index=3, key="tp_from")
    r_to = st.selectbox("unidade desejada", list(RATE_UNITS.keys()), index=5, key="tp_to")
    prop = simple_proportional(r, r_from, r_to)
    st.metric("taxa proporcional", f"{pct(prop,4)} {r_to}")
    show_formula_block(
        f"taxa proporcional = taxa × (períodos destino / períodos origem)\n"
        f"resultado = {r:.6f}% de {r_from} para {r_to}\n"
        f"resultado = {prop:.6f}%"
    )

def render_equiv():
    st.subheader("taxas equivalentes")
    r_eq = st.number_input("taxa base (%)", value=20.0, step=0.1, key="te_r")
    eq_from = st.selectbox("unidade base", list(RATE_UNITS.keys()), index=2, key="te_from")
    eq_to = st.selectbox("unidade equivalente", list(RATE_UNITS.keys()), index=3, key="te_to")
    eq = compound_effective_to_effective(r_eq, eq_from, eq_to)
    st.metric("taxa equivalente", f"{pct(eq,6)} {eq_to}")
    show_formula_block(
        f"1) taxa anual efetiva = (1 + {r_eq/100:.8f})^{RATE_UNITS[eq_from]} - 1\n"
        f"2) taxa equivalente = (1 + taxa_anual)^(1/{RATE_UNITS[eq_to]}) - 1\n"
        f"resultado = {eq:.8f}%"
    )

def render_js():
    st.subheader("juros simples")
    alvo = st.selectbox("descobrir", ["montante (M)", "juros (J)", "capital (C)", "taxa (i)", "tempo (t)"], key="js_alvo")
    mostrar_hp = st.toggle("mostrar hp12c", value=True, key="js_hp")
    C = None if alvo == "capital (C)" else st.number_input("capital (C)", min_value=0.0, value=50000.0, step=100.0, key="js_C")
    M = None if alvo in ["montante (M)", "juros (J)"] else st.number_input("montante (M)", min_value=0.0, value=72500.0, step=100.0, key="js_M")
    i_in = None if alvo == "taxa (i)" else st.number_input("taxa (%)", min_value=0.0, value=5.0, step=0.1, key="js_i")
    i_unit = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=2, key="js_i_unit")
    t_in = None if alvo == "tempo (t)" else st.number_input("tempo", min_value=0.0, value=9.0, step=1.0, key="js_t")
    t_unit = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=2, key="js_t_unit")

    i_annual = None if i_in is None else annual_nominal_from_simple(i_in, i_unit)
    t_years = None if t_in is None else to_years(t_in, t_unit)
    C_res, i_res, t_res, M_res, J_res = solve_simple(C, i_annual, t_years, M)

    if None not in (C_res, i_res, t_res, M_res, J_res):
        taxa_unidade = (i_res / RATE_UNITS[i_unit]) * 100
        tempo_unidade = years_to_time(t_res, t_unit)
        st.metric("capital", money(C_res))
        st.metric("montante", money(M_res))
        st.metric("juros", money(J_res))

        if alvo == "montante (M)":
            formula = (
                f"1) converter o prazo:\n"
                f"{t_in:.6f} {t_unit} = {tempo_unidade:.6f} {t_unit}\n\n"
                f"2) M = C(1 + i·t)\n"
                f"M = {C_res:.6f}(1 + {taxa_unidade/100:.8f} × {tempo_unidade:.6f})\n"
                f"M = {M_res:.6f}\n"
                f"J = M - C = {J_res:.6f}"
            )
            hp = hp_simple_for_MJ(C_res, taxa_unidade, i_unit, tempo_unidade, t_unit, M_res, J_res)
        elif alvo == "juros (J)":
            formula = (
                f"1) J = C·i·t\n"
                f"J = {C_res:.6f} × {taxa_unidade/100:.8f} × {tempo_unidade:.6f}\n"
                f"J = {J_res:.6f}\n\n"
                f"2) M = C + J = {M_res:.6f}"
            )
            hp = hp_simple_for_MJ(C_res, taxa_unidade, i_unit, tempo_unidade, t_unit, M_res, J_res)
        elif alvo == "capital (C)":
            formula = (
                f"C = M / (1 + i·t)\n"
                f"C = {M_res:.6f} / (1 + {taxa_unidade/100:.8f} × {tempo_unidade:.6f})\n"
                f"C = {C_res:.6f}"
            )
            hp = hp_simple_for_C(M_res, taxa_unidade, tempo_unidade, C_res)
        elif alvo == "taxa (i)":
            formula = (
                f"i = (M/C - 1) / t\n"
                f"i = ({M_res:.6f}/{C_res:.6f} - 1) / {tempo_unidade:.6f}\n"
                f"i = {taxa_unidade/100:.8f}\n"
                f"i = {taxa_unidade:.6f}% {i_unit}"
            )
            hp = hp_simple_for_i(C_res, M_res, tempo_unidade, taxa_unidade)
        else:
            formula = (
                f"t = (M/C - 1) / i\n"
                f"t = ({M_res:.6f}/{C_res:.6f} - 1) / {taxa_unidade/100:.8f}\n"
                f"t = {tempo_unidade:.6f} {t_unit}"
            )
            hp = hp_simple_for_t(C_res, M_res, taxa_unidade, tempo_unidade)

        show_formula_block(formula)
        if mostrar_hp:
            show_hp_block(hp)

def render_jc():
    st.subheader("juros compostos")
    alvo = st.selectbox("descobrir", ["montante (M)", "juros (J)", "capital (C)", "taxa (i)", "tempo (t)"], key="jc_alvo")
    mostrar_hp = st.toggle("mostrar hp12c", value=True, key="jc_hp")
    C = None if alvo == "capital (C)" else st.number_input("capital (C)", min_value=0.0, value=1000.0, step=100.0, key="jc_C")
    M = None if alvo in ["montante (M)", "juros (J)"] else st.number_input("montante (M)", min_value=0.0, value=1728.0, step=100.0, key="jc_M")
    i_in = None if alvo == "taxa (i)" else st.number_input("taxa (%)", min_value=0.0, value=20.0, step=0.1, key="jc_i")
    i_unit = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=6, key="jc_i_unit")
    t_in = None if alvo == "tempo (t)" else st.number_input("tempo", min_value=0.0, value=3.0, step=0.5, key="jc_t")
    t_unit = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=6, key="jc_t_unit")

    i_annual_eff = None if i_in is None else rate_to_effective_annual(i_in, i_unit)
    t_years = None if t_in is None else to_years(t_in, t_unit)
    C_res, i_res, t_res, M_res, J_res = solve_compound(C, i_annual_eff, t_years, M)

    if None not in (C_res, i_res, t_res, M_res, J_res):
        taxa_unidade = annual_eff_to_rate(i_res, i_unit)
        tempo_unidade = years_to_time(t_res, t_unit)
        st.metric("capital", money(C_res))
        st.metric("montante", money(M_res))
        st.metric("juros", money(J_res))

        if alvo == "montante (M)":
            formula = (
                f"M = C(1+i)^t\n"
                f"M = {C_res:.6f}(1 + {taxa_unidade/100:.8f})^{tempo_unidade:.6f}\n"
                f"M = {M_res:.6f}\n"
                f"J = M - C = {J_res:.6f}"
            )
            hp = hp_compound_for_MJ(C_res, taxa_unidade, tempo_unidade, t_unit, M_res, J_res)
        elif alvo == "juros (J)":
            formula = (
                f"M = C(1+i)^t\n"
                f"M = {C_res:.6f}(1 + {taxa_unidade/100:.8f})^{tempo_unidade:.6f}\n"
                f"M = {M_res:.6f}\n"
                f"J = M - C = {J_res:.6f}"
            )
            hp = hp_compound_for_MJ(C_res, taxa_unidade, tempo_unidade, t_unit, M_res, J_res)
        elif alvo == "capital (C)":
            formula = (
                f"C = M / (1+i)^t\n"
                f"C = {M_res:.6f} / (1 + {taxa_unidade/100:.8f})^{tempo_unidade:.6f}\n"
                f"C = {C_res:.6f}"
            )
            hp = hp_compound_for_C(M_res, taxa_unidade, tempo_unidade, C_res)
        elif alvo == "taxa (i)":
            formula = (
                f"i = (M/C)^(1/t) - 1\n"
                f"i = ({M_res:.6f}/{C_res:.6f})^(1/{tempo_unidade:.6f}) - 1\n"
                f"i = {taxa_unidade/100:.8f}\n"
                f"i = {taxa_unidade:.6f}% {i_unit}"
            )
            hp = hp_compound_for_i(C_res, M_res, tempo_unidade, taxa_unidade)
        else:
            formula = (
                f"t = ln(M/C) / ln(1+i)\n"
                f"t = ln({M_res:.6f}/{C_res:.6f}) / ln(1 + {taxa_unidade/100:.8f})\n"
                f"t = {tempo_unidade:.6f} {t_unit}"
            )
            hp = hp_compound_for_t(C_res, M_res, taxa_unidade, tempo_unidade)

        show_formula_block(formula)
        if mostrar_hp:
            show_hp_block(hp)

def render_capdiff():
    st.subheader("capitalização diferente")
    C = st.number_input("capital inicial", min_value=0.0, value=80000.0, step=1000.0, key="cd_C")
    annual_rate = st.number_input("taxa nominal anual (%)", min_value=0.0, value=21.0, step=0.1, key="cd_i")
    cap_unit = st.selectbox("capitalizados", ["ao mês", "ao bimestre", "ao trimestre", "ao semestre", "ao ano"], index=1, key="cd_cap")
    prazo = st.number_input("prazo", min_value=0.0, value=5.0, step=1.0, key="cd_t")
    prazo_unit = st.selectbox("unidade do prazo", ["meses", "bimestres", "trimestres", "semestres", "anos"], index=2, key="cd_tu")
    i_period = annual_rate / RATE_UNITS[cap_unit] / 100
    n_periods = convert_time(prazo, prazo_unit, RATE_TO_TIME[cap_unit])
    M = C * ((1 + i_period) ** n_periods)
    st.metric("montante", money(M))
    show_formula_block(
        f"1) taxa por período de capitalização:\n"
        f"i = {annual_rate:.6f}% / {RATE_UNITS[cap_unit]} = {i_period*100:.6f}%\n\n"
        f"2) converter prazo:\n"
        f"{prazo:.6f} {prazo_unit} = {n_periods:.6f} períodos de capitalização\n\n"
        f"3) M = C(1+i)^n\n"
        f"M = {C:.6f}(1 + {i_period:.8f})^{n_periods:.6f}\n"
        f"M = {M:.6f}"
    )
    show_hp_block(
        "\n".join([
            "f REG",
            f"{C:.10g} CHS PV",
            f"{i_period*100:.10g} i",
            f"{n_periods:.10g} n",
            "FV",
            f"FV = {M:.10g}"
        ])
    )

def render_vpfv():
    st.subheader("valor presente / futuro")
    modo = st.radio("modo", ["achar valor futuro", "achar valor presente"], horizontal=not watch_mode, key="vf_modo")
    regime = st.radio("regime", ["juros simples", "juros compostos"], horizontal=not watch_mode, key="vf_reg")
    val = st.number_input("valor base", min_value=0.0, value=23000.0 if modo == "achar valor presente" else 20000.0, step=1000.0, key="vf_val")
    taxa = st.number_input("taxa (%)", min_value=0.0, value=18.0 if regime == "juros compostos" else 5.0, step=0.1, key="vf_taxa")
    taxa_unit = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=6 if regime == "juros compostos" else 2, key="vf_tu")
    tempo = st.number_input("tempo", min_value=0.0, value=288.0 if modo == "achar valor presente" else 8.0, step=1.0, key="vf_tempo")
    tempo_unit = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=0 if modo == "achar valor presente" else 5, key="vf_tempou")

    if regime == "juros simples":
        i_annual = annual_nominal_from_simple(taxa, taxa_unit)
        t_years = to_years(tempo, tempo_unit)
        if modo == "achar valor futuro":
            out = val * (1 + i_annual * t_years)
            st.metric("valor futuro / montante", money(out))
            show_formula_block(
                f"i anual nominal = {i_annual:.8f}\n"
                f"t em anos = {t_years:.8f}\n"
                f"FV = PV(1+i·t)\n"
                f"FV = {val:.6f}(1 + {i_annual:.8f} × {t_years:.8f})\n"
                f"FV = {out:.6f}"
            )
        else:
            out = val / (1 + i_annual * t_years)
            st.metric("valor presente", money(out))
            show_formula_block(
                f"i anual nominal = {i_annual:.8f}\n"
                f"t em anos = {t_years:.8f}\n"
                f"PV = FV / (1+i·t)\n"
                f"PV = {val:.6f} / (1 + {i_annual:.8f} × {t_years:.8f})\n"
                f"PV = {out:.6f}"
            )
    else:
        i_annual = rate_to_effective_annual(taxa, taxa_unit)
        t_years = to_years(tempo, tempo_unit)
        if modo == "achar valor futuro":
            out = val * ((1 + i_annual) ** t_years)
            st.metric("valor futuro / montante", money(out))
            show_formula_block(
                f"i efetiva anual = {i_annual:.8f}\n"
                f"t em anos = {t_years:.8f}\n"
                f"FV = PV(1+i)^t\n"
                f"FV = {val:.6f}(1 + {i_annual:.8f})^{t_years:.8f}\n"
                f"FV = {out:.6f}"
            )
        else:
            out = val / ((1 + i_annual) ** t_years)
            st.metric("valor presente", money(out))
            show_formula_block(
                f"i efetiva anual = {i_annual:.8f}\n"
                f"t em anos = {t_years:.8f}\n"
                f"PV = FV / (1+i)^t\n"
                f"PV = {val:.6f} / (1 + {i_annual:.8f})^{t_years:.8f}\n"
                f"PV = {out:.6f}"
            )

def render_mista():
    st.subheader("capitalização mista")
    C = st.number_input("capital", min_value=0.0, value=1000.0, step=100.0, key="m_C")
    taxa = st.number_input("taxa (%)", min_value=0.0, value=20.0, step=0.1, key="m_i")
    taxa_unit = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=6, key="m_iu")
    tempo = st.number_input("tempo", min_value=0.0, value=2.5, step=0.5, key="m_t")
    tempo_unit = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=6, key="m_tu")

    n_periods = convert_time(tempo, tempo_unit, RATE_TO_TIME[taxa_unit])
    i_period = taxa / 100
    M_simples = C * (1 + i_period * n_periods)
    M_compostos = C * ((1 + i_period) ** n_periods)
    M_mista = mixed_capitalization(C, i_period, n_periods)

    st.metric("juros simples", money(M_simples))
    st.metric("juros compostos", money(M_compostos))
    st.metric("capitalização mista", money(M_mista))
    show_formula_block(
        f"n períodos = {n_periods:.6f}\n"
        f"parte inteira = {math.floor(n_periods)}\n"
        f"parte fracionária = {n_periods - math.floor(n_periods):.6f}\n\n"
        f"simples: M = C(1+i·n) = {M_simples:.6f}\n"
        f"compostos: M = C(1+i)^n = {M_compostos:.6f}\n"
        f"mista: M = C(1+i)^n_int · (1+i·f) = {M_mista:.6f}"
    )
    show_hp_block(
        "na hp12c clássica:\n"
        "com C no visor → compostos puros\n"
        "sem C no visor → parte inteira composta e parte fracionária simples"
    )

renderers = {
    "percentuais": render_percentuais,
    "conversão de tempo": render_conversao,
    "taxas proporcionais": render_prop,
    "taxas equivalentes": render_equiv,
    "juros simples": render_js,
    "juros compostos": render_jc,
    "capitalização diferente": render_capdiff,
    "valor presente / futuro": render_vpfv,
    "capitalização mista": render_mista,
}

if watch_mode:
    section = st.selectbox("abrir cálculo", SECTIONS)
    renderers[section]()
else:
    tabs = st.tabs(SECTIONS)
    for tab, name in zip(tabs, SECTIONS):
        with tab:
            renderers[name]()

st.markdown("</div>", unsafe_allow_html=True)
