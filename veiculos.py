import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Cubagem de Veículos", layout="wide")

# ===== SIDEBAR =====
st.sidebar.title("Instruções")
st.sidebar.write("""
Preencha as dimensões, peso e quantidade do material.  
Você pode adicionar várias cargas.  
Quando terminar, clique em **Calcular**.\n
⚠️ Digite os valores em **metros**.\n
Lembrando que são três casas decimais para preencher os parâmetros da carga.                 
""")
st.sidebar.write("Site JWM Nossa Frota: [👉Clique aqui](https://jwmlogistica.com.br/frota/)")

# ===== Layout com título =====
col1, col2 = st.columns([6, 1])
with col1:
    st.title("🚚 Dimensionamento de Veículos - JWM")
with col2:
    try:
        st.image("JWM.png", width=80)
    except Exception:
        st.warning("⚠️ Logo não carregada. Verifique se o arquivo 'JWM.png' está presente.")

# ===== Base de veículos =====
lista_veiculos = [
    {"nome": "Fiorino", "largura": 1.000, "status": "Furgão pequeno", "comprimento": 1.500, "altura": 1.000, "peso_max": 500},
    {"nome": "Van Utilitário", "largura": 1.000, "comprimento": 1.600, "altura": 1.000, "peso_max": 500},
    {"nome": "(HR Baú)", "largura": 1.700, "status": "Caminhonete fechada", "comprimento": 3.000, "altura": 1.900, "peso_max": 1300},
    {"nome": "(HR Aberto)", "largura": 1.800, "status": "Caminhonete Aberta", "comprimento": 3.000, "altura": 2.000, "peso_max": 1300},
    {"nome": "Veículo 3/4 Aberto", "largura": 2.100, "status": "Leve 3/4 Aberto",  "comprimento": 5.000, "altura": 2.300, "peso_max": 3000},
    {"nome": "Veículo 3/4 Baú", "largura": 2.100, "status": "Leve 3/4 Baú", "comprimento": 5.000, "altura": 2.300, "peso_max": 3000},
    {"nome": "Veículo Toco Aberto", "largura": 2.200, "status": "Toco Aberto", "comprimento": 6.000, "altura": 2.700, "peso_max": 6000},
    {"nome": "Veículo Toco Baú", "largura": 2.200, "status": "Toco Baú", "comprimento": 6.000, "altura": 2.700, "peso_max": 6000},
    {"nome": "Vuc Baú", "largura": 1.800, "status": "Vuc Baú Simples", "comprimento": 3.100, "altura": 2.000, "peso_max": 2500},
    {"nome": "Caminhão Truck Aberto", "largura": 2.400, "status": "Truck + Metragem (7M; 7.5M; 8M)", "comprimento": 8.000, "altura": 2.800, "peso_max": 12000},
    {"nome": "Caminhão Truck Baú", "largura": 2.400, "status": "Truck + Metragem (7M; 7.5M; 8M)", "comprimento": 8.000, "altura": 2.800, "peso_max": 12000},
    {"nome": "Combinado (Caminhão+Bi-truck) Aberto", "largura": 2.400, "status": "Bi-Truck Aberto", "comprimento": 10.000, "altura": 2.800, "peso_max": 17000},
    {"nome": "Combinado (Caminhão+Bi-truck) Baú", "largura": 2.400, "status": "Bi-Truck Baú", "comprimento": 10.000, "altura": 2.800, "peso_max": 17000},
    {"nome": "Carreta GNV", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 24000},
    {"nome": "Carreta Sider", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 24000},
    {"nome": "Carreta Wanderleia", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 27000},
    {"nome": "Carreta Wanderleia Aberta", "largura": 2.600, "status": "Carreta Aberta 3 eixos", "comprimento": 18.150, "altura": 2.900, "peso_max": 46000},
    {"nome": "Carreta Wandeleia Sider", "largura": 2.600, "status": "Carreta Sider 3 eixos", "comprimento": 15.200, "altura": 2.800, "peso_max": 41500},
    {"nome": "Carreta Rodo Trem", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 74000},
    {"nome": "Bitruck Sider", "largura": 2.400, "comprimento": 10.000, "altura": 2.700, "peso_max": 18000},
    {"nome": "Carreta Grade Baixa", "largura": 2.400, "comprimento": 12.400, "altura": 2.700, "peso_max": 24000},
    {"nome": "Wanderleia Carga Seca", "largura": 2.400, "comprimento": 14.400, "altura": 2.700, "peso_max": 27000}
]

