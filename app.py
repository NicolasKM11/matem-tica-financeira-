
import math
import streamlit as st

st.set_page_config(page_title="matemática financeira v3", page_icon="💸", layout="wide")

TIME_UNITS = {
    "dias corridos (360)": {"years_factor": 1/360, "periods_per_year": 360},
    "dias úteis (252)": {"years_factor": 1/252, "periods_per_year": 252},
    "meses": {"years_factor": 1/12, "periods_per_year": 12},
    "bimestres": {"years_factor": 1/6, "periods_per_year": 6},
    "trimestres": {"years_factor": 1/4, "periods_per_year": 4},
    "semestres": {"years_factor": 1/2, "periods_per_year": 2},
    "anos": {"years_factor": 1.0, "periods_per_year": 1},
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

def hp12c_simple_steps(C, taxa_pct_unidade, taxa_unit, t_val, t_unit, M, J):
    linhas = []
    linhas.append("jeito pela fórmula")
    linhas.append(f"J = C·i·t")
    linhas.append(f"M = C + J")
    linhas.append(f"ou M = C(1 + i·t)")
    linhas.append("")
    linhas.append("jeito na hp12c")
    linhas.append("1) f REG")
    linhas.append("2) digite o capital e CHS PV")
    linhas.append(f"   {C:.10g} CHS PV")
    linhas.append(f"3) digite a taxa na unidade escolhida: {taxa_pct_unidade:.10g}% {taxa_unit}")
    linhas.append(f"   {taxa_pct_unidade:.10g} i")
    linhas.append(f"4) digite o prazo: {t_val:.10g} {t_unit}")
    linhas.append(f"   {t_val:.10g} n")
    linhas.append("5) aperte FV")
    linhas.append(f"   resultado ≈ {M:.10g}")
    linhas.append("")
    linhas.append(f"juros = FV - PV = {J:.10g}")
    return "\n".join(linhas)

def hp12c_compound_steps(C, taxa_pct_unidade, taxa_unit, t_val, t_unit, M, J):
    linhas = []
    linhas.append("jeito pela fórmula")
    linhas.append("M = C(1+i)^t")
    linhas.append("")
    linhas.append("jeito na hp12c")
    linhas.append("1) f REG")
    linhas.append("2) digite o capital e CHS PV")
    linhas.append(f"   {C:.10g} CHS PV")
    linhas.append(f"3) digite a taxa na unidade escolhida: {taxa_pct_unidade:.10g}% {taxa_unit}")
    linhas.append(f"   {taxa_pct_unidade:.10g} i")
    linhas.append(f"4) digite o prazo: {t_val:.10g} {t_unit}")
    linhas.append(f"   {t_val:.10g} n")
    linhas.append("5) aperte FV")
    linhas.append(f"   resultado ≈ {M:.10g}")
    linhas.append("")
    linhas.append(f"juros = FV - PV = {J:.10g}")
    return "\n".join(linhas)

st.title("matemática financeira aplicada — v3")
st.caption("agora mostrando resultado pela fórmula e também no estilo hp12c.")

tabs = st.tabs([
    "percentuais",
    "conversão de tempo",
    "taxas proporcionais",
    "taxas equivalentes",
    "juros simples",
    "juros compostos",
    "capitalização diferente",
    "valor presente / futuro",
    "capitalização mista",
])

with tabs[0]:
    st.subheader("aumento, desconto e percentuais sucessivos")
    c1, c2 = st.columns(2)
    with c1:
        base = st.number_input("valor inicial", min_value=0.0, value=500.0, step=100.0)
        taxa = st.number_input("percentual (%)", value=40.0, step=0.1)
        valor_pct = base * taxa / 100
        aumento = base * (1 + taxa / 100)
        desconto = base * (1 - taxa / 100)
        st.metric("x% do valor", money(valor_pct))
        st.metric("com aumento", money(aumento))
        st.metric("com desconto", money(desconto))
        st.code(
            f"{taxa}% de {base} = {valor_pct}\n"
            f"aumento: {base} × (1 + {taxa/100}) = {aumento}\n"
            f"desconto: {base} × (1 - {taxa/100}) = {desconto}"
        )
    with c2:
        seq_base = st.number_input("valor inicial da sequência", min_value=0.0, value=85000.0, step=1000.0)
        seq_text = st.text_input("sequência de taxas (%) separadas por vírgula", value="12, -5, 8")
        taxas = []
        for x in seq_text.split(","):
            try:
                taxas.append(float(x.strip()))
            except:
                pass
        atual = seq_base
        passos = []
        for k, t in enumerate(taxas, start=1):
            fator = 1 + t/100
            atual *= fator
            passos.append(f"{k}) taxa {t:+.4f}% → fator {fator:.6f} → {money(atual)}")
        variacao = (atual/seq_base - 1) * 100 if seq_base else 0
        st.metric("valor final", money(atual))
        st.metric("variação total", pct(variacao, 4))
        for p in passos:
            st.write(p)

with tabs[1]:
    st.subheader("conversão automática de tempo")
    t_val = st.number_input("tempo", min_value=0.0, value=15.0, step=1.0)
    c1, c2 = st.columns(2)
    with c1:
        t_from = st.selectbox("de", list(TIME_UNITS.keys()), index=0)
    with c2:
        t_to = st.selectbox("para", list(TIME_UNITS.keys()), index=2)
    conv = convert_time(t_val, t_from, t_to)
    st.success(f"{t_val} {t_from} = {conv:.6f} {t_to}")

with tabs[2]:
    st.subheader("taxas proporcionais")
    r = st.number_input("taxa que eu tenho (%)", value=2.0, step=0.1)
    c1, c2 = st.columns(2)
    with c1:
        r_from = st.selectbox("unidade da taxa que eu tenho", list(RATE_UNITS.keys()), index=3)
    with c2:
        r_to = st.selectbox("unidade da taxa que eu quero", list(RATE_UNITS.keys()), index=5)
    prop = simple_proportional(r, r_from, r_to)
    st.metric("taxa proporcional", f"{pct(prop,4)} {r_to}")
    st.code(f"taxa proporcional = {r}% ajustada de {r_from} para {r_to} = {prop:.6f}%")

with tabs[3]:
    st.subheader("taxas equivalentes em juros compostos")
    r_eq = st.number_input("taxa base (%)", value=20.0, step=0.1, key="eq_r")
    c1, c2 = st.columns(2)
    with c1:
        eq_from = st.selectbox("unidade da taxa base", list(RATE_UNITS.keys()), index=2, key="eq_from")
    with c2:
        eq_to = st.selectbox("unidade da taxa equivalente", list(RATE_UNITS.keys()), index=3, key="eq_to")
    eq = compound_effective_to_effective(r_eq, eq_from, eq_to)
    st.metric("taxa equivalente", f"{pct(eq,6)} {eq_to}")
    st.code(f"i_quero = taxa equivalente de {r_eq}% {eq_from} para {eq_to} = {eq:.6f}%")

with tabs[4]:
    st.subheader("solver de juros simples")
    alvo = st.selectbox("descobrir", ["montante (M)", "juros (J)", "capital (C)", "taxa (i)", "tempo (t)"], key="js_alvo")
    mostrar_hp = st.toggle("mostrar também o passo a passo da hp12c", value=True, key="js_hp")
    c1, c2 = st.columns(2)
    with c1:
        C = None if alvo == "capital (C)" else st.number_input("capital (C)", min_value=0.0, value=50000.0, step=100.0, key="js_C")
        M = None if alvo in ["montante (M)", "juros (J)"] else st.number_input("montante (M)", min_value=0.0, value=72500.0, step=100.0, key="js_M")
    with c2:
        i_in = None if alvo == "taxa (i)" else st.number_input("taxa (%)", min_value=0.0, value=5.0, step=0.1, key="js_i")
        i_unit = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=2, key="js_i_unit")
        t_in = None if alvo == "tempo (t)" else st.number_input("tempo", min_value=0.0, value=9.0, step=1.0, key="js_t")
        t_unit = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=2, key="js_t_unit")

    i_annual = None if i_in is None else annual_nominal_from_simple(i_in, i_unit)
    t_years = None if t_in is None else to_years(t_in, t_unit)
    C_res, i_res, t_res, M_res, J_res = solve_simple(C, i_annual, t_years, M)

    if None not in (C_res, i_res, t_res, M_res, J_res):
        a, b, c = st.columns(3)
        a.metric("capital", money(C_res))
        b.metric("montante", money(M_res))
        c.metric("juros", money(J_res))
        taxa_unidade = (i_res / RATE_UNITS[i_unit]) * 100
        tempo_unidade = years_to_time(t_res, t_unit)

        st.markdown("**pela fórmula**")
        st.code(
            f"J = C·i·t\n"
            f"M = C + J\n"
            f"M = C(1+i·t)\n\n"
            f"C = {C_res:.6f}\n"
            f"i = {taxa_unidade:.6f}% {i_unit}\n"
            f"t = {tempo_unidade:.6f} {t_unit}\n"
            f"J = {J_res:.6f}\n"
            f"M = {M_res:.6f}"
        )

        if mostrar_hp and alvo in ["montante (M)", "juros (J)"]:
            st.markdown("**pela hp12c**")
            st.code(hp12c_simple_steps(C_res, taxa_unidade, i_unit, tempo_unidade, t_unit, M_res, J_res))

