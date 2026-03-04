import streamlit as st
import pandas as pd
import random
from io import BytesIO
import plotly.graph_objects as go


# ============================
# CONFIGURAÇÃO INICIAL
# ============================
st.set_page_config(page_title="Cubagem de Veículos - JWM", layout="wide")

# ============================
# SESSION STATE INIT
# ============================

if "df_result" not in st.session_state:
    st.session_state.df_result = pd.DataFrame()

if "df_viaveis" not in st.session_state:
    st.session_state.df_viaveis = None

if "veiculo_simulado" not in st.session_state:
    st.session_state.veiculo_simulado = None

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
# LISTA E EDIÇÃO DE CARGAS
# ============================

if st.session_state.cargas:

    st.subheader("📋 Cargas adicionadas (Editáveis)")

    df_cargas_edit = pd.DataFrame(st.session_state.cargas)

    df_editado = st.data_editor(
        df_cargas_edit,
        use_container_width=True,
        num_rows="dynamic",
        key="editor_cargas"
    )

    col1, col2, col3 = st.columns(3)

    # 💾 SALVAR ALTERAÇÕES
    with col1:
        if st.button("💾 Salvar alterações"):
            try:
                novas_cargas = []

                for _, row in df_editado.iterrows():

                    vol_unit = (
                        row["Comprimento (m)"]
                        * row["Largura (m)"]
                        * row["Altura (m)"]
                    )

                    peso_total = (
                        row["Peso unitário (kg)"]
                        * row["Quantidade"]
                    )

                    novas_cargas.append({
                        "Comprimento (m)": row["Comprimento (m)"],
                        "Largura (m)": row["Largura (m)"],
                        "Altura (m)": row["Altura (m)"],
                        "Peso unitário (kg)": row["Peso unitário (kg)"],
                        "Quantidade": int(row["Quantidade"]),
                        "Volume total (m³)": vol_unit * row["Quantidade"],
                        "Peso total (kg)": peso_total
                    })

                st.session_state.cargas = novas_cargas
                st.success("Alterações salvas com sucesso!")
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao salvar alterações: {e}")

    # ❌ LIMPAR CARGA UNITÁRIA
    with col2:
        indice_excluir = st.number_input(
            "Excluir carga nº:",
            min_value=1,
            max_value=len(st.session_state.cargas),
            step=1
        )

        if st.button("❌ Excluir carga selecionada"):
            del st.session_state.cargas[indice_excluir - 1]
            st.success("Carga removida.")
            st.rerun()

    # 🧹 LIMPAR TODAS
    with col3:
        if st.button("🧹 Limpar todas"):
            st.session_state.cargas = []
            st.success("Todas as cargas foram removidas.")
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

# ============================
# EXPORTAR RESULTADOS PARA EXCEL
# ============================

def gerar_excel_bytes(df_result, cargas):

    from io import BytesIO
    import pandas as pd

    out = BytesIO()

    with pd.ExcelWriter(out, engine="openpyxl") as writer:

        # Aba de Resultados
        if df_result is not None and not df_result.empty:
            df_result.to_excel(
                writer,
                sheet_name="Resultados",
                index=False
            )
        else:
            pd.DataFrame({
                "Aviso": ["Sem dados disponíveis para exportação"]
            }).to_excel(
                writer,
                sheet_name="Resultados",
                index=False
            )

        # Aba de Cargas (se existir)
        if cargas is not None and len(cargas) > 0:
            df_cargas = pd.DataFrame(cargas)
            df_cargas.to_excel(
                writer,
                sheet_name="Cargas",
                index=False
            )

    out.seek(0)
    return out


# ============================
# BOTÃO DE DOWNLOAD
# ============================

