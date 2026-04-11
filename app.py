
import math
import streamlit as st

st.set_page_config(page_title="matemática financeira v2", page_icon="💸", layout="wide")

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

def periodic_rate_from_annual_with_cap(rate_pct: float, annual_unit_label: str, capitalization_unit_label: str) -> float:
    # usada quando o enunciado traz "x% a.a. capitalizados bimestralmente"
    if annual_unit_label != "ao ano":
        annual_eff = rate_to_effective_annual(rate_pct, annual_unit_label)
        return annual_eff_to_rate(annual_eff, capitalization_unit_label)
    return rate_pct / RATE_UNITS[capitalization_unit_label.replace("ao ", "ao ")]

st.title("matemática financeira aplicada — v2")
st.caption("agora com taxas proporcionais, taxas equivalentes, capitalização em periodicidade diferente, valor presente/futuro e comparadores.")

with st.expander("o que esta versão cobre", expanded=False):
    st.markdown("""
- porcentagem, aumento, desconto e percentuais sucessivos  
- conversão de tempo entre dia/mês/bimestre/trimestre/semestre/ano  
- taxas proporcionais  
- taxas equivalentes em juros compostos  
- juros simples: C, J, M, i, t  
- juros compostos: C, J, M, i, t  
- capitalização mista  
- taxa anual com capitalização em outra periodicidade  
- valor presente / valor futuro de aplicações
""")

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
            f"x% do valor = {base:.2f} × {taxa/100:.6f} = {valor_pct:.6f}\n"
            f"aumento = {base:.2f} × (1 + {taxa/100:.6f}) = {aumento:.6f}\n"
            f"desconto = {base:.2f} × (1 - {taxa/100:.6f}) = {desconto:.6f}"
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
        if passos:
            st.markdown("**passo a passo**")
            for p in passos:
                st.write(p)

with tabs[1]:
    st.subheader("conversão automática de tempo")
    c1, c2 = st.columns(2)
    with c1:
        t_val = st.number_input("tempo", min_value=0.0, value=15.0, step=1.0)
        t_from = st.selectbox("de", list(TIME_UNITS.keys()), index=0)
        t_to = st.selectbox("para", list(TIME_UNITS.keys()), index=2)
        conv = convert_time(t_val, t_from, t_to)
        st.success(f"{t_val} {t_from} = {conv:.6f} {t_to}")
    with c2:
        st.markdown("**equivalências principais**")
        st.write("1 ano = 12 meses = 6 bimestres = 4 trimestres = 2 semestres = 360 dias corridos")
        st.write("1 semestre = 6 meses = 3 bimestres = 2 trimestres = 180 dias")
        st.write("1 trimestre = 3 meses = 90 dias")
        st.write("1 bimestre = 2 meses = 60 dias")
        st.write("1 mês = 30 dias")

with tabs[2]:
    st.subheader("taxas proporcionais")
    st.caption("para juros simples e exercícios do tipo 'qual a taxa proporcional...'")
    c1, c2 = st.columns(2)
    with c1:
        r = st.number_input("taxa que eu tenho (%)", value=2.0, step=0.1)
        r_from = st.selectbox("unidade da taxa que eu tenho", list(RATE_UNITS.keys()), index=3)
        r_to = st.selectbox("unidade da taxa que eu quero", list(RATE_UNITS.keys()), index=5)
        prop = simple_proportional(r, r_from, r_to)
        st.metric("taxa proporcional", f"{pct(prop,4)} {r_to}")
        st.code(
            f"taxa proporcional = taxa × (períodos destino / períodos origem)\n"
            f"resultado = {r:.6f}% ajustado de {r_from} para {r_to}\n"
            f"= {prop:.6f}%"
        )
    with c2:
        st.markdown("**exemplos clássicos**")
        ex1 = simple_proportional(2, "ao bimestre", "ao semestre")
        ex2 = simple_proportional(3, "ao mês", "ao ano")
        ex3 = simple_proportional(18, "ao ano", "ao mês")
        st.write(f"2% a.b → semestre = {pct(ex1,2)}")
        st.write(f"3% a.m → ano = {pct(ex2,2)}")
        st.write(f"18% a.a → mês = {pct(ex3,4)}")

