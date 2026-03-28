
import math
import streamlit as st

st.set_page_config(page_title="matemática financeira", page_icon="💸", layout="wide")

# ---------- helpers ----------
TIME_UNITS = {
    "dias corridos (base 360)": ("days_360", 1/360),
    "dias úteis (base 252)": ("days_252", 1/252),
    "meses": ("months", 1/12),
    "bimestres": ("bimesters", 2/12),
    "trimestres": ("quarters", 3/12),
    "semestres": ("semesters", 6/12),
    "anos": ("years", 1.0),
}

RATE_UNITS = {
    "ao dia corrido (base 360)": ("days_360", 360),
    "ao dia útil (base 252)": ("days_252", 252),
    "ao mês": ("months", 12),
    "ao bimestre": ("bimesters", 6),
    "ao trimestre": ("quarters", 4),
    "ao semestre": ("semesters", 2),
    "ao ano": ("years", 1),
}

def to_years(value: float, unit_label: str) -> float:
    return value * TIME_UNITS[unit_label][1]

def years_to_time(years: float, unit_label: str) -> float:
    mult = TIME_UNITS[unit_label][1]
    return years / mult

def nominal_rate_to_annual(rate_pct: float, unit_label: str) -> float:
    periods_per_year = RATE_UNITS[unit_label][1]
    return (rate_pct / 100.0) * periods_per_year

def annual_rate_to_nominal(annual_decimal: float, unit_label: str) -> float:
    periods_per_year = RATE_UNITS[unit_label][1]
    return (annual_decimal / periods_per_year) * 100.0

def compound_equivalent_rate(rate_pct: float, from_unit: str, to_unit: str) -> float:
    annual_eff = (1 + rate_pct/100.0) ** RATE_UNITS[from_unit][1] - 1
    per_target = (1 + annual_eff) ** (1 / RATE_UNITS[to_unit][1]) - 1
    return per_target * 100.0

def simple_rate_equivalent(rate_pct: float, from_unit: str, to_unit: str) -> float:
    annual_nom = nominal_rate_to_annual(rate_pct, from_unit)
    return annual_rate_to_nominal(annual_nom, to_unit)

def format_money(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_pct(v: float) -> str:
    return f"{v:.6f}%".replace(".", ",")

def safe_log(x: float) -> float:
    return math.log(x)

def solve_simple(known: dict):
    C = known.get("C")
    i = known.get("i")
    t = known.get("t")
    M = known.get("M")
    # i in decimal annual, t in years
    if C is None and None not in (M, i, t):
        C = M / (1 + i*t)
    elif i is None and None not in (C, M, t):
        i = (M/C - 1) / t
    elif t is None and None not in (C, M, i):
        t = (M/C - 1) / i
    elif M is None and None not in (C, i, t):
        M = C * (1 + i*t)
    J = None
    if None not in (C, M):
        J = M - C
    return {"C": C, "i": i, "t": t, "M": M, "J": J}

def solve_compound(known: dict):
    C = known.get("C")
    i = known.get("i")
    t = known.get("t")
    M = known.get("M")
    # i in decimal annual effective, t in years
    if C is None and None not in (M, i, t):
        C = M / ((1 + i) ** t)
    elif i is None and None not in (C, M, t):
        i = (M/C) ** (1/t) - 1
    elif t is None and None not in (C, M, i):
        t = safe_log(M/C) / safe_log(1 + i)
    elif M is None and None not in (C, i, t):
        M = C * ((1 + i) ** t)
    J = None
    if None not in (C, M):
        J = M - C
    return {"C": C, "i": i, "t": t, "M": M, "J": J}

def mixed_capitalization(C: float, rate_decimal_per_period: float, t_periods: float):
    integer_part = math.floor(t_periods)
    fractional_part = t_periods - integer_part
    return C * ((1 + rate_decimal_per_period) ** integer_part) * (1 + rate_decimal_per_period * fractional_part)

# ---------- UI ----------
st.title("matemática financeira aplicada")
st.caption("app pronto para hospedar, com conversão automática de dias/meses/anos e resolução de vários exercícios de juros simples e compostos.")

with st.expander("como o app interpreta tempo e taxa", expanded=False):
    st.markdown(
        """
- para **tempo**, o app converte tudo para **anos** internamente  
- **dias corridos** usam base **360**  
- **dias úteis** usam base **252**  
- para **juros simples**, a equivalência é proporcional  
- para **juros compostos**, a equivalência usa taxa **equivalente**
        """
    )

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "conversor",
    "juros simples",
    "juros compostos",
    "capitalização mista",
    "percentuais",
])

