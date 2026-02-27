import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go


# ============================
# CONFIGURAÇÃO INICIAL
# ============================
st.set_page_config(page_title="Cubagem de Veículos - JWM", layout="wide")

# ============================
# SIDEBAR
# ============================
st.sidebar.title("📘 Instruções de Uso")
st.sidebar.write(
    """
Preencha as dimensões, peso e quantidade do material.
Você pode adicionar várias cargas.
Quando terminar, clique em **Calcular**.

⚠️ Digite os valores em **metros**.
Use vírgula ou ponto para decimais.
"""
)

# ============================
# BASE DE VEÍCULOS
# ============================
lista_veiculos = [
    {"nome": "Fiorino", "largura": 1.000, "comprimento": 1.200, "altura": 1.000, "peso_max": 500},
    {"nome": "Van Utilitário", "largura": 1.000, "comprimento": 1.600, "altura": 1.000, "peso_max": 500},
    {"nome": "HR Baú", "largura": 1.700, "comprimento": 3.000, "altura": 1.900, "peso_max": 1300},
    {"nome": "HR Aberto", "largura": 1.800, "comprimento": 3.000, "altura": 2.000, "peso_max": 1300},
    {"nome": "Veículo 3/4 Aberto", "largura": 2.100, "comprimento": 5.000, "altura": 2.300, "peso_max": 3000},
    {"nome": "Veículo 3/4 Baú", "largura": 2.100, "comprimento": 5.000, "altura": 2.300, "peso_max": 3000},
    {"nome": "Toco Aberto", "largura": 2.200, "comprimento": 6.000, "altura": 2.700, "peso_max": 6000},
    {"nome": "Toco Baú", "largura": 2.200, "comprimento": 6.000, "altura": 2.700, "peso_max": 6000},
    {"nome": "VUC Baú", "largura": 1.800, "comprimento": 3.100, "altura": 2.000, "peso_max": 2500},
    {"nome": "Truck Aberto", "largura": 2.400, "comprimento": 8.000, "altura": 2.800, "peso_max": 12000},
    {"nome": "Truck Baú", "largura": 2.400, "comprimento": 8.000, "altura": 2.800, "peso_max": 12000},
    {"nome": "Bi-Truck Aberto", "largura": 2.400, "comprimento": 10.000, "altura": 2.800, "peso_max": 17000},
    {"nome": "Bi-Truck Baú", "largura": 2.400, "comprimento": 10.000, "altura": 2.800, "peso_max": 17000},
    {"nome": "Carreta Sider", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 24000},
    {"nome": "Carreta Wanderleia", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 27000},
    {"nome": "Carreta Wanderleia Aberta", "largura": 2.600, "comprimento": 18.150, "altura": 2.900, "peso_max": 46000},
    {"nome": "Carreta Wanderleia Sider", "largura": 2.600, "comprimento": 15.200, "altura": 2.800, "peso_max": 41500},
    {"nome": "Carreta Rodo Trem", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 74000},
    {"nome": "Bitruck Sider", "largura": 2.400, "comprimento": 10.000, "altura": 2.700, "peso_max": 18000},
    {"nome": "Carreta Grade Baixa", "largura": 2.400, "comprimento": 12.400, "altura": 2.700, "peso_max": 24000},
    {"nome": "Wanderleia Carga Seca", "largura": 2.400, "comprimento": 14.400, "altura": 2.700, "peso_max": 27000}
]

# ============================
# SESSION STATE
# ============================
if "cargas" not in st.session_state:
    st.session_state.cargas = []
if "to_delete" not in st.session_state:
    st.session_state.to_delete = None
if "clear_inputs" not in st.session_state:
    st.session_state.clear_inputs = False

# ============================
# RESET DE INPUTS
# ============================
if st.session_state.clear_inputs:
    st.session_state["comp"] = ""
    st.session_state["larg"] = ""
    st.session_state["alt"] = ""
    st.session_state["peso"] = ""
    st.session_state["qtd"] = 1
    st.session_state.clear_inputs = False

# ============================
# TÍTULO
# ============================
col1, col2 = st.columns([6, 1])
with col1:
    st.title("🚚 Dimensionamento de Veículos - JWM")