# ===== Estado da sessão =====
if "cargas" not in st.session_state:
    st.session_state.cargas = []

for campo in ["comp_input", "larg_input", "alt_input", "peso_input"]:
    if campo not in st.session_state:
        st.session_state[campo] = ""

# ===== Entrada do usuário =====
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

quantidade = st.number_input("Quantidade:", min_value=1, value=1, step=1)

# ===== Função para tratar entradas =====
def parse_input(value):
    """Converte texto para float, aceitando vírgula ou ponto."""
    if not value or value.strip() == "":
        raise ValueError("Campo vazio")
    return float(value.replace(",", ".").strip())

# ===== Adicionar carga =====
def adicionar_carga():
    try:
        comp = parse_input(st.session_state.comp_input)
        larg = parse_input(st.session_state.larg_input)
        alt = parse_input(st.session_state.alt_input)
        peso = parse_input(st.session_state.peso_input)

        volume_unitario = comp * larg * alt
        peso_total = peso * quantidade
        volume_total = volume_unitario * quantidade

        st.session_state.cargas.append({
            "Comprimento (m)": comp,
            "Largura (m)": larg,
            "Altura (m)": alt,
            "Peso unitário (kg)": peso,
            "Quantidade": quantidade,
            "Peso total (kg)": peso_total,
            "Volume total (m³)": volume_total
        })

        # Limpa os campos
        st.session_state.comp_input = ""
        st.session_state.larg_input = ""
        st.session_state.alt_input = ""
        st.session_state.peso_input = ""

    except ValueError:
        st.session_state.erro_carga = True

st.button("➕ Adicionar carga", on_click=adicionar_carga)

if st.session_state.get("erro_carga"):
    st.error("⚠️ Preencha todos os campos numéricos corretamente! Use vírgula ou ponto para decimais.")
    st.session_state.erro_carga = False

# ===== Gerenciamento de cargas =====
def remover_carga(index):
    st.session_state.cargas.pop(index)

def limpar_cargas():
    st.session_state.cargas = []

if st.session_state.cargas:
    st.subheader("📋 Cargas adicionadas")
    df_cargas = pd.DataFrame(st.session_state.cargas)
    st.dataframe(df_cargas, use_container_width=True)

    for i, carga in enumerate(st.session_state.cargas):
        st.button(f"❌ Remover carga {i+1}", key=f"remover_{i}", on_click=remover_carga, args=(i,))

    st.button("🗑️ Limpar todas as cargas", on_click=limpar_cargas)

# ===== Cálculo =====
opcoes = sorted({v["nome"].strip() for v in lista_veiculos})
filtro = st.multiselect("Filtrar veículos específicos (opcional):", opcoes)

