import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go

MAX_CAIXAS = 300
MAX_CAIXAS_3D = 200
MAX_ITERACOES = 5000
MAX_GRID = 10000

# ============================
# CONFIGURAÇÃO INICIAL
# ============================
st.set_page_config(page_title="Cubagem de Veículos - JWM", layout="wide")

# ============================
# SESSION STATE INIT
# ============================

if "df_result" not in st.session_state or not isinstance(st.session_state.df_result, pd.DataFrame):
    st.session_state.df_result = pd.DataFrame(columns=[
        "Veículo",
        "Status",
        "Motivo",
        "Aproveitamento Volume (%)",
        "Aproveitamento Peso (%)",
        "Score"
    ])
    
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
@st.cache_data
def get_veiculos():
    df = pd.DataFrame(lista_veiculos)
    df["Capacidade Volume (m³)"] = (
        df["largura"] * df["comprimento"] * df["altura"]
    )
    df.rename(columns={"nome": "Veículo"}, inplace=True)
    return df

df_veiculos = get_veiculos()

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
    comp = round(st.number_input("Comprimento (m):", min_value=0.0, step=0.01, format="%.2f", key="comp"), 2)
with col2:
    larg = round(st.number_input("Largura (m):", min_value=0.0, step=0.01, format="%.2f", key="larg"), 2)
with col3:
    alt = round(st.number_input("Altura (m):", min_value=0.0, step=0.01, format="%.2f", key="alt"), 2)
with col4:
    peso = round(st.number_input("Peso unitário (kg):", min_value=0.0, step=0.01, format="%.2f", key="peso"), 2)

qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1, key="qtd")

if qtd > 1000:
    st.warning("⚠ Quantidade muito alta pode impactar a performance.")