with tabs[3]:
    st.subheader("taxas equivalentes em juros compostos")
    c1, c2 = st.columns(2)
    with c1:
        r_eq = st.number_input("taxa base (%)", value=20.0, step=0.1, key="eq_r")
        eq_from = st.selectbox("unidade da taxa base", list(RATE_UNITS.keys()), index=2, key="eq_from")
        eq_to = st.selectbox("unidade da taxa equivalente", list(RATE_UNITS.keys()), index=3, key="eq_to")
        eq = compound_effective_to_effective(r_eq, eq_from, eq_to)
        st.metric("taxa equivalente", f"{pct(eq,6)} {eq_to}")
        st.code(
            f"i_quero = (1+i_tenho)^proporção - 1\n"
            f"taxa equivalente = {eq:.8f}%"
        )
    with c2:
        st.markdown("**casos cobrados**")
        st.write(f"1% a.m → a.a = {pct(compound_effective_to_effective(1, 'ao mês', 'ao ano'),4)}")
        st.write(f"12% a.a → a.m = {pct(compound_effective_to_effective(12, 'ao ano', 'ao mês'),4)}")
        st.write(f"1% a.d.u → a.a.o = {pct(compound_effective_to_effective(1, 'ao dia útil (252)', 'ao ano'),4)}")
        st.write(f"24% a.a → a.d.u = {pct(compound_effective_to_effective(24, 'ao ano', 'ao dia útil (252)'),6)}")

with tabs[4]:
    st.subheader("solver de juros simples")
    alvo = st.selectbox("descobrir", ["montante (M)", "juros (J)", "capital (C)", "taxa (i)", "tempo (t)"], key="js_alvo")
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
        d, e = st.columns(2)
        d.metric("taxa", f"{pct((i_res / RATE_UNITS[i_unit]) * 100,6)} {i_unit}")
        d.caption("taxa na unidade escolhida")
        e.metric("tempo", f"{years_to_time(t_res, t_unit):.6f} {t_unit}")
        st.code(
            f"J = C·i·t\nM = C(1+i·t)\n\n"
            f"C = {C_res:.6f}\n"
            f"i anual nominal = {i_res:.8f}\n"
            f"t em anos = {t_res:.8f}\n"
            f"M = {M_res:.6f}\n"
            f"J = {J_res:.6f}"
        )

with tabs[5]:
    st.subheader("solver de juros compostos")
    alvo = st.selectbox("descobrir", ["montante (M)", "juros (J)", "capital (C)", "taxa (i)", "tempo (t)"], key="jc_alvo")
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
        d, e = st.columns(2)
        d.metric("taxa equivalente", f"{pct(annual_eff_to_rate(i_res, i_unit),6)} {i_unit}")
        e.metric("tempo", f"{years_to_time(t_res, t_unit):.6f} {t_unit}")
        st.code(
            f"M = C(1+i)^t\n"
            f"i efetiva anual = {i_res:.8f}\n"
            f"t em anos = {t_res:.8f}\n"
            f"M = {M_res:.6f}\n"
            f"J = {J_res:.6f}"
        )

with tabs[6]:
    st.subheader("juros compostos com capitalização em periodicidade diferente")
    st.caption("exercícios do tipo: 24% a.a. capitalizados bimestralmente; prazo em meses/trimestres/anos.")
    c1, c2 = st.columns(2)
    with c1:
        C = st.number_input("capital inicial", min_value=0.0, value=80000.0, step=1000.0, key="capd_C")
        annual_rate = st.number_input("taxa nominal anual (%)", min_value=0.0, value=21.0, step=0.1, key="capd_i")
        cap_unit = st.selectbox("capitalizados", ["ao mês", "ao bimestre", "ao trimestre", "ao semestre", "ao ano"], index=1, key="capd_cap")
    with c2:
        prazo = st.number_input("prazo", min_value=0.0, value=5.0, step=1.0, key="capd_t")
        prazo_unit = st.selectbox("unidade do prazo", ["meses", "bimestres", "trimestres", "semestres", "anos"], index=2, key="capd_tu")
        operacao = st.radio("calcular", ["montante", "valor presente"], horizontal=True, key="capd_op")

    i_period = annual_rate / RATE_UNITS[cap_unit] / 100
    n_periods = convert_time(prazo, prazo_unit, cap_unit.replace("ao ", "").replace("dia corrido (360)", "dias corridos (360)").replace("dia útil (252)", "dias úteis (252)") + "")
    # map rate unit labels to time unit labels
    map_time = {
        "ao mês": "meses",
        "ao bimestre": "bimestres",
        "ao trimestre": "trimestres",
        "ao semestre": "semestres",
        "ao ano": "anos",
    }
    n_periods = convert_time(prazo, prazo_unit, map_time[cap_unit])
    if operacao == "montante":
        M = C * ((1 + i_period) ** n_periods)
        st.metric("montante", money(M))
        st.metric("taxa por período de capitalização", pct(i_period * 100, 6))
        st.metric("número de períodos", f"{n_periods:.6f}")
        st.code(
            f"i_per = {annual_rate}/ {RATE_UNITS[cap_unit]} = {i_period:.8f}\n"
            f"n = {prazo} {prazo_unit} = {n_periods:.6f} {cap_unit}\n"
            f"M = {C:.2f}(1+{i_period:.8f})^{n_periods:.6f} = {M:.6f}"
        )
    else:
        FV = st.number_input("montante futuro desejado", min_value=0.0, value=75000.0, step=1000.0, key="capd_FV")
        PV = FV / ((1 + i_period) ** n_periods)
        st.metric("valor presente", money(PV))
        st.metric("taxa por período de capitalização", pct(i_period * 100, 6))
        st.metric("número de períodos", f"{n_periods:.6f}")
        st.code(
            f"PV = FV / (1+i)^n\n"
            f"PV = {FV:.2f} / (1+{i_period:.8f})^{n_periods:.6f} = {PV:.6f}"
        )

