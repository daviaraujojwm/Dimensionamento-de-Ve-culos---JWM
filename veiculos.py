import streamlit as st
import pandas as pd
from io import BytesIO



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
# DATAFRAME DE VEÍCULOS (ESSENCIAL)
# ============================
df_veiculos = pd.DataFrame(lista_veiculos)

# cálculo automático da cubagem do veículo
df_veiculos["Capacidade Volume (m³)"] = (
    df_veiculos["largura"]
    * df_veiculos["comprimento"]
    * df_veiculos["altura"]
)

# padroniza nome da coluna usada no cálculo
df_veiculos.rename(columns={"nome": "Veículo"}, inplace=True)

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
todos_nomes = df_veiculos["Veículo"].tolist()

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

# Heurística piso (VERSÃO CORRIGIDA)
def cabe_no_piso_heuristica(cargas_unitarias, veh_comp, veh_larg, veh_alt):

    # ===============================
    # FAST MODE — muitas caixas iguais
    # ===============================
    if len(cargas_unitarias) > 50:

        comp = cargas_unitarias[0]["comp"]
        larg = cargas_unitarias[0]["larg"]
        alt = cargas_unitarias[0]["alt"]

        qtd_comp = int(veh_comp // comp)
        qtd_larg = int(veh_larg // larg)

        caixas_por_camada = qtd_comp * qtd_larg

        if caixas_por_camada == 0:
            return False

        camadas = int(veh_alt // alt)

        capacidade_total = caixas_por_camada * camadas

        return capacidade_total >= len(cargas_unitarias)

    # ===============================
    # modo heurístico original
    # ===============================
    items = sorted(
        cargas_unitarias,
        key=lambda x: x['comp'] * x['larg'],
        reverse=True
    )

    rows = []

    for it in items:
        placed = False

        for comp_i, larg_i in [(it['comp'], it['larg']), (it['larg'], it['comp'])]:

            if comp_i > veh_comp or larg_i > veh_larg:
                continue

            for row in rows:
                if row['used_length'] + comp_i <= veh_comp + 1e-6:

                    total_width = (
                        sum(r['row_width'] for r in rows)
                        - row['row_width']
                        + max(row['row_width'], larg_i)
                    )

                    if total_width <= veh_larg + 1e-6:
                        row['used_length'] += comp_i
                        row['row_width'] = max(row['row_width'], larg_i)
                        placed = True
                        break

            if placed:
                break

            if sum(r['row_width'] for r in rows) + larg_i <= veh_larg + 1e-6:
                rows.append({
                    "used_length": comp_i,
                    "row_width": larg_i
                })
                placed = True
                break

        if not placed:
            return False

    return True


# ============================
# BOTÃO CALCULAR
# ============================
calcular = st.button("🚀 Calcular Dimensionamento")

if calcular:

    if not st.session_state.cargas:
        st.warning("Adicione pelo menos uma carga.")
        st.stop()

    cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas)

    resultados = []

    if selecionados:
        df_testar = df_veiculos[df_veiculos["Veículo"].isin(selecionados)]
    else:
        df_testar = df_veiculos

    volume_total_carga = sum(
        c["comp"] * c["larg"] * c["alt"]
        for c in cargas_unitarias
    )

    peso_total = sum(c["peso"] for c in cargas_unitarias)

    # ============================
    # LOOP VEÍCULOS
    # ============================
    for _, veic in df_testar.iterrows():

            # ============================
            # DADOS DO VEÍCULO
            # ============================
            comp_v = veic["comprimento"]
            larg_v = veic["largura"]
            alt_v  = veic["altura"]
            peso_max = veic["peso_max"]
        
            volume_veiculo = comp_v * larg_v * alt_v
        
            # ============================
            # CONTROLE REAL DE VOLUME
            # ============================
            aproveitamento_volume_real = volume_total_carga / volume_veiculo
        
            if aproveitamento_volume_real > 1:
                continue
        
            aproveitamento_volume = round(aproveitamento_volume_real * 100, 2)
        
            # ============================
            # CONTROLE REAL DE PESO
            # ============================
            peso_aprov_real = (peso_total / peso_max) * 100
        
            if peso_aprov_real > 100:
                continue
        
            peso_aprov = round(peso_aprov_real, 2)
        
            # ============================
            # SIMULAÇÃO SIMPLIFICADA DE EMPILHAMENTO
            # ============================
        
            caixas_total = 0
                
            for carga in cargas_unitarias:
                
                comp_c = carga["comp"]
                larg_c = carga["larg"]
                alt_c  = carga["alt"]
                
                qtd_comprimento = int(comp_v // comp_c)
                qtd_largura     = int(larg_v // larg_c)
                
                caixas_por_camada = qtd_comprimento * qtd_largura
                camadas = int(alt_v // alt_c)
                
                capacidade_total = caixas_por_camada * camadas
                
                if capacidade_total > 0:
                    caixas_total += 1
        
            # ============================
            # HEURÍSTICA FINAL
            # ============================
        
            score = (
                (aproveitamento_volume * 0.5) +
                (peso_aprov * 0.3) +
                (caixas_total * 0.2)
            )
        
            resultados.append({
                "Veículo": veic["Veículo"],
                "Aproveitamento Volume (%)": aproveitamento_volume,
                "Aproveitamento Peso (%)": peso_aprov,
                "Caixas Alocadas": caixas_total,
                "Score": round(score, 2)
        })
    # ============================
    # CRIA DATAFRAME FINAL (FORA DO LOOP)
    # ============================
    if resultados:
        df_result = pd.DataFrame(resultados)

        df_result = df_result.sort_values(
            "Aproveitamento Volume (%)",
            ascending=False
        ).reset_index(drop=True)

        st.session_state.df_result = df_result
    else:
        st.session_state.df_result = pd.DataFrame()
        st.warning("Nenhum veículo comporta as cargas.")


# ============================
# MOSTRAR RESULTADOS
# ============================

if "df_result" in st.session_state and not st.session_state.df_result.empty:

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
    excel = gerar_excel_bytes(
        st.session_state.df_result,
        st.session_state.cargas
    )

    st.download_button(
        "📥 Baixar Excel",
        data=excel,
        file_name="dimensionamento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==========================================================
# 🤖 INTELIGÊNCIA LOGÍSTICA AVANÇADA
# ==========================================================

if "df_result" in st.session_state and not st.session_state.df_result.empty:

    st.markdown("---")
    st.header("🤖 Inteligência Logística Avançada")

    df_ia = st.session_state.df_result.copy()

    def eficiencia_logistica(vol_aprov, peso_aprov):
        ocupacao_media = (vol_aprov + peso_aprov) / 2
        penalidade = max(0, 100 - ocupacao_media) * 0.15
        eficiencia = ocupacao_media - penalidade
        return max(0, round(eficiencia, 2))

    custos_operacionais = {
        "Fiorino": 1.2,
        "Van Utilitário": 1.4,
        "HR Baú": 2.0,
        "HR Aberto": 2.1,
        "Veículo 3/4 Aberto": 3.5,
        "Veículo 3/4 Baú": 3.8,
        "Toco Aberto": 4.5,
        "Toco Baú": 4.8,
        "VUC Baú": 3.0,
        "Truck Aberto": 7.5,
        "Truck Baú": 7.0,
        "Bi-Truck Aberto": 9.0,
        "Bi-Truck Baú": 9.5,
        "Carreta Sider": 10.0,
        "Carreta Wanderleia": 11.0,
        "Carreta Wanderleia Aberta": 12.5,
        "Carreta Wanderleia Sider": 12.0,
        "Carreta Rodo Trem": 15.0,
        "Bitruck Sider": 9.8,
        "Carreta Grade Baixa": 10.5,
        "Wanderleia Carga Seca": 11.5,
    }

    eficiencias = []
    scores = []

    for _, row in df_ia.iterrows():

        vol_aprov = row["Aproveitamento Volume (%)"]
        peso_aprov = row["Aproveitamento Peso (%)"]

        eficiencia = eficiencia_logistica(
            vol_aprov,
            peso_aprov
        )

        custo = custos_operacionais.get(row["Veículo"], 10)

        score = (eficiencia * 0.7) - (custo * 1.3)

        eficiencias.append(eficiencia)
        scores.append(round(score, 2))

    df_ia["Eficiência Logística (%)"] = eficiencias
    df_ia["Score IA"] = scores

    df_ia = df_ia.sort_values("Score IA", ascending=False)

    melhor_ia = df_ia.iloc[0]["Veículo"]

    def highlight_ai(row):
        if row["Veículo"] == melhor_ia:
            return ["background-color: #00E5FF"] * len(row)
        return [""] * len(row)

    st.subheader("🧠 IA — Veículo Ideal Operacional")

    st.dataframe(
        df_ia.style.apply(highlight_ai, axis=1),
        use_container_width=True
    )

    st.success(f"🚀 IA recomenda operacionalmente: **{melhor_ia}**")
# ============================
# SIMULAÇÃO REAL DE EMPILHAMENTO
# ============================

if (
    "df_result" in st.session_state
    and not st.session_state.df_result.empty
    and st.session_state.cargas
):

    st.markdown("---")
    st.header("📦 Simulação Real de Empilhamento")

    melhor = st.session_state.df_result.loc[0, "Veículo"]

    st.write(f"🚛 Veículo simulado: **{melhor}**")

    # cargas expandidas
    cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas)
        
    if not cargas_unitarias:
        st.stop()
        
        primeira = cargas_unitarias[0]
        
        if not all(
            c["comp"] == primeira["comp"] and
            c["larg"] == primeira["larg"] and
            c["alt"] == primeira["alt"]
            for c in cargas_unitarias
        ):
            st.warning("⚠️ Simulação visual disponível apenas para cargas idênticas.")
            st.stop()
        
        comp_c = primeira["comp"]
        larg_c = primeira["larg"]
        alt_c = primeira["alt"]

    # busca veículo segura
    veiculo = next(
        (v for v in lista_veiculos if v["nome"] == melhor),
        None
    )

    if veiculo is None:
        st.error("Veículo não encontrado.")
        st.stop()

    comp_v = veiculo["comprimento"]
    larg_v = veiculo["largura"]
    alt_v = veiculo["altura"]

    caixas_linha = int(comp_v // comp_c)
    caixas_coluna = int(larg_v // larg_c)
    camadas = int(alt_v // alt_c)

    total_caixas = caixas_linha * caixas_coluna * camadas

    st.write(f"📦 Caixas por camada: {caixas_linha * caixas_coluna}")
    st.write(f"📚 Camadas possíveis: {camadas}")
    st.write(f"📦 Capacidade estimada: {total_caixas}")

    st.markdown("### 📐 Ocupação visual")

    linhas = min(caixas_coluna, 12)
    colunas = min(caixas_linha, 30)

    for camada in range(min(camadas, 5)):
        st.markdown(f"**Camada {camada+1}**")
        for _ in range(linhas):
            st.write("🟫 " * colunas)
        st.write("---")