with col2:
    try:
        st.image("JWM.png", width=80)
    except:
        pass

# ============================
# INPUTS CARGA
# ============================
st.subheader("📦 Adicionar carga")

col1, col2, col3, col4 = st.columns(4)

with col1:
    comp = st.text_input("Comprimento (m):", key="comp")
with col2:
    larg = st.text_input("Largura (m):", key="larg")
with col3:
    alt = st.text_input("Altura (m):", key="alt")
with col4:
    peso = st.text_input("Peso unitário (kg):", key="peso")

qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1, key="qtd")

# ============================
# FUNÇÃO PARSE
# ============================
def parse_input(v, name="valor"):
    if v is None or str(v).strip() == "":
        raise ValueError(f"{name} vazio.")
    v = str(v).replace(",", ".")
    try:
        n = float(v)
        if n <= 0:
            raise ValueError(f"{name} deve ser maior que zero.")
        return n
    except:
        raise ValueError(f"{name} inválido.")

# ============================
# ADICIONAR CARGA
# ============================
if st.button("➕ Adicionar carga"):
    try:
        c = parse_input(comp, "Comprimento")
        l = parse_input(larg, "Largura")
        a = parse_input(alt, "Altura")
        p = parse_input(peso, "Peso unitário (kg)")
        q = int(qtd)

        vol_unit = c * l * a
        peso_total = p * q

        st.session_state.cargas.append({
            "Comprimento (m)": c,
            "Largura (m)": l,
            "Altura (m)": a,
            "Peso unitário (kg)": p,
            "Quantidade": q,
            "Volume total (m³)": vol_unit * q,
            "Peso total (kg)": peso_total
        })

        st.session_state.clear_inputs = True
        st.rerun()

    except Exception as e:
        st.error(f"Erro ao adicionar carga: {e}")

# ============================
# LISTA DE CARGAS
# ============================
if st.session_state.cargas:
    st.subheader("📋 Cargas adicionadas")

    for i, carga in enumerate(st.session_state.cargas):
        col1, col2 = st.columns([9, 1])
        with col1:
            st.write(
                f"**Carga {i+1}:** {carga['Quantidade']} unid • "
                f"{carga['Comprimento (m)']}m × {carga['Largura (m)']}m × {carga['Altura (m)']}m • "
                f"Peso total: {carga['Peso total (kg)']} kg • Volume: {carga['Volume total (m³)']:.3f} m³"
            )

        with col2:
            if st.button("❌", key=f"delete_{i}"):
                st.session_state.to_delete = i

    if st.session_state.to_delete is not None:
        del st.session_state.cargas[st.session_state.to_delete]
        st.session_state.to_delete = None
        st.rerun()

    if st.button("🧹 Limpar todas as cargas"):
        st.session_state.cargas = []
        st.rerun()

else:
    st.info("Nenhuma carga adicionada ainda.")

# ============================
# SELEÇÃO DE VEÍCULOS
# ============================
todos_nomes = [v["nome"] for v in lista_veiculos]

selecionados = st.multiselect(
    "🚛 Selecione veículos específicos (ou deixe vazio para testar todos):",
    todos_nomes
)

# ============================
# AUXILIARES
# ============================
def expand_cargas_unitarias(cargas):
    lista = []
    for c in cargas:
        for _ in range(c["Quantidade"]):
            lista.append({
                "comp": c["Comprimento (m)"],
                "larg": c["Largura (m)"],
                "alt": c["Altura (m)"],
                "peso": c["Peso unitário (kg)"],
            })
    return lista

def gerar_excel_bytes(df_result, cargas):
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df_result.to_excel(writer, index=False, sheet_name="Resultado")
        pd.DataFrame(cargas).to_excel(writer, index=False, sheet_name="Cargas")
    return out.getvalue()