if (
    "df_result" in st.session_state
    and st.session_state.df_result is not None
    and not st.session_state.df_result.empty
):

    excel = gerar_excel_bytes(
        st.session_state.df_result,
        st.session_state.get("cargas", [])
    )

    st.download_button(
        label="📥 Baixar Excel",
        data=excel,
        file_name="dimensionamento_veiculos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("⚠ Execute a simulação antes de exportar o Excel.")

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
# BOTÃO CALCULAR (VERSÃO PROFISSIONAL)
# ============================

if st.button("🚛 Calcular Dimensionamento"):

    if not st.session_state.cargas:
        st.warning("Adicione pelo menos uma carga.")
        st.stop()

    resultados = []

    if selecionados:
        df_testar = df_veiculos[df_veiculos["Veículo"].isin(selecionados)]
    else:
        df_testar = df_veiculos

    # 🔢 Totais reais
    volume_total_carga = sum(
        item["Volume total (m³)"] for item in st.session_state.cargas
    )

    peso_total = sum(
        item["Peso total (kg)"] for item in st.session_state.cargas
    )

    cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas)

    # ============================
    # LOOP VEÍCULOS
    # ============================
    for _, veic in df_testar.iterrows():

        comp_v = veic["comprimento"]
        larg_v = veic["largura"]
        alt_v  = veic["altura"]
        peso_max = veic["peso_max"]

        volume_veiculo = comp_v * larg_v * alt_v

        status = "Viável"
        motivo = ""

        # 🔴 VERIFICA VOLUME
        if volume_total_carga > volume_veiculo:
            status = "Inviável"
            motivo = "Excede volume do veículo"

        # 🔴 VERIFICA PESO
        elif peso_total > peso_max:
            status = "Inviável"
            motivo = "Excede peso máximo permitido"

        # 🔴 VERIFICA EMPILHAMENTO
        else:
            cabe = cabe_no_piso_heuristica(
                cargas_unitarias,
                comp_v,
                larg_v,
                alt_v
            )

            if not cabe:
                status = "Inviável"
                motivo = "Não cabe fisicamente (dimensão incompatível)"

        # 🚫 SE INVIÁVEL
        if status == "Inviável":
            resultados.append({
                "Veículo": veic["Veículo"],
                "Status": status,
                "Motivo": motivo,
                "Aproveitamento Volume (%)": None,
                "Aproveitamento Peso (%)": None,
                "Score": None
            })
            continue

        # ✅ SE VIÁVEL
        aproveitamento_volume = round(
            (volume_total_carga / volume_veiculo) * 100, 2
        )

        aproveitamento_peso = round(
            (peso_total / peso_max) * 100, 2
        )

        score = round(
            (aproveitamento_volume * 0.6) +
            (aproveitamento_peso * 0.4),
            2
        )

        resultados.append({
            "Veículo": veic["Veículo"],
            "Status": "Viável",
            "Motivo": "",
            "Aproveitamento Volume (%)": aproveitamento_volume,
            "Aproveitamento Peso (%)": aproveitamento_peso,
            "Score": score
        })

    # ============================
    # DATAFRAME FINAL
    # ============================
    df_result = pd.DataFrame(resultados)

    df_result = df_result.sort_values(
        by=["Status", "Score"],
        ascending=[True, False]
    ).reset_index(drop=True)

    st.session_state.df_result = df_result

    st.success("Cálculo concluído com sucesso!")

# ============================
# 🚛 VEÍCULOS VIÁVEIS (APENAS)
# ============================

if not st.session_state.df_result.empty:

    df_base = st.session_state.df_result.copy()

    # 🔹 Filtra somente viáveis
    df_viaveis = df_base[df_base["Status"] == "Viável"].copy()

    if not df_viaveis.empty:

        # 🔹 Ordena por Score (maior primeiro)
        df_viaveis = df_viaveis.sort_values(
            by="Score",
            ascending=False
        ).reset_index(drop=True)

        # 🔹 Criar Ranking
        df_viaveis["Ranking"] = df_viaveis.index + 1

        melhor_veiculo = df_viaveis.iloc[0]["Veículo"]

        # 🔹 Destaque visual do melhor
        def destacar_melhor(row):
            if row["Veículo"] == melhor_veiculo:
                return [
                    "background-color: #145A32; color: white; font-weight: bold; font-size: 15px;"
                ] * len(row)
            else:
                return [""] * len(row)

        st.subheader("🏆 Veículos Viáveis (Ranking)")

        st.dataframe(
            df_viaveis.style.apply(destacar_melhor, axis=1),
            use_container_width=True
        )

        st.success(f"🚛 Melhor veículo pelo ranking: {melhor_veiculo}")

    else:
        st.warning("⚠ Nenhum veículo é viável para essa carga.")

else:
    st.info("Clique em calcular para gerar o dimensionamento.")

# ==========================================================
# 📦 SIMULAÇÃO REAL DE EMPILHAMENTO
# ==========================================================