with tab1:
    st.subheader("conversão automática")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**tempo**")
        time_value = st.number_input("valor do tempo", min_value=0.0, value=15.0, step=1.0, key="time_value")
        time_from = st.selectbox("unidade de origem", list(TIME_UNITS.keys()), index=0, key="time_from")
        time_to = st.selectbox("unidade de destino", list(TIME_UNITS.keys()), index=2, key="time_to")
        years = to_years(time_value, time_from)
        converted_time = years_to_time(years, time_to)
        st.success(f"{time_value} {time_from} = **{converted_time:.6f} {time_to}**")

    with col2:
        st.markdown("**taxa**")
        rate_value = st.number_input("taxa (%)", value=5.0, step=0.1, key="rate_value")
        rate_from = st.selectbox("período da taxa (origem)", list(RATE_UNITS.keys()), index=2, key="rate_from")
        rate_to = st.selectbox("período da taxa (destino)", list(RATE_UNITS.keys()), index=6, key="rate_to")
        mode = st.radio("tipo de equivalência", ["juros simples", "juros compostos"], horizontal=True)
        if mode == "juros simples":
            converted_rate = simple_rate_equivalent(rate_value, rate_from, rate_to)
        else:
            converted_rate = compound_equivalent_rate(rate_value, rate_from, rate_to)
        st.success(f"{format_pct(rate_value)} {rate_from} = **{format_pct(converted_rate)} {rate_to}**")

with tab2:
    st.subheader("solver de juros simples")
    target = st.selectbox(
        "o que você quer descobrir?",
        ["montante (M)", "juros (J)", "capital (C)", "taxa (i)", "tempo (t)"],
        key="simple_target"
    )
    c1, c2 = st.columns(2)
    with c1:
        C_in = None if target == "capital (C)" else st.number_input("capital (C)", min_value=0.0, value=50000.0, step=100.0, key="sC")
        M_in = None if target in ["montante (M)", "juros (J)"] else st.number_input("montante (M)", min_value=0.0, value=72500.0, step=100.0, key="sM")
    with c2:
        rate_s = None if target == "taxa (i)" else st.number_input("taxa (%)", min_value=0.0, value=5.0, step=0.1, key="si")
        rate_unit_s = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=2, key="s_rate_unit")
        time_s = None if target == "tempo (t)" else st.number_input("tempo", min_value=0.0, value=9.0, step=1.0, key="st")
        time_unit_s = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=2, key="s_time_unit")

    annual_i = None if rate_s is None else nominal_rate_to_annual(rate_s, rate_unit_s)
    years_t = None if time_s is None else to_years(time_s, time_unit_s)

    if target == "juros (J)":
        if None not in (C_in, annual_i, years_t):
            res = solve_simple({"C": C_in, "i": annual_i, "t": years_t, "M": None})
            st.metric("juros (J)", format_money(res["J"]))
            st.metric("montante (M)", format_money(res["M"]))
            st.code(f"M = C(1 + i·t)\nM = {C_in:.2f}(1 + {annual_i:.6f}·{years_t:.6f})\nM = {res['M']:.6f}\nJ = M - C = {res['J']:.6f}")
    else:
        res = solve_simple({"C": C_in, "i": annual_i, "t": years_t, "M": M_in})
        if None not in res.values():
            c3, c4, c5 = st.columns(3)
            c3.metric("capital (C)", format_money(res["C"]))
            c4.metric("montante (M)", format_money(res["M"]))
            c5.metric("juros (J)", format_money(res["J"]))
            st.divider()
            time_out = years_to_time(res["t"], time_unit_s)
            rate_out = annual_rate_to_nominal(res["i"], rate_unit_s)
            c6, c7 = st.columns(2)
            c6.metric("taxa", f"{format_pct(rate_out)} {rate_unit_s}")
            c7.metric("tempo", f"{time_out:.6f} {time_unit_s}")
            st.code(
                f"J = C·i·t\nM = C(1 + i·t)\n\n"
                f"C = {res['C']:.6f}\n"
                f"i (anual) = {res['i']:.8f}\n"
                f"t (anos) = {res['t']:.8f}\n"
                f"M = {res['M']:.6f}\n"
                f"J = {res['J']:.6f}"
            )