with tabs[5]:
    st.subheader("solver de juros compostos")
    alvo = st.selectbox("descobrir", ["montante (M)", "juros (J)", "capital (C)", "taxa (i)", "tempo (t)"], key="jc_alvo")
    mostrar_hp = st.toggle("mostrar também o passo a passo da hp12c", value=True, key="jc_hp")
    c1, c2 = st.columns(2)
    with c1:
        C = None if alvo == "capital (C)" else st.number_input("capital (C)", min_value=0.0, value=1000.0, step=100.0, key="jc_C")
        M = None if alvo in ["montante (M)", "juros (J)"] else st.number_input("montante (M)", min_value=0.0, value=1728.0, step=100.0, key="jc_M")
    with c2:
        i_in = None if alvo == "taxa (i)" else st.number_input("taxa (%)", min_value=0.0, value=20.0, step=0.1, key="jc_i")
        i_unit = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=6, key="jc_i_unit")
        t_in = None if alvo == "tempo (t)" else st.number_input("tempo", min_value=0.0, value=3.0, step=0.5, key="jc_t")
        t_unit = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=6, key="jc_t_unit")

    i_annual_eff = None if i_in is None else rate_to_effective_annual(i_in, i_unit)
    t_years = None if t_in is None else to_years(t_in, t_unit)
    C_res, i_res, t_res, M_res, J_res = solve_compound(C, i_annual_eff, t_years, M)

    if None not in (C_res, i_res, t_res, M_res, J_res):
        a, b, c = st.columns(3)
        a.metric("capital", money(C_res))
        b.metric("montante", money(M_res))
        c.metric("juros", money(J_res))
        taxa_unidade = annual_eff_to_rate(i_res, i_unit)
        tempo_unidade = years_to_time(t_res, t_unit)

        st.markdown("**pela fórmula**")
        st.code(
            f"M = C(1+i)^t\n\n"
            f"C = {C_res:.6f}\n"
            f"i = {taxa_unidade:.6f}% {i_unit}\n"
            f"t = {tempo_unidade:.6f} {t_unit}\n"
            f"J = {J_res:.6f}\n"
            f"M = {M_res:.6f}"
        )

        if mostrar_hp and alvo in ["montante (M)", "juros (J)"]:
            st.markdown("**pela hp12c**")
            st.code(hp12c_compound_steps(C_res, taxa_unidade, i_unit, tempo_unidade, t_unit, M_res, J_res))