with tabs[7]:
    st.subheader("valor presente / valor futuro")
    st.caption("para exercícios de aplicação necessária hoje ou resgate futuro.")
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
        tipo_ano = st.radio("base de dias", ["360", "252"], horizontal=True)

    # adjust day labels if needed
    if tempo_unit == "dias corridos (360)" and tipo_ano == "252":
        tempo_unit_eff = "dias úteis (252)"
    else:
        tempo_unit_eff = tempo_unit

    if regime == "juros simples":
        i_annual = annual_nominal_from_simple(taxa, taxa_unit)
        t_years = to_years(tempo, tempo_unit_eff)
        if modo == "achar valor futuro":
            FV = val * (1 + i_annual * t_years)
            st.metric("valor futuro / montante", money(FV))
            st.code(f"FV = PV(1+i·t) = {val:.2f}(1+{i_annual:.8f}·{t_years:.8f}) = {FV:.6f}")
        else:
            PV = val / (1 + i_annual * t_years)
            st.metric("valor presente / aplicação necessária", money(PV))
            st.code(f"PV = FV/(1+i·t) = {val:.2f}/(1+{i_annual:.8f}·{t_years:.8f}) = {PV:.6f}")
    else:
        i_annual = rate_to_effective_annual(taxa, taxa_unit)
        t_years = to_years(tempo, tempo_unit_eff)
        if modo == "achar valor futuro":
            FV = val * ((1 + i_annual) ** t_years)
            st.metric("valor futuro / montante", money(FV))
            st.code(f"FV = PV(1+i)^t = {val:.2f}(1+{i_annual:.8f})^{t_years:.8f} = {FV:.6f}")
        else:
            PV = val / ((1 + i_annual) ** t_years)
            st.metric("valor presente / aplicação necessária", money(PV))
            st.code(f"PV = FV/(1+i)^t = {val:.2f}/(1+{i_annual:.8f})^{t_years:.8f} = {PV:.6f}")

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

    target_time = {
        "ao dia corrido (360)": "dias corridos (360)",
        "ao dia útil (252)": "dias úteis (252)",
        "ao mês": "meses",
        "ao bimestre": "bimestres",
        "ao trimestre": "trimestres",
        "ao semestre": "semestres",
        "ao ano": "anos",
    }[taxa_unit]
    n_periods = convert_time(tempo, tempo_unit, target_time)
    i_period = taxa / 100

    M_simples = C * (1 + i_period * n_periods)
    M_compostos = C * ((1 + i_period) ** n_periods)
    M_mista = mixed_capitalization(C, i_period, n_periods)

    a, b, c = st.columns(3)
    a.metric("juros simples", money(M_simples))
    b.metric("juros compostos puros", money(M_compostos))
    c.metric("capitalização mista", money(M_mista))
    st.code(
        f"n períodos = {n_periods:.6f}\n"
        f"parte inteira = {math.floor(n_periods)}\n"
        f"parte fracionária = {n_periods - math.floor(n_periods):.6f}\n"
        f"M_mista = C(1+i)^n_int · (1+i·f)"
    )