if st.button("🔍 Simular Empilhamento"):

    if st.session_state.df_result.empty:
        st.error("⚠ Execute o cálculo primeiro.")
        st.stop()

    # 🔹 Cria df_base corretamente
    df_base = st.session_state.df_result.copy()

    # 🔹 Filtra apenas veículos viáveis
    df_viaveis = df_base[df_base["Status"] == "Viável"].copy()

    if df_viaveis.empty:
        st.error("❌ Nenhum veículo viável encontrado.")
        st.stop()

    # 🔹 Ordena pelo maior Score (ranking geral)
    df_viaveis = df_viaveis.sort_values(
        by="Score",
        ascending=False
    )

    veiculo_simulado = df_viaveis.iloc[0]

    st.success(f"🚛 Veículo ideal pelo ranking: {veiculo_simulado['Veículo']}")

    # ------------------------------------------------------
    # DADOS DO VEÍCULO
    # ------------------------------------------------------

    comp_veic = df_veiculos.loc[
        df_veiculos["Veículo"] == veiculo_simulado["Veículo"],
        "comprimento"
    ].values[0]

    larg_veic = df_veiculos.loc[
        df_veiculos["Veículo"] == veiculo_simulado["Veículo"],
        "largura"
    ].values[0]

    alt_veic = df_veiculos.loc[
        df_veiculos["Veículo"] == veiculo_simulado["Veículo"],
        "altura"
    ].values[0]

    # ------------------------------------------------------
    # 3️⃣ DADOS DA CARGA
    # ------------------------------------------------------

    # Usa a primeira carga como padrão
    carga_base = st.session_state.cargas[0]
    
    comp_cx = carga_base["Comprimento (m)"]
    larg_cx = carga_base["Largura (m)"]
    alt_cx  = carga_base["Altura (m)"]
    
    qtd_total = sum(c["Quantidade"] for c in st.session_state.cargas)
    # ------------------------------------------------------
    # 4️⃣ CÁLCULO DE EMPILHAMENTO REAL (VERSÃO CORRIGIDA)
    # ------------------------------------------------------
    
    capacidade_total = 0
    espaco_ocupado = 0
    caixas_alocadas = 0
    
    for carga in st.session_state.cargas:
    
        comp_cx = carga["Comprimento (m)"]
        larg_cx = carga["Largura (m)"]
        alt_cx  = carga["Altura (m)"]
        qtd_cx  = carga["Quantidade"]
    
        qtd_comp = int(comp_veic // comp_cx)
        qtd_larg = int(larg_veic // larg_cx)
        qtd_alt  = int(alt_veic  // alt_cx)
    
        capacidade_carga = qtd_comp * qtd_larg * qtd_alt
    
        capacidade_total += capacidade_carga
        caixas_alocadas += min(qtd_cx, capacidade_carga)
    
    st.write("### 📊 Capacidade Real de Empilhamento (Todas as Cargas)")
    st.write(f"Capacidade máxima estimada: {capacidade_total} caixas")
    st.write(f"Carga solicitada: {qtd_total} caixas")
    
    if caixas_alocadas < qtd_total:
        st.error("⚠️ A quantidade NÃO cabe fisicamente no veículo.")
        st.stop()
    else:
        st.success("✅ A carga cabe fisicamente no veículo.")

    # ------------------------------------------------------
    # 5️⃣ VISUALIZAÇÃO 3D PROFISSIONAL (ESTÁTICO)
    # ------------------------------------------------------
    
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas)
    
    # 🎨 Paleta profissional
    cores = [
        "#1f77b4", "#ff7f0e", "#2ca02c",
        "#d62728", "#9467bd", "#8c564b"
    ]
    
    contador = 0
    
    for idx, item in enumerate(cargas_unitarias):
    
        comp_cx = item["comp"]
        larg_cx = item["larg"]
        alt_cx  = item["alt"]
    
        cor = cores[idx % len(cores)]
    
        max_x = int(comp_veic // comp_cx)
        max_y = int(larg_veic // larg_cx)
    
        x0 = (contador % max_x) * comp_cx
        y0 = ((contador // max_x) % max_y) * larg_cx
        z0 = (contador // (max_x * max_y)) * alt_cx
    
        fig.add_trace(go.Mesh3d(
            x=[x0, x0+comp_cx, x0+comp_cx, x0,
               x0, x0+comp_cx, x0+comp_cx, x0],
            y=[y0, y0, y0+larg_cx, y0+larg_cx,
               y0, y0, y0+larg_cx, y0+larg_cx],
            z=[z0, z0, z0, z0,
               z0+alt_cx, z0+alt_cx, z0+alt_cx, z0+alt_cx],
            opacity=0.95,
            color=cor,
            flatshading=True,
            lighting=dict(
                ambient=0.6,
                diffuse=0.9,
                roughness=0.3,
                specular=0.4
            ),
            showscale=False
        ))
    
        contador += 1
    
    # ============================
    # ESTRUTURA DO BAÚ
    # ============================
    
    fig.add_trace(go.Mesh3d(
        x=[0, comp_veic, comp_veic, 0, 0, comp_veic, comp_veic, 0],
        y=[0, 0, larg_veic, larg_veic, 0, 0, larg_veic, larg_veic],
        z=[0, 0, 0, 0, alt_veic, alt_veic, alt_veic, alt_veic],
        opacity=0.06,
        color="#222222",
        flatshading=True,
        showscale=False
    ))
    
    # ============================
    # INDICADOR DE OCUPAÇÃO
    # ============================
    
    volume_carga = sum(
        item["comp"] * item["larg"] * item["alt"]
        for item in cargas_unitarias
    )
    
    volume_veiculo = comp_veic * larg_veic * alt_veic
    ocupacao = (volume_carga / volume_veiculo) * 100
    
    # ============================
    # LAYOUT PROFISSIONAL
    # ============================
    
    fig.update_layout(
        title=f"Simulação 3D de Carregamento | Ocupação: {ocupacao:.1f}%",
        scene=dict(
            xaxis=dict(title="Comprimento", showgrid=False),
            yaxis=dict(title="Largura", showgrid=False),
            zaxis=dict(title="Altura", showgrid=False),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.7, y=1.7, z=1.3)
            )
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        height=800,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)