with tab3:
    st.subheader("solver de juros compostos")
    target_c = st.selectbox(
        "o que você quer descobrir agora?",
        ["montante (M)", "juros (J)", "capital (C)", "taxa (i)", "tempo (t)"],
        key="compound_target"
    )
    cc1, cc2 = st.columns(2)
    with cc1:
        Cc_in = None if target_c == "capital (C)" else st.number_input("capital inicial (C)", min_value=0.0, value=1000.0, step=100.0, key="cC")
        Mc_in = None if target_c in ["montante (M)", "juros (J)"] else st.number_input("montante final (M)", min_value=0.0, value=1728.0, step=100.0, key="cM")
    with cc2:
        rate_c = None if target_c == "taxa (i)" else st.number_input("taxa (%) ", min_value=0.0, value=20.0, step=0.1, key="ci")
        rate_unit_c = st.selectbox("unidade da taxa ", list(RATE_UNITS.keys()), index=6, key="c_rate_unit")
        time_c = None if target_c == "tempo (t)" else st.number_input("tempo ", min_value=0.0, value=3.0, step=0.5, key="ct")
        time_unit_c = st.selectbox("unidade do tempo ", list(TIME_UNITS.keys()), index=6, key="c_time_unit")

    if rate_c is not None and time_c is not None:
        # convert using effective equivalent
        annual_eff = (1 + rate_c/100.0) ** RATE_UNITS[rate_unit_c][1] - 1
        years_eff = to_years(time_c, time_unit_c)
    else:
        annual_eff = None
        years_eff = None

    if target_c == "juros (J)":
        if None not in (Cc_in, annual_eff, years_eff):
            res = solve_compound({"C": Cc_in, "i": annual_eff, "t": years_eff, "M": None})
            st.metric("juros (J)", format_money(res["J"]))
            st.metric("montante (M)", format_money(res["M"]))
            st.code(f"M = C(1+i)^t\nM = {Cc_in:.2f}(1+{annual_eff:.6f})^{years_eff:.6f}\nM = {res['M']:.6f}\nJ = M - C = {res['J']:.6f}")
    else:
        res = solve_compound({"C": Cc_in, "i": annual_eff, "t": years_eff, "M": Mc_in})
        if None not in res.values():
            dc1, dc2, dc3 = st.columns(3)
            dc1.metric("capital (C)", format_money(res["C"]))
            dc2.metric("montante (M)", format_money(res["M"]))
            dc3.metric("juros (J)", format_money(res["J"]))
            st.divider()
            rate_out = ((1 + res["i"]) ** (1 / RATE_UNITS[rate_unit_c][1]) - 1) * 100
            time_out = years_to_time(res["t"], time_unit_c)
            dc4, dc5 = st.columns(2)
            dc4.metric("taxa equivalente", f"{format_pct(rate_out)} {rate_unit_c}")
            dc5.metric("tempo", f"{time_out:.6f} {time_unit_c}")
            st.code(
                f"M = C(1+i)^t\n\n"
                f"C = {res['C']:.6f}\n"
                f"i efetiva anual = {res['i']:.8f}\n"
                f"t (anos) = {res['t']:.8f}\n"
                f"M = {res['M']:.6f}\n"
                f"J = {res['J']:.6f}"
            )