# Heurística piso
def cabe_no_piso_heuristica(cargas_unitarias, veh_comp, veh_larg):
    items = sorted(cargas_unitarias, key=lambda x: x['comp'] * x['larg'], reverse=True)
    rows = []
    for it in items:
        placed = False
        for comp_i, larg_i in [(it['comp'], it['larg']), (it['larg'], it['comp'])]:
            if comp_i > veh_comp or larg_i > veh_larg:
                continue
            for row in rows:
                if row['used_length'] + comp_i <= veh_comp:
                    total_width = sum(r['row_width'] for r in rows) - row['row_width'] + max(row['row_width'], larg_i)
                    if total_width <= veh_larg:
                        row['used_length'] += comp_i
                        row['row_width'] = max(row['row_width'], larg_i)
                        placed = True
                        break
            if placed:
                break
            if sum(r['row_width'] for r in rows) + larg_i <= veh_larg:
                rows.append({"used_length": comp_i, "row_width": larg_i})
                placed = True
                break
        if not placed:
            return False
    return True

# ============================
# BOTÃO CALCULAR
# ============================
calcular = st.button("Calcular")

if calcular:

    # valida cargas
    if not st.session_state.cargas:
        st.warning("Adicione ao menos uma carga.")
        st.stop()

    veiculos_testar = [
        v for v in lista_veiculos
        if not selecionados or v["nome"] in selecionados
    ]

    df_cargas = pd.DataFrame(st.session_state.cargas)

    if df_cargas.empty:
        st.warning("Nenhuma carga válida.")
        st.stop()

    vol_total = df_cargas["Volume total (m³)"].sum()
    peso_total = df_cargas["Peso total (kg)"].sum()

    resultados = []
    erros = []

    cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas)

    # ============================
    # LOOP VEÍCULOS
    # ============================
    for v in veiculos_testar:

        # valida altura
        if not all(c["Altura (m)"] <= v["altura"] for c in st.session_state.cargas):
            erros.append(f"❌ {v['nome']}: Altura excedida.")
            continue

        # valida piso
        if not all(
            ((c["Comprimento (m)"] <= v["comprimento"] and c["Largura (m)"] <= v["largura"]) or
             (c["Largura (m)"] <= v["comprimento"] and c["Comprimento (m)"] <= v["largura"]))
            for c in st.session_state.cargas
        ):
            erros.append(f"❌ {v['nome']}: Item maior que o piso.")
            continue

        cubagem = v["comprimento"] * v["largura"] * v["altura"]

        if peso_total > v["peso_max"]:
            erros.append(f"❌ {v['nome']}: Peso excedido.")
            continue

        if not cabe_no_piso_heuristica(
            cargas_unitarias,
            v["comprimento"],
            v["largura"]
        ):
            erros.append(f"❌ {v['nome']}: Não cabe no piso.")
            continue

        aproveitamento_vol = (vol_total / cubagem) * 100
        aproveitamento_peso = (peso_total / v["peso_max"]) * 100
        viabilidade = (aproveitamento_vol * 0.6) + (aproveitamento_peso * 0.4)

        resultados.append({
            "Veículo": v["nome"],
            "Cubagem (m³)": round(cubagem, 3),
            "Peso Máx (kg)": v["peso_max"],
            "Volume Total (m³)": round(vol_total, 3),
            "Peso Total (kg)": round(peso_total, 3),
            "Aproveitamento Volume (%)": round(aproveitamento_vol, 2),
            "Aproveitamento Peso (%)": round(aproveitamento_peso, 2),
            "Viabilidade (%)": round(viabilidade, 2)
        })

    if not resultados:
        st.error("Nenhum veículo comporta as cargas.")
        st.stop()

    # dataframe final
    df_result = (
        pd.DataFrame(resultados)
        .sort_values("Viabilidade (%)", ascending=False)
        .reset_index(drop=True)
    )

    # salva sessão
    st.session_state.df_result = df_result