if st.button("Calcular"):
    if not st.session_state.cargas:
        st.warning("Adicione pelo menos uma carga antes de calcular.")
    else:
        aproveitamento = 0.90
        veiculos_para_olhar = lista_veiculos if not filtro else [v for v in lista_veiculos if v["nome"] in filtro]

        volume_total_cargas = sum(c["Volume total (m³)"] for c in st.session_state.cargas)
        peso_total_cargas = sum(c["Peso total (kg)"] for c in st.session_state.cargas)
        quantidade_total = sum(c["Quantidade"] for c in st.session_state.cargas)

        # ===== RESUMO DAS CARGAS =====
        st.subheader("📊 Resumo Geral das Cargas")
        df_resumo = pd.DataFrame([{
            "Quantidade total": quantidade_total,
            "Peso total (kg)": round(peso_total_cargas, 2),
            "Volume total (m³)": round(volume_total_cargas, 2)
        }])
        st.dataframe(df_resumo.style.set_properties(**{
            "background-color": "#e0f7fa",
            "color": "black",
            "font-weight": "bold"
        }), use_container_width=True)

        veiculos_viaveis = []
        for veiculo in veiculos_para_olhar:
            cubagem_veiculo = veiculo["comprimento"] * veiculo["largura"] * veiculo["altura"]
            limite_volume = cubagem_veiculo * aproveitamento

            # ======= Tratativa aprimorada =======
            # Verifica compatibilidade física e de peso
            comp_max = all(c["Comprimento (m)"] <= veiculo["comprimento"] for c in st.session_state.cargas)
            larg_max = all(c["Largura (m)"] <= veiculo["largura"] for c in st.session_state.cargas)
            alt_max = all(c["Altura (m)"] <= veiculo["altura"] for c in st.session_state.cargas)

            if not (comp_max and larg_max and alt_max):
                continue  # pular veículos menores que as dimensões das cargas

            if (volume_total_cargas <= limite_volume) and (peso_total_cargas <= veiculo["peso_max"]):
                aproveitamento_vol = volume_total_cargas / cubagem_veiculo
                aproveitamento_peso = peso_total_cargas / veiculo["peso_max"]

                sobra_peso = veiculo["peso_max"] - peso_total_cargas
                sobra_volume = limite_volume - volume_total_cargas

                # Pondera peso e volume — melhora precisão
                viabilidade = min(100, round(((aproveitamento_vol * 0.6) + (aproveitamento_peso * 0.4)) * 100, 2))

                # Calcular quantas unidades comporta
                unidades_volume = limite_volume // (volume_total_cargas / quantidade_total) if quantidade_total > 0 else 0
                unidades_peso = veiculo["peso_max"] // (peso_total_cargas / quantidade_total) if quantidade_total > 0 else 0
                quantidade_comporta = int(min(unidades_volume, unidades_peso))

                observacao = "✅ Leva toda a carga" if quantidade_comporta >= quantidade_total else "❌ Precisa mais viagens"

                veiculos_viaveis.append({
                    "Veículo": veiculo["nome"],
                    "Cubagem Veículo (m³)": round(cubagem_veiculo, 2),
                    "Parâmetros: C, L, A, PM": f'{veiculo["comprimento"]}m x {veiculo["largura"]}m x {veiculo["altura"]}m | {veiculo["peso_max"]}kg',
                    "Peso Máx Veículo (kg)": veiculo["peso_max"],
                    "Quantidade total": quantidade_total,
                    "Quantidade que comporta": quantidade_comporta,
                    "Peso total (kg)": round(peso_total_cargas, 2),
                    "Volume total (m³)": round(volume_total_cargas, 2),
                    "Aproveitamento (%)": round(aproveitamento_vol * 100, 2),
                    "Sobra de peso (kg)": round(sobra_peso, 2),
                    "Sobra de volume (m³)": round(sobra_volume, 2),
                    "Viabilidade (%)": viabilidade,
                    "Observação": observacao
                })

        if veiculos_viaveis:
            df_veiculos = pd.DataFrame(veiculos_viaveis).sort_values(by="Viabilidade (%)", ascending=False).reset_index(drop=True)

            # Adiciona estrela no mais viável
            df_veiculos.loc[0, "Veículo"] = "⭐ " + df_veiculos.loc[0, "Veículo"]

            # ===== Estilo condicional =====
            def highlight_rows(row):
                styles = [''] * len(row)
                if row.name == 0:
                    styles = ['background-color: lightgreen; font-weight: bold'] * len(row)
                if row["Quantidade que comporta"] < row["Quantidade total"]:
                    styles = ['background-color: #ffcccc'] * len(row)
                return styles

            st.subheader("🚛 Veículos viáveis (ordenados por viabilidade)")
            st.dataframe(df_veiculos.style.apply(highlight_rows, axis=1), use_container_width=True)

            def gerar_excel(df_veiculos):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_veiculos.to_excel(writer, index=False, sheet_name="Veículos Viáveis")
                return output.getvalue()

            excel_bytes = gerar_excel(df_veiculos)
            st.download_button(
                label="📥 Baixar Excel (Veículos Viáveis)",
                data=excel_bytes,
                file_name="veiculos_viaveis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("🚫 Nenhum veículo comporta todas as cargas.")