with tabs[6]:
    st.subheader("juros compostos com capitalização em periodicidade diferente")
    c1, c2 = st.columns(2)
    with c1:
        C = st.number_input("capital inicial", min_value=0.0, value=80000.0, step=1000.0, key="capd_C")
        annual_rate = st.number_input("taxa nominal anual (%)", min_value=0.0, value=21.0, step=0.1, key="capd_i")
        cap_unit = st.selectbox("capitalizados", ["ao mês", "ao bimestre", "ao trimestre", "ao semestre", "ao ano"], index=1, key="capd_cap")
    with c2:
        prazo = st.number_input("prazo", min_value=0.0, value=5.0, step=1.0, key="capd_t")
        prazo_unit = st.selectbox("unidade do prazo", ["meses", "bimestres", "trimestres", "semestres", "anos"], index=2, key="capd_tu")
    i_period = annual_rate / RATE_UNITS[cap_unit] / 100
    n_periods = convert_time(prazo, prazo_unit, RATE_TO_TIME[cap_unit])
    M = C * ((1 + i_period) ** n_periods)
    st.metric("montante", money(M))
    st.markdown("**pela fórmula**")
    st.code(
        f"i por período = {annual_rate}/{RATE_UNITS[cap_unit]} = {i_period:.8f}\n"
        f"n = {prazo} {prazo_unit} = {n_periods:.6f} períodos\n"
        f"M = {C:.6f}(1+{i_period:.8f})^{n_periods:.6f} = {M:.6f}"
    )
    st.markdown("**pela hp12c (jeito prático)**")
    st.code(
        f"1) converter a taxa anual para taxa {cap_unit}\n"
        f"2) converter o prazo para quantidade de períodos de capitalização\n"
        f"3) {C:.10g} CHS PV\n"
        f"4) {i_period*100:.10g} i\n"
        f"5) {n_periods:.10g} n\n"
        f"6) FV → {M:.10g}"
    )

