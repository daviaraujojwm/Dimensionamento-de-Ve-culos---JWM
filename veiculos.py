import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go

# ===== CONFIGURAÇÃO INICIAL =====
st.set_page_config(page_title="Cubagem de Veículos - JWM", layout="wide")

# ===== SIDEBAR =====
st.sidebar.title("📘 Instruções de Uso")
st.sidebar.write("""
Preencha as dimensões, peso e quantidade do material.
Você pode adicionar várias cargas.
Quando terminar, clique em **Calcular**.

⚠️Digite os valores em **metros**.
Use vírgula ou ponto para decimais.

🌐 [Acesse nossa frota JWM](https://jwmlogistica.com.br/frota/)
""")

# ===== LAYOUT PRINCIPAL =====
col1, col2 = st.columns([6, 1])
with col1:
    st.title("🚚 Dimensionamento de Veículos - JWM")
with col2:
    try:
        st.image("JWM.png", width=80)
    except Exception:
        st.warning("⚠️ Logo não carregada. Coloque o arquivo 'JWM.png' na mesma pasta do script.")

# ===== BASE DE VEÍCULOS =====
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
    {"nome": "Carreta Wandeleia Sider", "largura": 2.600, "comprimento": 15.200, "altura": 2.800, "peso_max": 41500},
    {"nome": "Carreta Rodo Trem", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 74000},
    {"nome": "Bitruck Sider", "largura": 2.400, "comprimento": 10.000, "altura": 2.700, "peso_max": 18000},
    {"nome": "Carreta Grade Baixa", "largura": 2.400, "comprimento": 12.400, "altura": 2.700, "peso_max": 24000},
    {"nome": "Wanderleia Carga Seca", "largura": 2.400, "comprimento": 14.400, "altura": 2.700, "peso_max": 27000}
]

# ===== ESTADO =====
if "cargas" not in st.session_state:
    st.session_state.cargas = []

# ===== INPUTS =====
st.subheader("📦 Adicionar carga")
col1, col2, col3, col4 = st.columns(4)
with col1:
    comp = st.text_input("Comprimento (m):", key="comp_input")
with col2:
    larg = st.text_input("Largura (m):", key="larg_input")
with col3:
    alt = st.text_input("Altura (m):", key="alt_input")
with col4:
    peso = st.text_input("Peso unitário (kg):", key="peso_input")
quantidade = st.number_input("Quantidade:", min_value=1, value=1, step=1, key="qtd_input")

# ===== FUNÇÕES =====
def parse_input(v):
    if not v or str(v).strip() == "":
        raise ValueError("Campo vazio ou inválido.")
    v = str(v).replace(",", ".")
    try:
        return float(v)
    except:
        raise ValueError("Digite apenas números.")

def gerar_excel_bytes(df_result, cargas):
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df_result.to_excel(writer, index=False, sheet_name="Veículos Viáveis")
        pd.DataFrame(cargas).to_excel(writer, index=False, sheet_name="Cargas")
    return out.getvalue()

# ===== ADICIONAR CARGA =====
if st.button("➕ Adicionar carga"):
    try:
        c, l, a, p = map(parse_input, [comp, larg, alt, peso])
        if min(c, l, a, p) <= 0:
            st.error("Os valores devem ser maiores que zero.")
        else:
            vol_unit = c * l * a
            vol_total = vol_unit * quantidade
            peso_total = p * quantidade
            st.session_state.cargas.append({
                "Comprimento (m)": c,
                "Largura (m)": l,
                "Altura (m)": a,
                "Peso unitário (kg)": p,
                "Quantidade": quantidade,
                "Volume total (m³)": vol_total,
                "Peso total (kg)": peso_total
            })
            st.success("Carga adicionada ✅")
    except Exception as e:
        st.error(f"Erro: {e}")

# ===== EXIBIR CARGAS =====
if st.session_state.cargas:
    st.subheader("📋 Cargas adicionadas")
    for i, carga in enumerate(st.session_state.cargas):
        with st.container():
            col1, col2 = st.columns([9, 1])
            with col1:
                st.write(
                    f"**Carga {i+1}:** {carga['Quantidade']} unid. | "
                    f"{carga['Comprimento (m)']}m × {carga['Largura (m)']}m × {carga['Altura (m)']}m | "
                    f"Peso total: {carga['Peso total (kg)']} kg"
                )
            with col2:
                if st.button("❌", key=f"excluir_{i}"):
                    del st.session_state.cargas[i]
                    st.rerun()

    if st.button("🧹 Limpar todas as cargas"):
        st.session_state.cargas = []
        st.success("Todas as cargas foram removidas!")
else:
    st.info("Nenhuma carga adicionada ainda.")

# ===== SELEÇÃO DE VEÍCULOS =====
todos_nomes = [v["nome"] for v in lista_veiculos]
selecionados = st.multiselect(
    "🚛 Selecione veículos específicos (ou deixe em branco para testar todos):",
    todos_nomes
)