# ============================
# MOSTRAR RESULTADOS
# ============================
if "df_result" in st.session_state:

    df_result = st.session_state.df_result
    melhor = df_result.loc[0, "Veículo"]

    def highlight_best(row):
        if row["Veículo"] == melhor:
            return ['background-color: #28FF77'] * len(row)
        return [''] * len(row)

    st.subheader("🚛 Veículos Viáveis")
    st.dataframe(
        df_result.style.apply(highlight_best, axis=1),
        use_container_width=True
    )

    st.markdown(f"### ⭐ Melhor opção: **{melhor}**")

    # ============================
    # DOWNLOAD EXCEL
    # ============================
    excel = gerar_excel_bytes(df_result, st.session_state.cargas)

    st.download_button(
        "📥 Baixar Excel",
        data=excel,
        file_name="dimensionamento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==========================================================
# 🤖 INTELIGÊNCIA LOGÍSTICA AVANÇADA
# ==========================================================

st.markdown("---")
st.header("🤖 Inteligência Logística Avançada")

def eficiencia_logistica(vol_aprov, peso_aprov):
    ocupacao_media = (vol_aprov + peso_aprov) / 2
    penalidade = max(0, 100 - ocupacao_media) * 0.15
    eficiencia = ocupacao_media - penalidade
    return max(0, round(eficiencia, 2))

custos_operacionais = {
    "Fiorino": 1.2, "Van Utilitário": 1.4,
    "HR Baú": 2.0, "HR Aberto": 2.0,
    "Veículo 3/4 Aberto": 3.0, "Veículo 3/4 Baú": 3.2,
    "Toco Aberto": 4.5, "Toco Baú": 4.8,
    "VUC Baú": 3.5,
    "Truck Aberto": 6.5, "Truck Baú": 7.0,
    "Bi-Truck Aberto": 8.0, "Bi-Truck Baú": 8.5,
    "Carreta Sider": 10.0,
    "Carreta Wanderleia": 11.0,
    "Carreta Wanderleia Aberta": 13.0,
    "Carreta Wanderleia Sider": 12.5,
    "Carreta Rodo Trem": 18.0,
    "Bitruck Sider": 9.0,
    "Carreta Grade Baixa": 11.5,
    "Wanderleia Carga Seca": 10.5,
}

# ============================
# IA VEÍCULO IDEAL
# ============================

if "df_result" in st.session_state:

    df_ia = st.session_state.df_result.copy()

    if not df_ia.empty:

        eficiencias = []
        scores = []

        for _, row in df_ia.iterrows():

            eficiencia = eficiencia_logistica(
                row["Aproveitamento Volume (%)"],
                row["Aproveitamento Peso (%)"]
            )

            custo = custos_operacionais.get(row["Veículo"], 10)
            score = (eficiencia * 0.7) - (custo * 1.3)

            eficiencias.append(eficiencia)
            scores.append(round(score, 2))

        df_ia["Eficiência Logística (%)"] = eficiencias
        df_ia["Score IA"] = scores

        df_ia = df_ia.sort_values("Score IA", ascending=False)

        melhor_ia = df_ia.iloc[0]["Veículo"]

        st.subheader("🧠 IA — Veículo Ideal Operacional")

        def highlight_ai(row):
            if row["Veículo"] == melhor_ia:
                return ["background-color: #00E5FF"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_ia.style.apply(highlight_ai, axis=1),
            use_container_width=True
        )

        st.success(f"🚀 IA recomenda operacionalmente: **{melhor_ia}**")

# ============================
# 📦 SIMULAÇÃO DE OCUPAÇÃO
# ============================

if "df_result" in st.session_state:

    st.subheader("📦 Simulação de Ocupação do Veículo")

    melhor = st.session_state.df_result.iloc[0]

    ocupacao = melhor["Aproveitamento Volume (%)"]

    fig = go.Figure()

    # Base do caminhão (baú)
    fig.add_trace(go.Mesh3d(
        x=[0,10,10,0,0,10,10,0],
        y=[0,0,4,4,0,0,4,4],
        z=[0,0,0,0,5,5,5,5],
        opacity=0.15,
        color="gray",
        name="Baú"
    ))

    # Volume ocupado
    altura_ocupada = 5 * (ocupacao / 100)

    fig.add_trace(go.Mesh3d(
        x=[0,10,10,0,0,10,10,0],
        y=[0,0,4,4,0,0,4,4],
        z=[0,0,0,0,altura_ocupada,altura_ocupada,altura_ocupada,altura_ocupada],
        opacity=0.7,
        color="green",
        name="Carga"
    ))

    fig.update_layout(
        scene=dict(
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_title="Ocupação (%)"
        ),
        height=500,
        margin=dict(l=0, r=0, b=0, t=30)
    )

    st.plotly_chart(fig, use_container_width=True)