# ============================
# ADICIONAR CARGA
# ============================
if st.button("➕ Adicionar carga"):
    try:
        c = float(comp)
        l = float(larg)
        a = float(alt)
        p = float(peso)

        if c == 0 or l == 0 or a == 0 or p == 0:
            st.warning("Preencha todos os campos corretamente.")
            st.stop()
        
        if c <= 0 or l <= 0 or a <= 0:
            raise ValueError("Dimensões devem ser maiores que zero.")
        
        if p <= 0:
            raise ValueError("Peso deve ser maior que zero.")

        vol_unit = c * l * a
        peso_total = p * qtd

        st.session_state.cargas.append({
            "Comprimento (m)": c,
            "Largura (m)": l,
            "Altura (m)": a,
            "Peso unitário (kg)": p,
            "Quantidade": qtd,
            "Volume total (m³)": vol_unit * qtd,
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

                colunas_esperadas = [
                    "Comprimento (m)", "Largura (m)", "Altura (m)",
                    "Peso unitário (kg)", "Quantidade"
                ]
                
                for col in colunas_esperadas:
                    if col not in df_editado.columns:
                        raise ValueError(f"Coluna obrigatória ausente: {col}")

                for _, row in df_editado.iterrows():

                    # 🔒 garante tipo numérico
                    try:
                        comp = float(row["Comprimento (m)"])
                        larg = float(row["Largura (m)"])
                        alt = float(row["Altura (m)"])
                        peso = float(row["Peso unitário (kg)"])
                    except:
                        raise ValueError("Valores inválidos na tabela.")
                    
                    if comp <= 0 or larg <= 0 or alt <= 0:
                        raise ValueError("Dimensões inválidas.")
                    
                    if peso <= 0:
                        raise ValueError("Peso inválido.")
                                        
                    vol_unit = comp * larg * alt
                    
                    try:
                        qtd_row = int(row["Quantidade"])
                    except:
                        raise ValueError("Quantidade inválida.")
                                        
                    if qtd_row <= 0:
                        raise ValueError("Quantidade inválida.")
                    peso_total = peso * qtd_row
                    
                    novas_cargas.append({
                        "Comprimento (m)": comp,
                        "Largura (m)": larg,
                        "Altura (m)": alt,
                        "Peso unitário (kg)": peso,
                        "Quantidade": qtd_row,
                        "Volume total (m³)": vol_unit * qtd_row,
                        "Peso total (kg)": peso_total
                    })

                st.session_state.cargas = novas_cargas
                st.success("Alterações salvas com sucesso!")
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao salvar alterações: {e}")

    # ❌ LIMPAR CARGA UNITÁRIA
    with col2:
        if len(df_editado) > 0:
            linha_para_excluir = st.selectbox(
                "Selecione a carga para excluir:",
                options=range(len(df_editado)),
                format_func=lambda i: f"Carga {i+1}"
            )
        
            if st.button("❌ Excluir carga selecionada"):
                del st.session_state.cargas[linha_para_excluir]
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
def expand_cargas_unitarias(cargas, limite=MAX_CAIXAS):
    lista = []
    total_original = sum(c["Quantidade"] for c in cargas)

    for c in cargas:
    
        if c["Peso unitário (kg)"] <= 0:
            continue
        if (
            c["Comprimento (m)"] <= 0 or
            c["Largura (m)"] <= 0 or
            c["Altura (m)"] <= 0
        ):
            continue

        for _ in range(c["Quantidade"]):
        
            if len(lista) >= limite:
                st.warning(
                    f"⚠ Limite de simulação atingido ({limite} caixas). "
                    f"Total real: {total_original}"
                )
                return lista
        
            comp = float(c["Comprimento (m)"])
            larg = float(c["Largura (m)"])
            alt = float(c["Altura (m)"])
            
            lista.append({
                "comp": comp,
                "larg": larg,
                "alt": alt,
                "peso": float(c["Peso unitário (kg)"]),
                "volume": comp * larg * alt
            })

    return lista
def calcular_totais(cargas):
    volume = sum(item["Volume total (m³)"] for item in cargas)
    peso = sum(
        float(item.get("Peso total (kg)", 0))
        for item in cargas
    )
    return volume, peso

from itertools import combinations_with_replacement

def gerar_cenarios(lista_veiculos, max_veiculos=3):
    nomes = lista_veiculos["Veículo"].tolist()
    cenarios = []

    for i in range(1, max_veiculos + 1):
        cenarios += list(combinations_with_replacement(nomes, i))

    return cenarios
    
# ============================
# EXPORTAR RESULTADOS PARA EXCEL
# ============================
def gerar_excel_bytes(df_result, cargas):

    from io import BytesIO
    import pandas as pd

    out = BytesIO()

    with pd.ExcelWriter(out, engine="openpyxl") as writer:

        if isinstance(df_result, pd.DataFrame) and not df_result.empty:
            df_result.to_excel(writer, sheet_name="Resultados", index=False)
        else:
            pd.DataFrame({
                "Aviso": ["Sem dados disponíveis para exportação"]
            }).to_excel(writer, sheet_name="Resultados", index=False)

        if isinstance(cargas, list) and len(cargas) > 0:
            df_cargas = pd.DataFrame(cargas)
        
            if not df_cargas.empty:
                df_cargas.to_excel(writer, sheet_name="Cargas", index=False)

    out.seek(0)
    return out


# ============================
# 🔴 COLE A FUNÇÃO AQUI
# ============================
def cabe_no_piso_heuristica(cargas_unitarias, veh_comp, veh_larg, veh_alt):

    if len(cargas_unitarias) > 80:

        dimensoes_unicas = set(
            (c["comp"], c["larg"], c["alt"]) for c in cargas_unitarias
        )

        if len(dimensoes_unicas) == 1:

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

    items = sorted(
        cargas_unitarias,
        key=lambda x: x['comp'] * x['larg'] * x['alt'],
        reverse=True
    )

    rows = []

    for it in items:
        placed = False

        for comp_i, larg_i in [(it['comp'], it['larg']), (it['larg'], it['comp'])]:

            EPS = 1e-6
            
            if comp_i > veh_comp + EPS or larg_i > veh_larg + EPS:
                continue

            for row in rows:
                if row['used_length'] + comp_i <= veh_comp + 1e-6:

                    total_rows_width = sum(r['row_width'] for r in rows)
                    
                    total_width = (
                        total_rows_width
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

def calcular_multi_veiculos(cargas, df_veiculos):

    cargas_unit = expand_cargas_unitarias(cargas, limite=MAX_CAIXAS)
    # ordenar cargas maiores primeiro
    cargas_unit = sorted(
        cargas_unit,
        key=lambda x: x["comp"] * x["larg"] * x["alt"],
        reverse=True
    )

    # ordenar veículos do maior para o menor
    veiculos_ordenados = df_veiculos.sort_values(
        by="Capacidade Volume (m³)",
        ascending=True
    )

    resultado = []
    cargas_restantes = cargas_unit.copy()
    
    # 🔴 alerta de cargas impossíveis
    if any(c["peso"] > df_veiculos["peso_max"].max() for c in cargas_restantes):
        st.warning("⚠ Existem cargas com peso maior que qualquer veículo disponível.")

while cargas_restantes:

    alocou_algum = False

    for _, veic in veiculos_ordenados.iterrows():

        if not cargas_restantes:
            break

        comp_v, larg_v, alt_v, peso_max = (
            veic["comprimento"],
            veic["largura"],
            veic["altura"],
            veic["peso_max"]
        )

        alocadas = []
        peso_total = 0
        volume_ocupado = 0
        novas_restantes = []

        for carga in cargas_restantes:

            volume_carga = carga["volume"]

            if (
                peso_total + carga["peso"] > peso_max or
                volume_ocupado + volume_carga > (comp_v * larg_v * alt_v)
            ):
                novas_restantes.append(carga)
                continue

            cabe = cabe_no_piso_heuristica(
                alocadas + [carga],
                comp_v,
                larg_v,
                alt_v
            )

            if cabe:
                alocadas.append(carga)
                peso_total += carga["peso"]
                volume_ocupado += volume_carga
                alocou_algum = True
            else:
                novas_restantes.append(carga)

        if alocadas:
            resultado.append({
                "Veículo": veic["Veículo"],
                "Qtd Caixas": len(alocadas),
                "Peso Total (kg)": round(peso_total, 2)
            })

        cargas_restantes = novas_restantes

    if not alocou_algum:
        break

    return resultado, len(cargas_restantes)
def simular_cenario(cargas, veiculos_usados, df_veiculos):

    cargas_restantes = expand_cargas_unitarias(cargas)
    resultado = []

    for nome_veic in veiculos_usados:

        veic_match = df_veiculos[df_veiculos["Veículo"] == nome_veic]

        if veic_match.empty:
            continue  # 🔥 evita crash

        veic = veic_match.iloc[0]

        comp_v = veic["comprimento"]
        larg_v = veic["largura"]
        alt_v  = veic["altura"]
        peso_max = veic["peso_max"]

        alocadas = []
        peso_total = 0

        novas_restantes = []
        
        for carga in cargas_restantes:
        
            volume_ocupado = sum(c["volume"] for c in alocadas)
            volume_carga = carga["volume"]
            
            if (
                peso_total + carga["peso"] > peso_max or
                volume_ocupado + volume_carga > (comp_v * larg_v * alt_v)
            ):
                novas_restantes.append(carga)
                continue
        
            cabe = cabe_no_piso_heuristica(
                alocadas + [carga],
                comp_v,
                larg_v,
                alt_v
            )
        
            if cabe:
                alocadas.append(carga)
                peso_total += carga["peso"]
            else:
                novas_restantes.append(carga)
        
        cargas_restantes = novas_restantes

        resultado.append({
            "Veículo": nome_veic,
            "Qtd Caixas": len(alocadas),
            "Peso Total (kg)": round(peso_total, 2)
        })

    return resultado, len(cargas_restantes)

# ============================
# 🚀 BOTÃO CALCULAR
# ============================
btn_calcular = st.button(
    "🚀 Calcular Dimensionamento",
    disabled=not st.session_state.cargas
)

if btn_calcular:
    with st.spinner("Calculando melhor cenário..."):

        if not st.session_state.cargas:
            st.warning("Adicione pelo menos uma carga.")
            st.stop()

        # seleção de veículos
        if selecionados:
            df_testar = df_veiculos[df_veiculos["Veículo"].isin(selecionados)]
        else:
            df_testar = df_veiculos

        # totais reais
        volume_total_carga, peso_total = calcular_totais(st.session_state.cargas)

    # ============================
    # 🔥 MODO MULTI-VEÍCULO
    # ============================
    
        # ============================
        # 🧠 CENÁRIOS INTELIGENTES
        # ============================
    
        # ============================
        # 🟢 TESTE DE VEÍCULO ÚNICO
        # ============================
        resultados = []
        
        cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas, limite=300)
        
        for _, veic in df_testar.iterrows():
        
            comp_v = veic["comprimento"]
            larg_v = veic["largura"]
            alt_v  = veic["altura"]
            peso_max = veic["peso_max"]
        
            volume_veiculo = comp_v * larg_v * alt_v
        
            status = "Viável"
            motivo = ""
        
            if volume_total_carga > volume_veiculo:
                status = "Inviável"
                motivo = "Excede volume"
        
            elif peso_total > peso_max:
                status = "Inviável"
                motivo = "Excede peso"
        
            else:
                cabe = cabe_no_piso_heuristica(
                    cargas_unitarias,
                    comp_v,
                    larg_v,
                    alt_v
                )
        
                if not cabe:
                    status = "Inviável"
                    motivo = "Não cabe fisicamente"
        
            resultados.append({
                "Veículo": veic["Veículo"],
                "Status": status,
                "Motivo": motivo
            })
        
        df_result = pd.DataFrame(resultados)
        
        # ============================
        # 🔴 DECISÃO AUTOMÁTICA
        # ============================
        if (df_result["Status"] == "Viável").any():
        
            st.session_state.df_result = df_result
            st.success("✅ Veículo único encontrado!")
        
        else:
        
            st.warning("⚠ Nenhum veículo único comporta a carga. Calculando multi-veículo...")
        
            resultado, sobra = calcular_multi_veiculos(
                st.session_state.cargas,
                df_testar
            )
        
            df_multi = pd.DataFrame(resultado)
        
            st.session_state.df_result = df_multi
        
            if sobra > 0:
                st.warning(f"⚠ {sobra} caixas não foram alocadas.")
        
            st.success("🚚 Solução com múltiplos veículos encontrada!")
            st.dataframe(df_multi, use_container_width=True)
        
            st.stop()

    # ============================
    # 🟢 MODO MELHOR VEÍCULO
    # ============================

    resultados = []

    cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas, limite=300)
    
    # 🔥 PROTEÇÃO DE PERFORMANCE
    if len(cargas_unitarias) > 200:
        st.warning(
            f"⚠ Muitas caixas ({len(cargas_unitarias)}). "
            f"A simulação 3D será limitada para manter a performance."
        )
        
        # limitar quantidade simulada
        cargas_unitarias = cargas_unitarias[:200]

    if not cargas_unitarias:
        st.error("Nenhuma carga válida para simulação.")
        st.stop()

    def calcular_volume_veiculo(veic):
        return veic["comprimento"] * veic["largura"] * veic["altura"]
    
    for _, veic in df_testar.iterrows():
    
        comp_v = veic["comprimento"]
        larg_v = veic["largura"]
        alt_v  = veic["altura"]
        peso_max = veic["peso_max"]
    
        volume_veiculo = calcular_volume_veiculo(veic)
    
        status = "Viável"
        motivo = ""
    
        # valida volume
        if volume_total_carga > volume_veiculo:
            status = "Inviável"
            motivo = "Excede volume do veículo"
    
        # valida peso
        elif peso_total > peso_max:
            status = "Inviável"
            motivo = "Excede peso máximo permitido"
    
        # valida dimensão real
        else:
            cabe = cabe_no_piso_heuristica(
                cargas_unitarias,
                comp_v,
                larg_v,
                alt_v
            )
    
            if not cabe:
                status = "Inviável"
                motivo = "Não cabe fisicamente"
            
        if status == "Inviável":
            resultados.append({
                "Veículo": veic["Veículo"],
                "Status": "Inviável",
                "Motivo": motivo,
                "Aproveitamento Volume (%)": 0,
                "Aproveitamento Peso (%)": 0,
                "Score": 0
            })
            continue
        
        # ✅ FORA do if (agora executa corretamente)
        aproveitamento_volume = round(
            (volume_total_carga / volume_veiculo) * 100, 2
        )
        
        aproveitamento_peso = round(
            (peso_total / peso_max) * 100, 2
        ) if peso_max > 0 else 0
        
        ociosidade = 100 - aproveitamento_volume
        balanceamento = 100 - abs(aproveitamento_volume - aproveitamento_peso)
        
        penalidade_excesso = max(0, aproveitamento_peso - 100) * 2
        
        score = (
            (aproveitamento_volume * 0.45) +
            (aproveitamento_peso * 0.35) +
            (balanceamento * 0.2)
            - penalidade_excesso
        )
        
        score = max(0, round(score, 2))
        
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
    
    if df_result.empty:
        st.error("❌ Nenhum resultado gerado.")
        st.stop()

    if "Score" in df_result.columns:
        df_result = df_result.sort_values(
            by=["Score"],
            ascending=False
        ).reset_index(drop=True)
    st.session_state.df_result = df_result

    st.success("Cálculo concluído com sucesso!")

# ============================
# 🚛 VEÍCULOS VIÁVEIS (APENAS)
# ============================

df_base = st.session_state.df_result

if df_base.empty:
    st.info("Clique em calcular para gerar o dimensionamento.")
else:

    # modo multi-veículo
    if "Status" not in df_base.columns:
        st.warning("⚠️ Resultado exibido no modo multi-veículo (sem ranking).")
        st.dataframe(df_base, use_container_width=True)
        st.stop()

df_viaveis = df_base[df_base["Status"] == "Viável"].copy()

if df_viaveis.empty:
    st.warning("⚠ Nenhum veículo viável encontrado.")
    st.stop()

df_viaveis = df_viaveis.sort_values(
    by="Score",
    ascending=False
).reset_index(drop=True)

df_viaveis["Ranking"] = df_viaveis.index + 1

if df_viaveis.empty:
    st.error("❌ Nenhum veículo disponível para simulação.")
    st.stop()

melhor_veiculo = df_viaveis.iloc[0]["Veículo"]

def destacar(row):
    if row["Veículo"] == melhor_veiculo:
        return ["background-color:#145A32;color:white;font-weight:bold"] * len(row)
    return [""] * len(row)

st.subheader("🏆 Veículos Viáveis (Ranking)")

st.dataframe(
    df_viaveis.style.apply(destacar, axis=1),
    use_container_width=True
)

# ============================
# 🧠 EXPLICAÇÃO DO MELHOR VEÍCULO
# ============================

if df_viaveis.empty:
    st.error("❌ Nenhum veículo viável encontrado.")
    st.stop()

melhor_linha = df_viaveis.iloc[0]

vol = float(melhor_linha.get("Aproveitamento Volume (%)", 0) or 0)
peso = float(melhor_linha.get("Aproveitamento Peso (%)", 0) or 0)
score = float(melhor_linha.get("Score", 0) or 0)

# 🔍 lógica de explicação
if abs(vol - peso) < 10:
    motivo = "Possui ótimo balanceamento entre peso e volume"
elif vol > peso:
    motivo = "Aproveita melhor o espaço do veículo (volume)"
else:
    motivo = "Aproveita melhor a capacidade de carga (peso)"

# 🔥 EXIBIÇÃO PROFISSIONAL
st.success(
    f"""
🏆 **Melhor escolha:** {melhor_veiculo}

📊 **Por quê?**
- Volume utilizado: {vol}%
- Peso utilizado: {peso}%
- Score final: {score}

💡 {motivo}
"""
)
def colide(nova, ocupadas):
    x, y, z, dx, dy, dz = nova

    for ox, oy, oz, odx, ody, odz in ocupadas:
        if (
            x < ox + odx and x + dx > ox and
            y < oy + ody and y + dy > oy and
            z < oz + odz and z + dz > oz
        ):
            return True
    return False


def tem_base(nova, ocupadas):
    x, y, z, dx, dy, dz = nova

    if z == 0:
        return True

    for ox, oy, oz, odx, ody, odz in ocupadas:
        if (
            oz + odz == z and
            x < ox + odx and x + dx > ox and
            y < oy + ody and y + dy > oy
        ):
            return True

    return False


# ============================
# 🔍 SIMULAÇÃO REAL DE EMPILHAMENTO (AJUSTADA)
# ============================

if st.button("🔍 Simular Empilhamento"):

    if st.session_state.df_result.empty:
        st.error("⚠ Execute o cálculo primeiro.")
        st.stop()

    if not st.session_state.cargas:
        st.error("⚠ Nenhuma carga disponível.")
        st.stop()

    qtd_total_real = sum(c["Quantidade"] for c in st.session_state.cargas)
    volume_total_carga, peso_total = calcular_totais(st.session_state.cargas)

    # expandir cargas
    cargas_unitarias = expand_cargas_unitarias(st.session_state.cargas, limite=300)
    
    # 🔥 PROTEÇÃO DE PERFORMANCE
    
    if len(cargas_unitarias) > MAX_CAIXAS_3D:
        st.warning(
            f"⚠ Simulação limitada a {MAX_CAIXAS_3D} caixas "
            f"(total real: {len(cargas_unitarias)})"
        )
        cargas_unitarias = cargas_unitarias[:MAX_CAIXAS_3D]
    
    # ✅ AGORA SIM DENTRO DO BOTÃO
    if "Status" in st.session_state.df_result.columns:
        df_viaveis = st.session_state.df_result[
            st.session_state.df_result["Status"] == "Viável"
        ].copy()
    else:
        st.warning("Modo multi-veículo não suporta simulação de empilhamento.")
        st.stop()
    
    # fora do else
    if df_viaveis is None or df_viaveis.empty:
        st.error("❌ Nenhum veículo viável encontrado.")
        st.stop()

    df_viaveis = (
        df_viaveis
        .dropna(subset=["Score"])
        .sort_values(by="Score", ascending=False)
        .reset_index(drop=True)
    )
    
    if df_viaveis.empty:
        st.error("❌ Nenhum veículo válido com score.")
        st.stop()
    melhor_veiculo = df_viaveis.iloc[0]["Veículo"]
    
    veic_match = df_veiculos[df_veiculos["Veículo"] == melhor_veiculo]

    if veic_match.empty:
        st.error(f"Veículo {melhor_veiculo} não encontrado na base.")
        st.stop()
    
    veic = veic_match.iloc[0]

    comp_veic = veic["comprimento"]
    larg_veic = veic["largura"]
    alt_veic = veic["altura"]
    volume_veiculo = comp_veic * larg_veic * alt_veic

    if comp_veic <= 0 or larg_veic <= 0 or alt_veic <= 0:
        st.error("Dimensões do veículo inválidas.")
        st.stop()

    cargas_unitarias = sorted(
        cargas_unitarias,
        key=lambda x: (x["comp"] * x["larg"] * x["alt"]),
        reverse=True
    )

    posicoes_ocupadas = []
    caixas_alocadas = 0
    peso_acumulado = 0
    peso_max = veic["peso_max"]

    limite_iter = MAX_ITERACOES
    contador = 0
    estourou_limite = False
    for item in cargas_unitarias:
    
        if estourou_limite:
            break
    
        # 🔥 VALIDAÇÃO EXTRA DE SEGURANÇA
        if item["peso"] <= 0:
            continue
    
        encaixou = False
    
        orientacoes = [
            (item["comp"], item["larg"], item["alt"]),
            (item["larg"], item["comp"], item["alt"])
        ]
    
        for comp_o, larg_o, alt_o in orientacoes:
        
            # 🔒 validação mais rígida
            if min(comp_o, larg_o, alt_o) <= 0:
                continue
        
            # 🔥 evita divisões inválidas
            try:
                x_max = int(comp_veic // comp_o) if comp_o > 0 else 0
                y_max = int(larg_veic // larg_o) if larg_o > 0 else 0
                z_max = int(alt_veic // alt_o) if alt_o > 0 else 0
        
                if x_max <= 0 or y_max <= 0 or z_max <= 0:
                    continue
            except:
                continue
        
            # 🔥 controle inteligente de grid
            grid_size = x_max * y_max * z_max
            
            if grid_size > MAX_GRID:
                fator = (grid_size / MAX_GRID) ** (1/3)
            
                x_max = max(1, int(x_max / fator))
                y_max = max(1, int(y_max / fator))
                z_max = max(1, int(z_max / fator))
            
                # 🔥 recalcular grid
                grid_size = x_max * y_max * z_max
        
            # 🔴 PROTEÇÃO FINAL (NOVO)
            if grid_size > MAX_GRID:
                continue
        
            if grid_size <= 0:
                continue
            
            for x in range(x_max):
                if estourou_limite:
                    break
            
                for y in range(y_max):
                    if estourou_limite:
                        break
            
                    for z in range(z_max):
        
                        contador += 1
        
                        if contador > limite_iter:
                            st.warning("Limite de simulação atingido.")
                            estourou_limite = True
                            break
            
                        nova_caixa = (
                            x * comp_o,
                            y * larg_o,
                            z * alt_o,
                            comp_o,
                            larg_o,
                            alt_o
                        )
            
                        if colide(nova_caixa, posicoes_ocupadas):
                            continue
            
                        if not tem_base(nova_caixa, posicoes_ocupadas):
                            continue
                                    
                        # valida peso antes de alocar
                        if peso_acumulado + item["peso"] > peso_max:
                            continue
                        
                        posicoes_ocupadas.append(nova_caixa)
                        caixas_alocadas += 1
                        peso_acumulado += item["peso"]
                                    
                        if caixas_alocadas >= qtd_total_real:
                            encaixou = True
                            estourou_limite = True
                            break
            
                    if encaixou or estourou_limite:
                        break
                if encaixou or estourou_limite:
                    break

    volume_usado = sum(
        c * l * a
        for (_, _, _, c, l, a) in posicoes_ocupadas
    )

    ocupacao = round(
        min(100, max(0, (volume_usado / volume_veiculo) * 100)),
        2
    )

    # 🔥 usar MESMA lógica do score do ranking
    aproveitamento_volume = ocupacao
    aproveitamento_peso = (
        (peso_acumulado / veic["peso_max"]) * 100
        if veic["peso_max"] > 0 else 0
    )

    balanceamento = 100 - abs(aproveitamento_volume - aproveitamento_peso)
    ociosidade = 100 - aproveitamento_volume
    penalidade = ociosidade * 0.3

    eficiencia = (
        (aproveitamento_volume * 0.4) +
        (aproveitamento_peso * 0.3) +
        (balanceamento * 0.2) -
        (ociosidade * 0.1)
    )

    eficiencia = round(max(0, min(100, eficiencia)), 2)
    
    st.write("### 📊 Resultado da Simulação")
    st.write(f"Veículo: {melhor_veiculo}")
    st.write(f"Volume utilizado: {volume_usado:.2f} m³")
    st.write(f"Ocupação: {ocupacao:.2f}%")
    st.write(f"Caixas alocadas: {caixas_alocadas}")
    st.write(f"Eficiência: {eficiencia:.1f}%")
    st.write(f"Peso total carregado: {peso_acumulado:.2f} kg")
    st.write(f"Capacidade máxima do veículo: {peso_max:.2f} kg")

    if caixas_alocadas < qtd_total_real:
        st.error("⚠️ Nem todas as caixas couberam.")
    else:
        st.success("✅ Todas as caixas foram alocadas.")

    # ============================
    # VISUALIZAÇÃO 3D
    # ============================
    fig = go.Figure()

    cores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for i, item in enumerate(posicoes_ocupadas):
    
        if not isinstance(item, tuple) or len(item) != 6:
            continue
    
        try:
            x0, y0, z0, c, l, a = item
        except Exception as e:
            st.warning(f"Erro no item 3D: {e}")
            continue
    
        fig.add_trace(go.Mesh3d(
            x=[x0, x0+c, x0+c, x0, x0, x0+c, x0+c, x0],
            y=[y0, y0, y0+l, y0+l, y0, y0, y0+l, y0+l],
            z=[z0, z0, z0, z0, z0+a, z0+a, z0+a, z0+a],
            opacity=0.9,
            color=cores[i % len(cores)],
            showscale=False
        ))

    # caixa do veículo
    fig.add_trace(go.Mesh3d(
        x=[0, comp_veic, comp_veic, 0, 0, comp_veic, comp_veic, 0],
        y=[0, 0, larg_veic, larg_veic, 0, 0, larg_veic, larg_veic],
        z=[0, 0, 0, 0, alt_veic, alt_veic, alt_veic, alt_veic],
        opacity=0.05,
        color="gray",
        showscale=False
    ))

    fig.update_layout(
        title=f"Ocupação: {ocupacao:.1f}%",
        scene=dict(aspectmode="data"),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

if isinstance(st.session_state.df_result, pd.DataFrame) and not st.session_state.df_result.empty:
    excel_file = gerar_excel_bytes(
        st.session_state.df_result,
        st.session_state.cargas
    )

    st.download_button(
        label="📥 Baixar Excel",
        data=excel_file,
        file_name="resultado_cubagem.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
