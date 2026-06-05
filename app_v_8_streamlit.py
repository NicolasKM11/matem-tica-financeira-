import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="matemática financeira v8", page_icon="💸", layout="centered")

TIME_FACTORS = {"dia corrido (360)":1/360,"dia civil (365)":1/365,"dia útil (252)":1/252,"mês":1/12,"bimestre":1/6,"trimestre":1/4,"semestre":1/2,"ano":1.0}
PER_YEAR = {"dia corrido (360)":360,"dia civil (365)":365,"dia útil (252)":252,"mês":12,"bimestre":6,"trimestre":4,"semestre":2,"ano":1}

def money(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def pct(v,d=4): return f"{v:.{d}f}%".replace(".", ",")
def to_years(v,u): return v*TIME_FACTORS[u]
def years_to_unit(y,u): return y/TIME_FACTORS[u]
def convert_time(v,fu,tu): return years_to_unit(to_years(v,fu),tu)
def effective_from_nominal(nom, un_taxa, cap): return nom*(PER_YEAR[cap]/PER_YEAR[un_taxa])
def equivalent_rate(rate,fu,tu): return (((1+rate/100)**(PER_YEAR[tu]/PER_YEAR[fu]))-1)*100
def annual_effective_from_rate(rate,unit): return ((1+rate/100)**PER_YEAR[unit])-1
def rate_real(gross,infl): return ((1+gross/100)/(1+infl/100)-1)*100
def gross_required_for_real(real,infl): return (((1+real/100)*(1+infl/100))-1)*100

def npv(rate, cfs):
    r = rate/100
    return sum(cf/((1+r)**t) for t,cf in enumerate(cfs))

def irr(cfs):
    def f(r): return sum(cf/((1+r)**t) for t,cf in enumerate(cfs))
    lo, hi = -0.9999, 10
    flo, fhi = f(lo), f(hi)
    k=0
    while flo*fhi>0 and k<40:
        hi*=2; fhi=f(hi); k+=1
    if flo*fhi>0: return None
    for _ in range(200):
        mid=(lo+hi)/2; fm=f(mid)
        if abs(fm)<1e-12: return mid*100
        if flo*fm<=0: hi=mid; fhi=fm
        else: lo=mid; flo=fm
    return mid*100

def annuity_pmt(pv, i_pct, n, due="END", fv=0.0):
    i=i_pct/100
    if abs(i)<1e-12: return -(pv+fv)/n
    factor=1 if due=="END" else (1+i)
    return -((pv*(1+i)**n + fv)*i)/(((1+i)**n-1)*factor)

def annuity_pv(pmt, i_pct, n, due="END", fv=0.0):
    i=i_pct/100
    if abs(i)<1e-12: return -(pmt*n+fv)
    factor=1 if due=="END" else (1+i)
    return -(((pmt*factor)*(((1+i)**n-1)/i)+fv)/((1+i)**n))

def annuity_fv(pmt, i_pct, n, due="END", pv=0.0):
    i=i_pct/100
    if abs(i)<1e-12: return -(pv+pmt*n)
    factor=1 if due=="END" else (1+i)
    return -pv*(1+i)**n - pmt*factor*(((1+i)**n -1)/i)

if "watch_mode" not in st.session_state:
    st.session_state.watch_mode=False

c1,c2=st.columns([1.1,1])
with c1:
    if not st.session_state.watch_mode:
        if st.button("⌚ ativar modo smartwatch", type="primary", use_container_width=True):
            st.session_state.watch_mode=True
            st.rerun()
    else:
        if st.button("💻 voltar para modo normal", type="primary", use_container_width=True):
            st.session_state.watch_mode=False
            st.rerun()
with c2:
    st.caption("modo relógio/normal")

st.title("matemática financeira aplicada — v8")
with st.sidebar:
    basis = st.selectbox("base padrão de dias", ["360","365","252"], index=0)

tabs = st.tabs([
    "início","porcentagem e apoio","taxas proporcionais","taxas equivalentes","taxa nominal x efetiva",
    "desconto racional simples","desconto comercial simples","desconto racional composto",
    "desconto comercial composto","séries uniformes","fluxo de caixa irregular"
])

with tabs[0]:
    st.write("estrutura v8 separada por assunto.")
    st.write("- taxas")
    st.write("- descontos")
    st.write("- séries uniformes")
    st.write("- fluxo irregular")

with tabs[1]:
    sub = st.radio("subaba",["aumento/desconto","percentuais sucessivos","taxa real"], horizontal=not st.session_state.watch_mode)
    if sub=="aumento/desconto":
        valor=st.number_input("valor inicial", value=500.0)
        taxa=st.number_input("percentual (%)", value=40.0)
        st.metric("com aumento", money(valor*(1+taxa/100)))
        st.metric("com desconto", money(valor*(1-taxa/100)))
    elif sub=="percentuais sucessivos":
        base=st.number_input("valor inicial", value=100.0)
        seq=st.text_input("taxas separadas por vírgula", value="-50, 100, -20, 30")
        cur=base
        for raw in seq.split(","):
            try: cur*=1+float(raw.strip())/100
            except: pass
        st.metric("valor final", money(cur))
        st.metric("variação total", pct((cur/base-1)*100 if base else 0))
    else:
        modo=st.radio("modo",["achar taxa bruta necessária","achar taxa real"], horizontal=not st.session_state.watch_mode)
        if modo=="achar taxa bruta necessária":
            real=st.number_input("taxa real desejada (%)", value=6.0)
            infl=st.number_input("inflação (%)", value=4.0)
            st.metric("taxa efetiva necessária", pct(gross_required_for_real(real,infl)))
        else:
            gross=st.number_input("rendimento efetivo (%)", value=10.24)
            infl=st.number_input("inflação (%)", value=4.0)
            st.metric("taxa real", pct(rate_real(gross,infl)))

with tabs[2]:
    taxa=st.number_input("taxa de origem (%)", value=2.0)
    de=st.selectbox("de", list(PER_YEAR.keys()), index=3)
    para=st.selectbox("para", list(PER_YEAR.keys()), index=6)
    st.metric("taxa proporcional", pct(taxa*(PER_YEAR[de]/PER_YEAR[para])))

with tabs[3]:
    taxa=st.number_input("taxa efetiva de origem (%)", value=2.0, key="eq")
    de=st.selectbox("de", list(PER_YEAR.keys()), index=3, key="eqd")
    para=st.selectbox("para", list(PER_YEAR.keys()), index=6, key="eqp")
    st.metric("taxa equivalente", pct(equivalent_rate(taxa,de,para)))

with tabs[4]:
    nominal=st.number_input("taxa nominal (%)", value=12.0)
    un=st.selectbox("unidade da taxa nominal", list(PER_YEAR.keys()), index=6)
    cap=st.selectbox("capitalização", list(PER_YEAR.keys()), index=3)
    eff=effective_from_nominal(nominal,un,cap)
    st.metric("taxa efetiva da capitalização", f"{pct(eff)} {cap}")
    st.metric("taxa efetiva anual", pct(annual_effective_from_rate(eff,cap)*100))

with tabs[5]:
    FV=st.number_input("FV", value=65000.0)
    i=st.number_input("taxa i (%)", value=3.0)
    n=st.number_input("prazo n", value=8.0)
    PV=FV/(1+i/100*n); D=FV-PV
    st.metric("PV", money(PV)); st.metric("D", money(D))

with tabs[6]:
    FV=st.number_input("FV", value=65000.0, key="dcs_fv")
    d=st.number_input("taxa d (%)", value=3.0, key="dcs_d")
    n=st.number_input("prazo n", value=8.0, key="dcs_n")
    D=FV*d/100*n; PV=FV-D
    st.metric("D", money(D)); st.metric("PV", money(PV))

with tabs[7]:
    FV=st.number_input("FV", value=12000.0, key="drcf")
    i=st.number_input("taxa i (%)", value=4.56, key="drci")
    n=st.number_input("prazo n", value=5.0, key="drcn")
    PV=FV/((1+i/100)**n); D=FV-PV
    st.metric("PV", money(PV)); st.metric("D", money(D))

with tabs[8]:
    FV=st.number_input("FV", value=65000.0, key="dccf")
    d=st.number_input("taxa d (%)", value=3.0, key="dccd")
    n=st.number_input("prazo n", value=8.0, key="dccn")
    PV=FV*((1-d/100)**n); D=FV-PV
    st.metric("PV", money(PV)); st.metric("D", money(D))

with tabs[9]:
    sub=st.radio("tipo",["postecipada","antecipada","diferida / carência","perpetuidade"], horizontal=not st.session_state.watch_mode)
    if sub in ["postecipada","antecipada"]:
        due="END" if sub=="postecipada" else "BEG"
        alvo=st.selectbox("descobrir",["PMT","PV","FV"])
        i=st.number_input("taxa por período (%)", value=1.8)
        n=st.number_input("número de períodos", value=36.0)
        if alvo=="PMT":
            pv=st.number_input("PV", value=36000.0)
            st.metric("PMT", money(abs(annuity_pmt(pv,i,n,due=due,fv=0.0))))
        elif alvo=="PV":
            pmt=st.number_input("PMT", value=15000.0)
            st.metric("PV", money(abs(annuity_pv(-pmt,i,n,due=due,fv=0.0))))
        else:
            pmt=st.number_input("PMT", value=1000.0)
            st.metric("FV", money(abs(annuity_fv(-pmt,i,n,due=due,pv=0.0))))
    elif sub=="diferida / carência":
        pv=st.number_input("PV hoje", value=20000.0)
        i=st.number_input("taxa por período (%)", value=3.0)
        car=st.number_input("carência", value=2.0)
        n=st.number_input("número de parcelas", value=6.0)
        pv_serie=pv*((1+i/100)**car)
        st.metric("PMT", money(abs(annuity_pmt(pv_serie,i,n,due="END",fv=0.0))))
    else:
        modo=st.radio("modo",["achar PV","achar PMT"], horizontal=not st.session_state.watch_mode)
        i=st.number_input("taxa (%)", value=6.0)
        if modo=="achar PV":
            pmt=st.number_input("PMT", value=12000.0)
            st.metric("PV", money(pmt/(i/100)))
        else:
            pv=st.number_input("PV", value=200000.0)
            st.metric("PMT", money(pv*(i/100)))

with tabs[10]:
    default = pd.DataFrame({"período":[0,1,2,3,4,5,6],"fluxo":[-1200,300,400,400,500,500,500]})
    df = st.data_editor(default, num_rows="dynamic", use_container_width=True)
    taxa=st.number_input("taxa para VPL (%)", value=20.0)
    if len(df)>0:
        df2=df.sort_values("período").reset_index(drop=True)
        maxp=int(df2["período"].max())
        cfs=[0.0]*(maxp+1)
        for _,row in df2.iterrows(): cfs[int(row["período"])] += float(row["fluxo"])
        st.metric("VPL / NPV", money(npv(taxa,cfs)))
        r=irr(cfs)
        st.metric("TIR / IRR", pct(r) if r is not None else "não encontrada")