with tabs[7]:
    st.subheader("valor presente / valor futuro")
    modo = st.radio("modo", ["achar valor futuro", "achar valor presente"], horizontal=True)
    regime = st.radio("regime", ["juros simples", "juros compostos"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        val = st.number_input("valor base", min_value=0.0, value=23000.0 if modo == "achar valor presente" else 20000.0, step=1000.0)
        taxa = st.number_input("taxa (%)", min_value=0.0, value=18.0 if regime == "juros compostos" else 5.0, step=0.1)
        taxa_unit = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=6 if regime == "juros compostos" else 2)
    with c2:
        tempo = st.number_input("tempo", min_value=0.0, value=288.0 if modo == "achar valor presente" else 8.0, step=1.0)
        tempo_unit = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=0 if modo == "achar valor presente" else 5)

    if regime == "juros simples":
        i_annual = annual_nominal_from_simple(taxa, taxa_unit)
        t_years = to_years(tempo, tempo_unit)
        if modo == "achar valor futuro":
            FV = val * (1 + i_annual * t_years)
            st.metric("valor futuro / montante", money(FV))
            st.code(f"FV = PV(1+i·t) = {val:.6f}(1+{i_annual:.8f}·{t_years:.8f}) = {FV:.6f}")
        else:
            PV = val / (1 + i_annual * t_years)
            st.metric("valor presente / aplicação necessária", money(PV))
            st.code(f"PV = FV/(1+i·t) = {val:.6f}/(1+{i_annual:.8f}·{t_years:.8f}) = {PV:.6f}")
    else:
        i_annual = rate_to_effective_annual(taxa, taxa_unit)
        t_years = to_years(tempo, tempo_unit)
        if modo == "achar valor futuro":
            FV = val * ((1 + i_annual) ** t_years)
            st.metric("valor futuro / montante", money(FV))
            st.code(f"FV = PV(1+i)^t = {val:.6f}(1+{i_annual:.8f})^{t_years:.8f} = {FV:.6f}")
        else:
            PV = val / ((1 + i_annual) ** t_years)
            st.metric("valor presente / aplicação necessária", money(PV))
            st.code(f"PV = FV/(1+i)^t = {val:.6f}/(1+{i_annual:.8f})^{t_years:.8f} = {PV:.6f}")

with tabs[8]:
    st.subheader("capitalização mista")
    c1, c2 = st.columns(2)
    with c1:
        C = st.number_input("capital", min_value=0.0, value=1000.0, step=100.0, key="mix_C")
        taxa = st.number_input("taxa (%)", min_value=0.0, value=20.0, step=0.1, key="mix_i")
        taxa_unit = st.selectbox("unidade da taxa", list(RATE_UNITS.keys()), index=6, key="mix_iu")
    with c2:
        tempo = st.number_input("tempo", min_value=0.0, value=2.5, step=0.5, key="mix_t")
        tempo_unit = st.selectbox("unidade do tempo", list(TIME_UNITS.keys()), index=6, key="mix_tu")

    n_periods = convert_time(tempo, tempo_unit, RATE_TO_TIME[taxa_unit])
    i_period = taxa / 100

    M_simples = C * (1 + i_period * n_periods)
    M_compostos = C * ((1 + i_period) ** n_periods)
    M_mista = mixed_capitalization(C, i_period, n_periods)

    a, b, c = st.columns(3)
    a.metric("juros simples", money(M_simples))
    b.metric("juros compostos puros", money(M_compostos))
    c.metric("capitalização mista", money(M_mista))
    st.code(
        f"simples: M = C(1+i·n) = {M_simples:.6f}\n"
        f"compostos: M = C(1+i)^n = {M_compostos:.6f}\n"
        f"mista: parte inteira composta + parte fracionária simples = {M_mista:.6f}"
    )