# ===== CÁLCULO =====
if st.button("Calcular"):
    if not st.session_state.cargas:
        st.warning("Adicione ao menos uma carga antes de calcular.")
        st.stop()

    veiculos_testar = [v for v in lista_veiculos if not selecionados or v["nome"] in selecionados]

    df_cargas = pd.DataFrame(st.session_state.cargas)
    vol_total = df_cargas["Volume total (m³)"].sum()
    peso_total = df_cargas["Peso total (kg)"].sum()

    resultados, erros = [], []

    for v in veiculos_testar:
        comp_ok = all(c["Comprimento (m)"] <= v["comprimento"] for c in st.session_state.cargas)
        larg_ok = all(c["Largura (m)"] <= v["largura"] for c in st.session_state.cargas)
        alt_ok = all(c["Altura (m)"] <= v["altura"] for c in st.session_state.cargas)
        peso_ok = peso_total <= v["peso_max"]

        if not comp_ok or not larg_ok or not alt_ok:
            msg = []
            if not comp_ok: msg.append("Comprimento excede")
            if not larg_ok: msg.append("Largura excede")
            if not alt_ok: msg.append("Altura excede")
            erros.append(f"❌ {v['nome']}: {'; '.join(msg)}")
            continue

        cubagem = v["comprimento"] * v["largura"] * v["altura"]
        if vol_total > cubagem or not peso_ok:
            msg = []
            if vol_total > cubagem: msg.append("Volume excedido")
            if not peso_ok: msg.append("Peso excedido")
            erros.append(f"❌ {v['nome']}: {'; '.join(msg)}")
            continue

        aproveitamento_vol = (vol_total / cubagem) * 100
        aproveitamento_peso = (peso_total / v["peso_max"]) * 100
        viabilidade = (aproveitamento_vol * 0.6) + (aproveitamento_peso * 0.4)

        resultados.append({
            "Veículo": v["nome"],
            "Cubagem Veículo (m³)": round(cubagem, 2),
            "Peso Máx (kg)": v["peso_max"],
            "Volume Total (m³)": round(vol_total, 2),
            "Peso Total (kg)": round(peso_total, 2),
            "Aproveitamento Volume (%)": round(aproveitamento_vol, 2),
            "Aproveitamento Peso (%)": round(aproveitamento_peso, 2),
            "Viabilidade (%)": round(viabilidade, 2),
        })

    if erros:
        st.subheader("🔍 Restrições encontradas")
        for e in erros:
            st.warning(e)

    if not resultados:
        st.error("🚫 Nenhum veículo comporta as cargas informadas.")
        st.stop()

    df_result = pd.DataFrame(resultados).sort_values("Viabilidade (%)", ascending=False).reset_index(drop=True)
    melhor = df_result.loc[0, "Veículo"]

    st.subheader("🚛 Veículos Viáveis")
    st.dataframe(
        df_result.style.apply(
            lambda row: ['background-color: lightgreen; font-weight: bold;' if row["Veículo"] == melhor else '' for _ in row],
            axis=1
        ),
        use_container_width=True
    )

    st.markdown(
        f"### ⭐ **Melhor opção:** <span style='color:green; font-weight:bold;'>{melhor}</span>",
        unsafe_allow_html=True
    )

    # ===== GRÁFICO 3D SEM POSSIBILIDADE DE ERRO =====
    st.subheader("📊 Gráfico 3D de Viabilidade dos Veículos")

    fig3d = go.Figure()

    for i, row in df_result.iterrows():
        fig3d.add_trace(go.Scatter3d(
            x=[i, i],
            y=[0, 0],
            z=[0, row["Viabilidade (%)"]],
            mode="lines",
            line=dict(width=40, color=row["Viabilidade (%)"], colorscale="Viridis"),
            name=row["Veículo"],
        ))

    melhor_idx = 0
    melhor_viab = df_result.loc[0, "Viabilidade (%)"]

    fig3d.add_trace(go.Scatter3d(
        x=[melhor_idx],
        y=[0],
        z=[melhor_viab + 2],
        mode="text",
        text=["⭐"],
        textfont=dict(size=22, color="gold"),
        hoverinfo="skip",
    ))

    fig3d.update_layout(
        scene=dict(
            xaxis=dict(
                title="Veículo",
                tickvals=list(range(len(df_result))),
                ticktext=df_result["Veículo"],
            ),
            yaxis=dict(title=""),
            zaxis=dict(title="Viabilidade (%)"),
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)),
        ),
        height=650,
        margin=dict(l=0, r=0, b=0, t=50),
    )

    st.plotly_chart(fig3d, use_container_width=True)

    # ===== DOWNLOAD =====
    excel_bytes = gerar_excel_bytes(df_result, st.session_state.cargas)
    st.download_button(
        label="📥 Baixar resultado em Excel",
        data=excel_bytes,
        file_name="resultado_cubagem.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