with tab4:
    st.subheader("capitalização mista / convenção hp12c")
    st.caption("compara: juros simples, juros compostos puros e capitalização mista (composto na parte inteira e simples na parte fracionária).")
    mc1, mc2 = st.columns(2)
    with mc1:
        C_mix = st.number_input("capital", min_value=0.0, value=1000.0, step=100.0, key="mixC")
        rate_mix = st.number_input("taxa (%)", min_value=0.0, value=20.0, step=0.1, key="mixi")
        rate_unit_mix = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=6, key="mix_rate_unit")
    with mc2:
        time_mix = st.number_input("tempo", min_value=0.0, value=2.5, step=0.5, key="mixt")
        time_unit_mix = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=6, key="mix_time_unit")

    # convert time to number of rate periods
    years_mix = to_years(time_mix, time_unit_mix)
    periods_per_year_mix = RATE_UNITS[rate_unit_mix][1]
    t_periods = years_mix * periods_per_year_mix
    i_period = rate_mix / 100.0

    M_simple = C_mix * (1 + i_period * t_periods)
    M_compound = C_mix * ((1 + i_period) ** t_periods)
    M_mixed = mixed_capitalization(C_mix, i_period, t_periods)

    e1, e2, e3 = st.columns(3)
    e1.metric("juros simples", format_money(M_simple))
    e2.metric("juros compostos puros", format_money(M_compound))
    e3.metric("capitalização mista", format_money(M_mixed))

    st.code(
        f"nº de períodos da taxa = {t_periods:.6f}\n"
        f"parte inteira = {math.floor(t_periods)}\n"
        f"parte fracionária = {t_periods - math.floor(t_periods):.6f}\n\n"
        f"simples: M = C(1 + i·t)\n"
        f"compostos: M = C(1+i)^t\n"
        f"mista: M = C(1+i)^inteiro · (1 + i·fração)"
    )

with tab5:
    st.subheader("porcentagem, aumentos, descontos e variações sucessivas")
    p1, p2 = st.columns(2)

    with p1:
        base_value = st.number_input("valor base", min_value=0.0, value=500.0, step=10.0)
        pct = st.number_input("percentual (%)", value=40.0, step=0.1)
        increase_factor = 1 + pct/100.0
        discount_factor = 1 - pct/100.0
        st.metric("aumento", format_money(base_value * increase_factor))
        st.metric("desconto", format_money(base_value * discount_factor))

    with p2:
        st.markdown("**percentuais sucessivos**")
        seq_text = st.text_input("digite percentuais separados por vírgula", value="-50, 100, -20, 30")
        initial_seq = st.number_input("valor inicial", min_value=0.0, value=100.0, step=10.0)
        try:
            seq = [float(x.strip().replace("%", "").replace(",", ".")) for x in seq_text.split(";")] if ";" in seq_text else [float(x.strip().replace("%", "").replace(",", ".")) for x in seq_text.split(",")]
            factors = [(1 + x/100.0) for x in seq]
            final = initial_seq
            for f in factors:
                final *= f
            var_pct = ((final / initial_seq) - 1) * 100 if initial_seq != 0 else 0
            st.metric("valor final", format_money(final))
            st.metric("variação total", format_pct(var_pct))
            st.code(" × ".join([f"{initial_seq:.2f}"] + [f"{f:.4f}" for f in factors]) + f" = {final:.6f}")
        except Exception:
            st.error("não consegui ler a sequência. exemplo válido: -50, 100, -20, 30")

st.divider()
st.markdown(
    """
### tipos de exercícios que este app cobre
- descobrir **montante**, **juros**, **capital**, **taxa** ou **tempo**
- converter **dias corridos / dias úteis / meses / bimestres / trimestres / semestres / anos**
- comparar **juros simples x compostos x capitalização mista**
- calcular **aumento, desconto e percentuais sucessivos**
- resolver exercícios com taxa e tempo em unidades diferentes
"""
)
