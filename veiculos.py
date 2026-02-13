import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
import math

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
if st.button("Calcular"):
    if not st.session_state.cargas:
        st.warning("Adicione ao menos uma carga.")
        st.stop()

    veiculos_testar = [v for v in lista_veiculos if not selecionados or v["nome"] in selecionados]

    df_cargas = pd.DataFrame(st.session_state.cargas)
    vol_total = df_cargas["Volume total (m³)"].sum()
    peso_total = df_cargas["Peso total (kg)"].sum()

    resultados = []
    erros = []
    cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas)

    for v in veiculos_testar:
        if not all(c["Altura (m)"] <= v["altura"] for c in st.session_state.cargas):
            erros.append(f"❌ {v['nome']}: Altura excedida.")
            continue

        if not all(
            ((c["Comprimento (m)"] <= v["comprimento"] and c["Largura (m)"] <= v["largura"]) or
             (c["Largura (m)"] <= v["comprimento"] and c["Comprimento (m)"] <= v["largura"]))
            for c in st.session_state.cargas
        ):
            erros.append(f"❌ {v['nome']}: Item maior que o piso.")
            continue

        cubagem = v["comprimento"] * v["largura"] * v["altura"]

        if vol_total > cubagem:
            erros.append(f"❌ {v['nome']}: Volume excedido.")
            continue

        if peso_total > v["peso_max"]:
            erros.append(f"❌ {v['nome']}: Peso excedido.")
            continue

        if not cabe_no_piso_heuristica(cargas_unitarias, v["comprimento"], v["largura"]):
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

    df_result = pd.DataFrame(resultados).sort_values("Viabilidade (%)", ascending=False).reset_index(drop=True)

    melhor = df_result.loc[0, "Veículo"]

    def highlight_best(row):
        if row["Veículo"] == melhor:
            return ['background-color: #9cff9c'] * len(row)
        return [''] * len(row)

    styled = df_result.style.apply(highlight_best, axis=1)

    # ✅ TABELA PRIMEIRO
    st.subheader("🚛 Veículos Viáveis")
    st.dataframe(styled, use_container_width=True)

    st.markdown(f"### ⭐ Melhor opção: **{melhor}**")

    # ✅ RESTRIÇÕES DEPOIS
    if erros:
        st.subheader("⚠️ Restrições encontradas")
        for e in erros:
            st.warning(e)

    # ============================
    # GRÁFICO 3D
    # ============================
    st.subheader("📊 Viabilidade (3D)")

    fig = go.Figure()

    for i, row in df_result.iterrows():
        fig.add_trace(go.Scatter3d(
            x=[i, i],
            y=[0, 0],
            z=[0, row["Viabilidade (%)"]],
            mode="lines",
            line=dict(width=40, color=row["Viabilidade (%)"], colorscale="Viridis"),
            showlegend=False
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title="Veículo",
                tickvals=list(range(len(df_result))),
                ticktext=df_result["Veículo"]
            ),
            zaxis=dict(title="Viabilidade (%)"),
        ),
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)

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




