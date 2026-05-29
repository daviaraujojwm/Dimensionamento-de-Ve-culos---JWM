import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
import math


# 🔥 PRIMEIRA COISA
st.set_page_config(
    page_title="Cubagem de Veículos - JWM",
    layout="wide"
)

MAX_CAIXAS = 300
MAX_CAIXAS_3D = 200
MAX_ITERACOES = 12000
MAX_GRID = 12000
MAX_RENDER_3D = 80
MAX_ORIENTACOES = 6

st.markdown("""
<style>
/* ============================
   FUNDO
============================ */
.stApp {
    background-image: url("https://raw.githubusercontent.com/daviaraujojwm/Dimensionamento-de-Ve-culos---JWM/main/tela%20de%20fundo.png");
    background-size: cover;
    background-position: center;
    background-attachment: scroll;
}

/* ✅ overlay mais leve e estável */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.22); /* ligeiramente mais escuro p/ contraste */
    z-index: 0;
}

/* ============================
   CONTAINER PRINCIPAL (CARD)
============================ */
.block-container {
    position: relative;
    z-index: 1;

    max-width: 95%;
    height: auto;

    margin: 60px auto 20px auto;

    padding: 20px 25px;

    background: rgba(255, 255, 255, 0.085);
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);

    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 6px 30px rgba(0,0,0,0.22);

    overflow: visible;
}

.main .block-container {
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}

/* ============================
   TEXTOS
============================ */
label {
    color: #f1f1f1 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.6);
    font-weight: 500;
}
/* ============================
   INPUTS
============================ */
.stTextInput input, 
.stNumberInput input {
    background: rgba(255,255,255,0.98);
    color: #111;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid rgba(0,0,0,0.15);
}

/* ============================
   ESPAÇAMENTO ENTRE ELEMENTOS
============================ */
.stTextInput, 
.stNumberInput, 
.stSelectbox {
    margin-bottom: 18px;
}

h1, h2, h3 {
    color: #ffffff;
    text-shadow: 0 2px 6px rgba(0,0,0,0.5);
    margin-top: 25px;
    margin-bottom: 15px;
}

/* ============================
   BOTÕES
============================ */
.stButton button {
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton button:hover {
    transform: scale(1.03);
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

/* ============================
   TÍTULO GRADIENTE
============================ */
.titulo-gradient {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #ff0000, #cc0000, #990000);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ============================
   RESPONSIVIDADE
============================ */
@media (max-width: 768px) {
    .block-container {
        padding: 20px !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ============================
# SESSION STATE INIT
# ============================

if "df_result" not in st.session_state or not isinstance(st.session_state.df_result, pd.DataFrame):
    st.session_state.df_result = pd.DataFrame(columns=[
        "Veículo",
        "Status",
        "Motivo",
        "Aproveitamento (%)",
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

    {"nome": "Fiorino", "largura": 1.000, "comprimento": 1.200, "altura": 1.000, "peso_max": 500, "custo": 1},

    {"nome": "Van Utilitário", "largura": 1.000, "comprimento": 1.600, "altura": 1.000, "peso_max": 500, "custo": 2},

    {"nome": "HR Baú", "largura": 1.700, "comprimento": 3.000, "altura": 1.900, "peso_max": 1300, "custo": 3},

    {"nome": "HR Aberto", "largura": 1.800, "comprimento": 3.000, "altura": 2.000, "peso_max": 1300, "custo": 3},

    {"nome": "VUC Baú", "largura": 1.800, "comprimento": 3.100, "altura": 2.000, "peso_max": 2500, "custo": 4},

    {"nome": "Veículo 3/4 Aberto", "largura": 2.100, "comprimento": 5.000, "altura": 2.300, "peso_max": 3000, "custo": 5},

    {"nome": "Veículo 3/4 Baú", "largura": 2.100, "comprimento": 5.000, "altura": 2.300, "peso_max": 3000, "custo": 5},

    {"nome": "Toco Aberto", "largura": 2.200, "comprimento": 6.000, "altura": 2.700, "peso_max": 6000, "custo": 6},

    {"nome": "Toco Baú", "largura": 2.200, "comprimento": 6.000, "altura": 2.700, "peso_max": 6000, "custo": 6},

    {"nome": "Truck Aberto", "largura": 2.400, "comprimento": 8.000, "altura": 2.800, "peso_max": 12000, "custo": 7},

    {"nome": "Truck Baú", "largura": 2.400, "comprimento": 8.000, "altura": 2.800, "peso_max": 12000, "custo": 7},

    {"nome": "Bitruck Sider", "largura": 2.400, "comprimento": 10.000, "altura": 2.700, "peso_max": 18000, "custo": 8},

    {"nome": "Bi-Truck Aberto", "largura": 2.400, "comprimento": 10.000, "altura": 2.800, "peso_max": 17000, "custo": 8},

    {"nome": "Bi-Truck Baú", "largura": 2.400, "comprimento": 10.000, "altura": 2.800, "peso_max": 17000, "custo": 8},

    {"nome": "Carreta Sider", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 24000, "custo": 10},

    {"nome": "Carreta Grade Baixa", "largura": 2.400, "comprimento": 12.400, "altura": 2.700, "peso_max": 24000, "custo": 10},

    {"nome": "Carreta Wanderleia", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 27000, "custo": 10},

    {"nome": "Wanderleia Carga Seca", "largura": 2.400, "comprimento": 14.400, "altura": 2.700, "peso_max": 27000, "custo": 10},

    {"nome": "Carreta Wanderleia Sider", "largura": 2.600, "comprimento": 15.200, "altura": 2.800, "peso_max": 41500, "custo": 11},

    {"nome": "Carreta Wanderleia Aberta", "largura": 2.600, "comprimento": 18.150, "altura": 2.900, "peso_max": 46000, "custo": 11},

    {"nome": "Carreta Rodo Trem", "largura": 2.400, "comprimento": 12.000, "altura": 2.700, "peso_max": 74000, "custo": 12}

]

# ============================
# DATAFRAME DE VEÍCULOS (ESSENCIAL)
# ============================
@st.cache_data(show_spinner=False)
def get_veiculos():

    df = pd.DataFrame(lista_veiculos)

    df["Volume Bruto"] = (
        df["largura"]
        * df["comprimento"]
        * df["altura"]
    )

    df["Area Piso"] = (
        df["largura"]
        * df["comprimento"]
    )

    df.rename(
        columns={"nome": "Veículo"},
        inplace=True
    )

    df["fator"] = (
        df["Veículo"].apply(get_fator)
    )

    df["eficiencia"] = (
        df["Veículo"].apply(get_eficiencia)
    )

    return df
    
# ============================
# FUNÇÃO GLOBAL DE FATOR
# ============================
def get_fator(nome):
    if " + " in nome:
        return 0.82

    if "Fiorino" in nome or "Van" in nome:
        return 0.98
    elif "HR" in nome or "VUC" in nome:
        return 0.92
    elif "3/4" in nome or "Toco" in nome:
        return 0.87
    else:
        return 0.82


def get_eficiencia(nome):
    if "Carreta" in nome:
        return 0.85
    elif "Bi-Truck" in nome or "Bitruck" in nome:
        return 0.82
    elif "Truck" in nome:
        return 0.78
    elif "3/4" in nome or "Toco" in nome:
        return 0.77
    elif "HR" in nome or "VUC" in nome:
        return 0.75
    else:
        return 0.72

def categoria_veiculo(nome):

    if "Fiorino" in nome:
        return "FIORINO"

    elif "Van" in nome:
        return "VAN"

    elif "HR" in nome:
        return "HR"

    elif "VUC" in nome:
        return "VUC"

    elif "3/4" in nome:
        return "TRES_QUARTOS"

    elif "Toco" in nome:
        return "TOCO"

    elif "Bi-Truck" in nome or "Bitruck" in nome:
        return "BITRUCK"

    elif "Truck" in nome:
        return "TRUCK"

    elif "Carreta" in nome or "Wanderleia" in nome:
        return "CARRETA"

    else:
        return "OUTRO"

# =====================================
# DATAFRAME GLOBAL DE VEÍCULOS
# =====================================
df_veiculos = get_veiculos()

# =====================================
# HELPER GLOBAL DE VOLUME
# =====================================
def volume_veiculo(veic):
    return (
        veic["largura"]
        * veic["comprimento"]
        * veic["altura"]
    )

def capacidade_veiculo(veic, empilhavel=True):

    fator = get_fator(veic["Veículo"])
    eficiencia = get_eficiencia(veic["Veículo"])

    if empilhavel:
        base = volume_veiculo(veic)
    else:
        base = veic["largura"] * veic["comprimento"]

    return base * fator * eficiencia

# ============================
# SESSION STATE
# ============================
if "cargas" not in st.session_state:
    st.session_state.cargas = []

# ============================
# TÍTULO
# ============================
col1, col2 = st.columns([6, 1])
with col1:
    st.title("Dimensionamento de Veículos - JWM")
with col2:
    try:
        st.image("JWM.png", width=80)
    except Exception:
        st.warning("Logo JWM não encontrada.")
# ============================
# INPUTS CARGA
# ============================

st.subheader("📦 Adicionar carga")

col1, col2, col3, col4, col5 = st.columns(
    [1.2, 1.2, 1.2, 1.2, 0.8],
    gap="large"
)

with col1:
    comp_txt = st.text_input(
        "Comprimento (m)",
        key="comp",
        placeholder="ex: 1,20 ou 1.20"
    )

with col2:
    larg_txt = st.text_input(
        "Largura (m)",
        key="larg",
        placeholder="ex: 0,80 ou 0.80"
    )

with col3:
    alt_txt = st.text_input(
        "Altura (m)",
        key="alt",
        placeholder="ex: 1,00"
    )

with col4:
    peso_txt = st.text_input(
        "Peso unitário (kg)",
        key="peso",
        placeholder="ex: 15,5"
    )

with col5:
    qtd = st.number_input(
    "Quantidade:",
    min_value=1,
    value=1,
    step=1,
    key="qtd"
)



def parse_float(valor):
    try:
        if valor is None:
            return None
        valor = str(valor).strip().replace(",", ".")
        if valor == "":
            return None
        return round(float(valor), 4)
    except:
        return None

# 🔥 SÓ DEPOIS DISSO
comp = parse_float(comp_txt)
larg = parse_float(larg_txt)
alt = parse_float(alt_txt)
peso = parse_float(peso_txt)

# VALIDAÇÃO DE INPUTS

def validar_inputs(comp, larg, alt, peso, qtd=None):
    """
    Valida dimensões, peso e quantidade da carga.
    Retorna lista de erros (vazia se válido).
    """

    erros = []

    def invalido(valor):
        try:
            return valor is None or float(valor) <= 0
        except Exception:
            return True

    # Comprimento
    if invalido(comp):
        erros.append("Comprimento inválido")
    elif comp < 0.05:
        erros.append("Comprimento muito pequeno")

    # Largura
    if invalido(larg):
        erros.append("Largura inválida")
    elif larg < 0.01:
        erros.append("Largura muito pequena")

    # Altura
    if invalido(alt):
        erros.append("Altura inválida")
    elif alt < 0.01:
        erros.append("Altura muito pequena")

    # Peso
    if invalido(peso):
        erros.append("Peso inválido")

    # Quantidade
    if qtd is not None:
        try:
            if int(qtd) <= 0:
                erros.append("Quantidade inválida")
        except Exception:
            erros.append("Quantidade inválida")

    return erros
#.

col1, col2, col3, col4, col5 = st.columns(
    [1.2, 1.2, 1.2, 1.2, 0.8],
    gap="large"
)

erros = validar_inputs(comp, larg, alt, peso, qtd)

if erros and (comp_txt or larg_txt or alt_txt or peso_txt):
    st.error(" | ".join(erros))

# aviso de performance
if qtd > 1000:
    st.warning("⚠ Quantidade muito alta pode impactar a performance.")

total_caixas = sum(
    int(c["Quantidade"])
    for c in st.session_state.cargas
) + int(qtd)

if total_caixas > MAX_CAIXAS:
    st.warning(f"⚠ Máximo recomendado para cálculo assertivo: {MAX_CAIXAS} caixas.")

if qtd > 5000:
    st.error("❌ Quantidade máxima por item: 5000")
    st.stop()

pode_adicionar = len(erros) == 0

# ========================================
# ✅ TOGGLE DE EMPILHAMENTO (FORA DO BOTÃO)
# ========================================

empilhavel = st.toggle(
    "📦 Permitir empilhamento (cálculo 3D)",
    value=True
)

# ========================================
# ✅ BOTÃO DE ADICIONAR CARGA
# ========================================

if st.button("➕ Adicionar carga", disabled=not pode_adicionar):
    st.session_state.cargas.append({
        "Comprimento (m)": comp,
        "Largura (m)": larg,
        "Altura (m)": alt,
        "Peso unitário (kg)": peso,
        "Quantidade": qtd,
        "Volume total (m³)": comp * larg * alt * qtd,
        "Peso total (kg)": peso * qtd
    })

    for k in ["comp", "larg", "alt", "peso"]:
        st.session_state[k] = ""
    
    st.session_state["qtd"] = 1
    
    st.rerun()
    
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
        key="editor_cargas",
        hide_index=True
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
                        if pd.isna(row["Comprimento (m)"]):
                            raise ValueError("Campo vazio.")
                        comp = float(row["Comprimento (m)"])
                        larg = float(row["Largura (m)"])
                        alt = float(row["Altura (m)"])
                        peso = float(row["Peso unitário (kg)"])
                    except Exception as e:
                        raise ValueError("Valores inválidos na tabela.")
                    
                    if comp <= 0 or larg <= 0 or alt <= 0:
                        raise ValueError("Dimensões inválidas.")
                    
                    if peso <= 0:
                        raise ValueError("Peso inválido.")
                                        
                    vol_unit = comp * larg * alt
                    
                    try:
                        qtd_row = int(row["Quantidade"])
                    except Exception as e:
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
            if not df_editado.empty:
            
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
@st.cache_data(show_spinner=False)
def expand_cargas_unitarias(cargas, limite=MAX_CAIXAS):
    """
    Expande cargas agregadas em unidades individuais.
    Retorna lista de caixas unitárias.
    """
    lista = []

    for c in cargas:
        try:
            qtd = int(c["Quantidade"])
            comp = float(c["Comprimento (m)"])
            larg = float(c["Largura (m)"])
            alt = float(c["Altura (m)"])
            peso = float(c["Peso unitário (kg)"])
        except Exception as e:
            continue

        if qtd <= 0 or min(comp, larg, alt, peso) <= 0:
            continue
        if qtd > 2000:
            qtd = 2000

        for _ in range(qtd):
            if len(lista) >= limite:
                return lista

            volume = comp * larg * alt

            if volume <= 0:
                continue
            
            densidade = peso / volume if volume > 0 else 0
            
            lista.append({
                "comp": comp,
                "larg": larg,
                "alt": alt,
                "peso": peso,
                "densidade": densidade,
                "volume": comp * larg * alt
            })

    return lista

def agrupar_em_pallets(cargas_unit, max_por_pallet=10):

    pallets = []

    grupo = []

    for caixa in cargas_unit:

        grupo.append(caixa)

        if len(grupo) >= max_por_pallet:
            pallets.append(grupo)
            grupo = []

    if grupo:
        pallets.append(grupo)

    return pallets

def calcular_totais(cargas, empilhavel=True):

    area = 0
    volume = 0
    peso = 0

    for c in cargas:
        qtd = float(c.get("Quantidade", 0))

        comp = float(c["Comprimento (m)"])
        larg = float(c["Largura (m)"])
        alt = float(c["Altura (m)"])
        peso_unit = float(c["Peso unitário (kg)"])

        area += comp * larg * qtd
        volume += comp * larg * alt * qtd
        peso += peso_unit * qtd

    if empilhavel:
        return volume, peso
    else:
        return area, peso

def calcular_totais_reais(cargas, empilhavel=True):

    volume = 0
    area = 0
    peso = 0

    for c in cargas:

        qtd = int(c["Quantidade"])

        comp = float(c["Comprimento (m)"])
        larg = float(c["Largura (m)"])
        alt = float(c["Altura (m)"])
        peso_unit = float(c["Peso unitário (kg)"])

        volume += comp * larg * alt * qtd
        area += comp * larg * qtd
        peso += peso_unit * qtd

    if empilhavel:
        return volume, peso
    else:
        return area, peso

def excede_capacidade(
    peso_atual,
    volume_atual,
    peso_carga,
    volume_carga,
    peso_max,
    volume_max
):
    """
    Retorna True se a inclusão da carga exceder
    peso ou volume do veículo.
    """
    if peso_atual + peso_carga > peso_max:
        return True

    if volume_atual + volume_carga > volume_max:
        return True

    return False
    
@st.cache_data(show_spinner=False)
def calcular_score(volume_total, capacidade, peso_total, peso_max):

    if capacidade <= 0 or peso_max <= 0:
        return 0

    ocupacao_volume = volume_total / capacidade
    ocupacao_peso = peso_total / peso_max

    equilibrio = max(0, 1 - abs(ocupacao_volume - ocupacao_peso))

    score = (
        ocupacao_volume * 55
        + ocupacao_peso * 30
        + equilibrio * 15
    )

    if ocupacao_volume < 0.15:
        score -= 35
    elif ocupacao_volume < 0.30:
        score -= 18

    if ocupacao_volume > 0.95:
        score -= 20

    if ocupacao_peso > 0.95:
        score -= 20

    return round(max(1, min(100, score)), 2)

def escolher_veiculo_unico_completo(cargas_unit, df_veiculos, cargas, empilhavel):

    if not cargas_unit:
        return None

    valor_total, peso_total = calcular_totais_reais(
        cargas,
        empilhavel
    )

    melhor_score = -1
    melhor_veiculo = None

    df_ordenado = df_veiculos.sort_values(
        by="Volume Bruto"
    )

    max_comp = max(c["comp"] for c in cargas_unit)
    max_larg = max(c["larg"] for c in cargas_unit)
    max_alt  = max(c["alt"] for c in cargas_unit)

    for _, veic in df_ordenado.iterrows():

        # ✅ BLOQUEIO FÍSICO
        dim_carga = sorted([
            max_comp,
            max_larg,
            max_alt
        ])
        
        dim_veiculo = sorted([
            veic["comprimento"],
            veic["largura"],
            veic["altura"]
        ])
        
        if any(c > v for c, v in zip(dim_carga, dim_veiculo)):
            continue

        fator = get_fator(veic["Veículo"])
        eficiencia = get_eficiencia(veic["Veículo"])
        
        capacidade = capacidade_veiculo(veic, empilhavel)

        peso_max = veic["peso_max"]
        
        if valor_total > capacidade * 1.03:
            continue
        
        if peso_total > peso_max:
            continue

        aproveitamento_peso = (
        (peso_total / peso_max) * 100
        if peso_max > 0 else 0
        )
        
        aproveitamento_volume = (
        (valor_total / capacidade) * 100
        if capacidade > 0 else 0
        )
        
        # evita veículos absurdamente vazios
        if aproveitamento_volume < 18:
            continue
        
        if aproveitamento_peso < 3:
            continue
        # evita veículos desbalanceados
        if (
            aproveitamento_peso > 85
            and aproveitamento_volume < 35
        ):
            continue

        capacidade_bruta = (
        volume_veiculo(veic)
        )
        
        # =========================================
        # PENALIDADE DE OCIOSIDADE
        # =========================================
        
        ocupacao_real = (
            valor_total / capacidade_bruta
            if capacidade_bruta > 0 else 0
        )
        
        # =========================================
        # PENALIDADE INTELIGENTE
        # =========================================
        
        if ocupacao_real < 0.10:
        
            score_penalidade = 45
        
        elif ocupacao_real < 0.20:
        
            score_penalidade = 30
        
        elif ocupacao_real < 0.35:
        
            score_penalidade = 15
        
        else:
        
            score_penalidade = 0
        
        # bônus para veículos muito bem aproveitados
        if ocupacao_real > 0.80:
            score_penalidade -= 10

        # =========================================
        # VALIDAÇÃO DE PISO (NOVA)
        # =========================================
        
        if not empilhavel:
        
            if not cabe_no_piso_heuristica(
                cargas_unit,
                veic["comprimento"],
                veic["largura"],
                veic["altura"]
            ):
                continue
        # =========================================
        # VALIDAÇÃO FÍSICA
        # =========================================
        
        if empilhavel:
        
            cargas_reduzidas = reduzir_cargas_para_simulacao(
                [
                    {
                        "Comprimento (m)": c["comp"],
                        "Largura (m)": c["larg"],
                        "Altura (m)": c["alt"],
                        "Peso unitário (kg)": c["peso"],
                        "Quantidade": 1
                    }
                    for c in cargas_unit
                ],
                MAX_CAIXAS_3D
            )
        
            posicoes, caixas_alocadas, volume_usado_3d, peso_usado_3d = simular_empilhamento_3d(
                cargas_reduzidas,
                veic,
                len(cargas_reduzidas)
            )
        
            if caixas_alocadas < len(cargas_reduzidas):
                continue
        
        else:
        
            caixas_alocadas = len(cargas_unit)
        
        score = calcular_score(
            valor_total,
            capacidade,
            peso_total,
            peso_max
        ) - score_penalidade
        
        ocupacao_real = valor_total / capacidade_bruta if capacidade_bruta > 0 else 0
        custo_operacional = veic.get("custo", 5)
        
        # =========================================
        # BÔNUS COMPACTO
        # =========================================
        
        bonus_compacto = (
            100 / capacidade_bruta
        )
        
        score += bonus_compacto
        
        # Penaliza trabalhar no limite
        if aproveitamento_volume > 95:
            score -= 25
        elif aproveitamento_volume > 90:
            score -= 12
        
        # Penaliza custo
        score -= custo_operacional * 1.8
        
        # Bônus para ocupação ideal
        if 0.55 <= ocupacao_real <= 0.85:
            score += 12
        elif 0.45 <= ocupacao_real <= 0.90:
            score += 6
        
        # Bônus por validação 3D
        score += 10
        
        score = max(1, min(100, score))

        if score > melhor_score:
            melhor_score = score
            melhor_veiculo = veic

    return melhor_veiculo

def identificar_fator_limitante(
    volume_usado, volume_max,
    peso_usado, peso_max,
    margem=5
):
    """
    Identifica se a limitação do veículo foi por PESO ou VOLUME.
    """
    perc_vol = (volume_usado / volume_max) * 100 if volume_max > 0 else 0
    perc_peso = (peso_usado / peso_max) * 100 if peso_max > 0 else 0

    if perc_peso > perc_vol + margem:
        return "PESO"
    elif perc_vol > perc_peso + margem:
        return "VOLUME"
    else:
        return "EQUILIBRADO"

def gerar_justificativa_veiculo(
    veiculo,
    valor_total,
    peso_total,
    volume_max,
    peso_max,
    score,
    caixas_alocadas,
    qtd_total_real
):
    aproveitamento_volume = (valor_total / volume_max) * 100
    aproveitamento_peso = (peso_total / peso_max) * 100
    equilibrio = 100 - abs(aproveitamento_volume - aproveitamento_peso)

    texto = (
        f"O veículo **{veiculo}** foi selecionado por apresentar o melhor "
        f"equilíbrio técnico entre volume e peso.\n\n"
        f"• Ocupação da capacidade: {aproveitamento_volume:.1f}%\n"
        f"• Utilização de peso: {aproveitamento_peso:.1f}%\n"
        f"• Índice de equilíbrio: {equilibrio:.1f}%\n"
        f"• Score técnico final: {score:.1f}\n\n"
    )

    if caixas_alocadas >= qtd_total_real:
        texto += (
            "A simulação tridimensional confirmou que **100% das caixas "
            "foram fisicamente alocadas**, validando a escolha operacional."
        )
    else:
        texto += (
            "Apesar da viabilidade teórica, a simulação tridimensional "
            "indicou restrições físicas de empilhamento."
        )

    return texto

def reduzir_cargas_para_simulacao(cargas, limite):
    """
    Reduz o número de caixas para simulação 3D
    preservando proporções e dimensões.
    """
    todas = expand_cargas_unitarias(
        cargas,
        limite=max(limite * 3, 5000)
    )

    if len(todas) <= limite:
        return todas

    fator = len(todas) / limite
    reduzidas = []

    for i in range(limite):
        idx = int(i * fator)
        reduzidas.append(todas[idx])

    return reduzidas


    
# ============================
# EXPORTAR RESULTADOS PARA EXCEL
# ============================
@st.cache_data(show_spinner=False)
def gerar_excel_bytes(df_result, cargas):

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


def cabe_no_piso_heuristica(items, comp_v, larg_v, alt_v):
    """
    Heurística simplificada de empacotamento 2D + camadas.
    Retorna True se a heurística indicar que cabe,
    False se claramente não cabe.
    """

    if not items:
        return True

    # Ordena as caixas maiores primeiro
    items = sorted(
        items,
        key=lambda x: x["comp"] * x["larg"] * x["alt"],
        reverse=True
    )

    camadas = []
    altura_usada = 0

    for it in items:

        colocado = False

        # Testa duas orientações no piso (rotação)
        for comp_i, larg_i in (
            (it["comp"], it["larg"]),
            (it["larg"], it["comp"])
        ):

            # Não cabe no piso
            if comp_i > comp_v or larg_i > larg_v:
                continue

            # Tenta encaixar na camada existente
            for camada in camadas:
                if camada["len"] + comp_i <= comp_v:
                    camada["len"] += comp_i
                    colocado = True
                    break

            if colocado:
                break

        # Não foi possível colocar a caixa
        if not colocado:
        
            comp_novo = min(it["comp"], it["larg"])
        
            comprimento_usado = sum(
                camada["len"]
                for camada in camadas
            )
        
            if comprimento_usado + comp_novo <= comp_v:
        
                camadas.append({
                    "len": comp_novo
                })
        
                colocado = True

        if not colocado:
            return False

    return True

GRID_SIZE = 1.0

def gerar_chave_grid(x, y, z):
    return (
        int(x // GRID_SIZE),
        int(y // GRID_SIZE),
        int(z // GRID_SIZE)
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


def tem_base(nova, ocupadas, suporte_min=0.7):

    x, y, z, dx, dy, dz = nova

    # chão
    if z == 0:
        return True

    area_caixa = dx * dy

    for ox, oy, oz, odx, ody, odz in ocupadas:

        # precisa estar exatamente sobre
        if abs((oz + odz) - z) > 0.001:
            continue

        overlap_x = max(
            0,
            min(x + dx, ox + odx) - max(x, ox)
        )

        overlap_y = max(
            0,
            min(y + dy, oy + ody) - max(y, oy)
        )

        area_suporte = overlap_x * overlap_y

        if area_suporte >= area_caixa * suporte_min:
            return True

    return False

def calcular_centro_massa(posicoes):
    if not posicoes:
        return 0

    soma = 0
    peso_total = 0

    for x, y, z, c, l, a in posicoes:

        centro_x = x + (c / 2)

        volume = c * l * a

        soma += centro_x * volume
        peso_total += volume

    if peso_total == 0:
        return 0

    return soma / peso_total
    
def simular_empilhamento_3d(
    cargas_unitarias,
    veiculo,
    qtd_total_real,
    limite_iter=MAX_ITERACOES,
    max_grid=MAX_GRID
):
    comp_veic = veiculo["comprimento"]
    larg_veic = veiculo["largura"]
    alt_veic = veiculo["altura"]
    peso_max = veiculo["peso_max"]
    
    posicoes_ocupadas = []
    grid_ocupacao = {}
    caixas_alocadas = 0
    peso_acumulado = 0

    contador = 0
    estourou_limite = False

    cargas_unitarias = sorted(
        cargas_unitarias,
        key=lambda x: (
            -x["densidade"],
            -(x["comp"] * x["larg"]),
            -x["volume"]
        )
    )

    qtd_total_real = len(cargas_unitarias)

    free_spaces = [
    (0, 0, 0, comp_veic, larg_veic, alt_veic)
    ]
    
    for item in cargas_unitarias:
        contador += 1

        # evita simular caixas impossíveis
        if (
            item["comp"] > comp_veic
            or item["larg"] > larg_veic
            or item["alt"] > alt_veic
        ):
            continue

        if estourou_limite:
            break

        if item["peso"] <= 0:
            continue

        # =========================================
        # ORIENTAÇÕES ÚNICAS (REMOVE DUPLICADAS)
        # =========================================
        
        orientacoes = list(set([
            (
                round(item["comp"], 4),
                round(item["larg"], 4),
                round(item["alt"], 4)
            ),
            (
                round(item["comp"], 4),
                round(item["alt"], 4),
                round(item["larg"], 4)
            ),
            (
                round(item["larg"], 4),
                round(item["comp"], 4),
                round(item["alt"], 4)
            ),
            (
                round(item["larg"], 4),
                round(item["alt"], 4),
                round(item["comp"], 4)
            ),
            (
                round(item["alt"], 4),
                round(item["comp"], 4),
                round(item["larg"], 4)
            ),
            (
                round(item["alt"], 4),
                round(item["larg"], 4),
                round(item["comp"], 4)
            )
        ]))
        
        orientacoes = orientacoes[:MAX_ORIENTACOES]
        for comp_o, larg_o, alt_o in orientacoes:

            try:
                x_max = int(comp_veic // comp_o)
                y_max = int(larg_veic // larg_o)
                z_max = int(alt_veic // alt_o)
            except Exception as e:
                continue

            grid_size = x_max * y_max * z_max
            if grid_size <= 0:
                continue

            if grid_size > max_grid:
                fator = (grid_size / max_grid) ** (1/3)
                x_max = max(1, int(x_max / fator))
                y_max = max(1, int(y_max / fator))
                z_max = max(1, int(z_max / fator))

            # =========================================
            # STEP DINÂMICO (MELHORA PERFORMANCE)
            # =========================================
            
            menor_dim = min(comp_o, larg_o)
            
            volume_item = comp_o * larg_o * alt_o
        
            if volume_item >= 3:
                step = 2
            else:
                step = 1

            # ================================
            # ✅ LOOP EM CAMADAS (Z FORÇADO)
            # ================================
            
            alturas_camadas = [i * alt_o for i in range(z_max)]
            if contador > limite_iter:
                estourou_limite = True
                break
            
            colocado = False
            
            for idx, espaco in enumerate(free_spaces):
        
                sx, sy, sz, scomp, slarg, salt = espaco
        
                # cabe no espaço?
                if (
                    comp_o <= scomp and
                    larg_o <= slarg and
                    alt_o <= salt
                ):
        
                    nova = (
                        sx,
                        sy,
                        sz,
                        comp_o,
                        larg_o,
                        alt_o
                    )
        
                    if colide(nova, posicoes_ocupadas):
                        continue
                    
                    if not tem_base(nova, posicoes_ocupadas):
                        continue
                    
                    # valida peso máximo do veículo
                    
                    if peso_acumulado + item["peso"] > peso_max:
                        continue
                    
                    posicoes_ocupadas.append(nova)

                    chave = gerar_chave_grid(sx, sy, sz)

                    if chave not in grid_ocupacao:
                        grid_ocupacao[chave] = []
                    
                    grid_ocupacao[chave].append(nova)
        
                    caixas_alocadas += 1
                    peso_acumulado += item["peso"]
        
                    colocado = True
        
                    # remove espaço usado
                    free_spaces.pop(idx)
        
                    # espaço lateral
                    free_spaces.append((
                        sx + comp_o,
                        sy,
                        sz,
                        scomp - comp_o,
                        slarg,
                        salt
                    ))
        
                    # espaço frontal
                    free_spaces.append((
                        sx,
                        sy + larg_o,
                        sz,
                        comp_o,
                        slarg - larg_o,
                        salt
                    ))
        
                    # espaço superior
                    free_spaces.append((
                        sx,
                        sy,
                        sz + alt_o,
                        comp_o,
                        larg_o,
                        max(0, salt - alt_o)
                    ))
                    free_spaces = [
                        s for s in free_spaces
                        if s[3] > 0 and s[4] > 0 and s[5] > 0
                    ]
                    
                    # evita explosão
                    if len(free_spaces) > 1500:
                    
                        free_spaces = sorted(
                            free_spaces,
                            key=lambda s: s[3] * s[4] * s[5],
                            reverse=True
                        )[:1500]
        
                    break
        
            if colocado:
                break

    volume_usado = sum(c * l * a for (_, _, _, c, l, a) in posicoes_ocupadas)
    centro = calcular_centro_massa(posicoes_ocupadas)

    # evita concentração extrema
    if centro > comp_veic * 0.80:
        return [], 0, 0, 0

    return posicoes_ocupadas, caixas_alocadas, volume_usado, peso_acumulado

def gerar_cenarios_multi(cargas, df_veiculos, empilhavel=True, max_opcoes=5):

    volume_total, peso_total = calcular_totais_reais(
        cargas,
        empilhavel
    )

    cenarios = []

    veiculos_ordenados = df_veiculos.sort_values(
        by="Volume Bruto",
        ascending=False
    )

    for _, veic in veiculos_ordenados.iterrows():

        nome = veic["Veículo"]

        # eficiência por tipo
        eficiencia = get_eficiencia(nome)

        fator = get_fator(nome)

        if empilhavel:
            cap_vol = (
                volume_veiculo(veic)
            )
        else:
            cap_vol = (
                veic["largura"]
                * veic["comprimento"]
            )

        cap_vol *= eficiencia * fator
        cap_peso = veic["peso_max"] * fator

        qtd_por_volume = math.ceil(volume_total / cap_vol)
        qtd_por_peso = math.ceil(peso_total / cap_peso)

        qtd = max(qtd_por_volume, qtd_por_peso)

        # =========================================
        # AJUSTE DE FOLGA OPERACIONAL
        # =========================================
        
        if qtd >= 2:
        
            ocupacao_media = max(
                volume_total / (cap_vol * qtd),
                peso_total / (cap_peso * qtd)
            )
        
            # evita veículos trabalhando no limite
            if ocupacao_media > 0.92:
                qtd += 1

        if qtd <= 1:
            continue
        
        # evita explosões absurdas
        if qtd > 50:
            continue
        
        if qtd >= 3:
            if not ("Carreta" in nome or "Bi-Truck" in nome or "Bitruck" in nome):
                continue

        aproveitamento_vol = min(1, volume_total / (cap_vol * qtd))
        
        aproveitamento_peso = min(1, peso_total / (cap_peso * qtd))
        
        if aproveitamento_vol < 0.02:
            continue
        
        if aproveitamento_peso < 0.1 and qtd >= 2:
            continue

                
        # 🔥 NOVA INTELIGÊNCIA
        fator_limitante = "VOLUME" if aproveitamento_vol > aproveitamento_peso else "PESO"

        # penaliza muitos veículos
        penalidade_qtd = (qtd - 1) * 15

        bonus_grande = 0
        
        if "Carreta" in nome:
            bonus_grande = 15
        elif "Bi-Truck" in nome or "Bitruck" in nome:
            bonus_grande = 10
        elif "Truck" in nome:
            bonus_grande = 5
        
        score = (
            (aproveitamento_vol * 50) +
            (aproveitamento_peso * 30) +
            ((1 - abs(aproveitamento_vol - aproveitamento_peso)) * 20)
        ) - penalidade_qtd + bonus_grande

        # ✅ CAPACIDADE REAL DO VEÍCULO (SEM FATOR/EFICIÊNCIA)
        cap_vol_bruto = (
            volume_veiculo(veic)
        )
        
        peso_bruto = veic["peso_max"]
        
        # ✅ EXPLICAÇÃO CORRIGIDA
        explicacao = (
            f"A carga exige múltiplos veículos devido ao {fator_limitante.lower()} elevado.\n\n"
            f"• Volume total ocupa {(volume_total / cap_vol_bruto) * 100:.1f}% de um único veículo\n"
            f"• Peso total ocupa {(peso_total / peso_bruto) * 100:.1f}% da capacidade\n"
            f"• Isso equivale a aproximadamente {volume_total / cap_vol:.1f} veículos completos\n\n"
            f"✅ Configuração sugerida: {qtd}x {nome}\n"
            f"🔎 Fator limitante: {fator_limitante}"
        )
        cenarios.append({
            "Veículo": nome,
            "Configuração": f"{qtd}x {nome}",
            "Aproveitamento (%)": round(aproveitamento_vol * 100, 1),
            "Aproveitamento Peso (%)": round(aproveitamento_peso * 100, 1),
            "Score": round(score, 2),
            "Motivo": explicacao
        })

    df = pd.DataFrame(cenarios)

    if not df.empty:
        df = df.sort_values(by="Score", ascending=False)

    return df.head(max_opcoes)

# =====================================
# NOVA FUNÇÃO (ESTAVA FALTANDO)
# =====================================
def dividir_carga_multi(cargas, df_veiculos, empilhavel=True):

    df_multi = gerar_cenarios_multi(
        cargas,
        df_veiculos,
        empilhavel
    )

    if df_multi.empty:
        return pd.DataFrame()

    # ✅ mantém explicação já calculada em gerar_cenarios_multi
    df_multi["Status"] = "Viável"
    df_multi["Cenário"] = "MULTI"

    return df_multi

def gerar_combinacoes(df_testar, valor_total, peso_total, empilhavel):

    combos = []
    usados = set()

    for i, v1 in df_testar.iterrows():
        for j, v2 in df_testar.iterrows():

            if j < i:
                continue

            chave = tuple(sorted([v1["Veículo"], v2["Veículo"]]))
            categoria_1 = categoria_veiculo(v1["Veículo"])
            categoria_2 = categoria_veiculo(v2["Veículo"])
            
            # evita misturas muito diferentes
            combos_permitidos = [
                ("HR", "VUC"),
                ("VUC", "TRUCK"),
                ("TRUCK", "BITRUCK"),
                ("TRUCK", "CARRETA"),
                ("BITRUCK", "CARRETA")
            ]
            
            if categoria_1 != categoria_2:
                if (categoria_1, categoria_2) not in combos_permitidos and (categoria_2, categoria_1) not in combos_permitidos:
                    continue
                
            if chave in usados:
                continue
            usados.add(chave)

            f1 = get_fator(v1["Veículo"])
            f2 = get_fator(v2["Veículo"])
            
            if empilhavel:
                e1 = get_eficiencia(v1["Veículo"])
                e2 = get_eficiencia(v2["Veículo"])
                
                cap1 = (
                    v1["largura"] * v1["comprimento"] * v1["altura"]
                ) * f1 * e1
                
                cap2 = (
                    v2["largura"] * v2["comprimento"] * v2["altura"]
                ) * f2 * e2
            else:
                cap1 = (v1["largura"] * v1["comprimento"]) * f1
                cap2 = (v2["largura"] * v2["comprimento"]) * f2


            cap_total = cap1 + cap2
            cap_peso = v1["peso_max"] + v2["peso_max"]
            peso_cap = cap_peso

            if valor_total > cap_total * 1.25:
                continue

            if peso_total > peso_cap * 1.3:
                continue

            aproveitamento_vol = valor_total / cap_total * 100
            aproveitamento_peso = peso_total / peso_cap * 100
            
            if aproveitamento_vol < 10:
                continue

            score = (
                (aproveitamento_vol * 0.50)
                + (aproveitamento_peso * 0.25)
                + ((100 - abs(aproveitamento_vol - aproveitamento_peso)) * 0.15)
            )
            
            # penaliza combo
            score -= 10
            
            combos.append({
                "Veículo": f'{v1["Veículo"]} + {v2["Veículo"]}',
                "Status": "Viável",
                "Motivo": "Combo otimizado",
                "Cenário": "COMBO",
                "Aproveitamento (%)": round(aproveitamento_vol, 2),
                "Aproveitamento Peso (%)": round(aproveitamento_peso, 2),
                "Score": round(score, 2)
            })

    return pd.DataFrame(combos)

def executar_calculo(cargas, df_veiculos, selecionados, empilhavel):
    """
    Função central do sistema.
    Responsável por:
    - Calcular viabilidade
    - Ranqueamento
    - Simulação 3D
    - Decidir UNICO ou MULTI
    """

    if not cargas:
        return pd.DataFrame(), {"cenario": None}

    # --------------------------------
    # Seleção dos veículos a testar
    # --------------------------------
    df_testar = (
        df_veiculos[df_veiculos["Veículo"].isin(selecionados)]
        if selecionados else df_veiculos.copy()
    )

    # --------------------------------
    # Totais da carga
    # --------------------------------
    valor_total, peso_total = calcular_totais_reais(
        cargas,
        empilhavel
    )
    
    # --------------------------------
    # Viabilidade básica (peso + volume)
    # --------------------------------
    registros = []

    # 🔒 Dimensões máximas unitárias da carga
    max_comp = max(c["Comprimento (m)"] for c in cargas)
    max_larg = max(c["Largura (m)"] for c in cargas)
    max_alt  = max(c["Altura (m)"] for c in cargas)

    for _, veic in df_testar.iterrows():
        volume_max = volume_veiculo(veic)
        peso_max = veic["peso_max"]
    
        status = "Viável"
        motivo = ""
        
        # =====================================
        # VALIDAÇÃO COM ROTAÇÃO
        # =====================================
        
        dim_carga = sorted([
            max_comp,
            max_larg,
            max_alt
        ])
        
        dim_veiculo = sorted([
            veic["comprimento"],
            veic["largura"],
            veic["altura"]
        ])
        
        if any(
            c > v
            for c, v in zip(dim_carga, dim_veiculo)
        ):
            status = "Inviável"
            motivo = "Dimensão excede"
    
        # 🚫 REGRAS OPERACIONAIS (PESO / CAPACIDADE)
        
        nome = veic["Veículo"]
        
        # capacidade base
        if empilhavel:
            capacidade_base = volume_veiculo(veic)
        else:
            capacidade_base = veic["largura"] * veic["comprimento"]
        
        fator = get_fator(nome)
        eficiencia = get_eficiencia(nome)
        
        capacidade_max = capacidade_base * fator * eficiencia

        if status == "Viável":
            if peso_total > peso_max:
                status = "Inviável"
                motivo = "Excede peso"
            elif valor_total > capacidade_max:
                status = "Inviável"
                motivo = "Excede capacidade"
        elif status == "Inviável":
            # Se já era inviável por dimensão, mantemos, mas garantimos que o peso/capacidade também sejam checados
            if peso_total > peso_max:
                motivo += " + Peso"
            if valor_total > capacidade_max:
                motivo += " + Capacidade"
        
        registros.append({
            "Veículo": veic["Veículo"],
            "Status": status,
            "Motivo": motivo,
            "Volume Máx": volume_max,
            "Peso Máx": peso_max
        })

    df_status = pd.DataFrame(registros)
    
    # ✅ proteção total
    if df_status.empty or not any(df_status["Status"] == "Viável"):
    
        df_multi = dividir_carga_multi(cargas, df_testar, empilhavel)
    
        if not df_multi.empty:
        
            melhor = df_multi.sort_values(by="Score", ascending=False).iloc[[0]]
            
            return melhor, {"cenario": "MULTI"}

        return pd.DataFrame([{
            "Veículo": "Nenhum",
            "Status": "Inviável",
            "Motivo": "Nenhum veículo atende critérios",
            "Aproveitamento (%)": 0,
            "Aproveitamento Peso (%)": 0,
            "Score": 0
        }]), {"cenario": None}
    
    
    # ==========================================
    # ✅ 2. VERIFICA VEÍCULO ÚNICO REAL
    # ==========================================
    
    cargas_unit = expand_cargas_unitarias(
        cargas,
        limite=MAX_CAIXAS
    )
    
    # totais reais da carga
    valor_total_real, peso_total_real = calcular_totais_reais(
        cargas,
        empilhavel
    )
    
    veic_unico = escolher_veiculo_unico_completo(
        cargas_unit,
        df_testar,
        cargas,
        empilhavel
    )
        
    # ==================================================
    # PRIORIZA O MENOR VEÍCULO COMPATÍVEL (COM FILTRO)
    # ==================================================

    if veic_unico is not None:

        fator = get_fator(veic_unico["Veículo"])
        eficiencia = get_eficiencia(veic_unico["Veículo"])

        if empilhavel:
            capacidade = (
                veic_unico["largura"]
                * veic_unico["comprimento"]
                * veic_unico["altura"]
            ) * fator * eficiencia
        else:
            capacidade = (
                veic_unico["largura"]
                * veic_unico["comprimento"]
            ) * fator * eficiencia

        aproveitamento_vol = min(100, (valor_total / capacidade) * 100)
        aproveitamento_peso = min(100, (peso_total / veic_unico["peso_max"]) * 100)

        if aproveitamento_vol >= 15:

            score = calcular_score(
                valor_total,
                capacidade,
                peso_total,
                veic_unico["peso_max"]
            )

            return pd.DataFrame([{
                "Veículo": veic_unico["Veículo"],
                "Status": "Viável",
                "Motivo": "Melhor aproveitamento geral",
                "Cenário": "UNICO",
                "Aproveitamento (%)": round(aproveitamento_vol, 2),
                "Aproveitamento Peso (%)": round(aproveitamento_peso, 2),
                "Score": score
            }]), {"cenario": "UNICO"}

    # ==========================
    # ✅ RANKING
    # ==========================
    ranking = []
    
    for _, veic in df_testar.iterrows():
        # ✅ 🔥 BLOQUEIO FÍSICO REAL
        dim_carga = sorted([
            max_comp,
            max_larg,
            max_alt
        ])
        
        dim_veiculo = sorted([
            veic["comprimento"],
            veic["largura"],
            veic["altura"]
        ])
        
        if any(
            c > v
            for c, v in zip(dim_carga, dim_veiculo)
        ):
            continue

        nome = veic["Veículo"]
        
        # capacidade base
        if empilhavel:
            capacidade_base = volume_veiculo(veic)
        else:
            capacidade_base = veic["largura"] * veic["comprimento"]
        
        nome = veic["Veículo"]
        fator = get_fator(nome)

        eficiencia = get_eficiencia(nome)
        capacidade_max = capacidade_base * fator * eficiencia

        peso_max = veic["peso_max"]
    
        # remove apenas absurdamente inviáveis
        if peso_total > peso_max * 3:
            continue
        
        if valor_total > capacidade_max * 3:
            continue
    
        aproveitamento_vol = min(100, (valor_total / capacidade_max) * 100)
        aproveitamento_peso = min(100, (peso_total / peso_max) * 100)
        
        # evita veículos absurdamente vazios
        if aproveitamento_vol < 15:
            continue
        
        # evita aproveitamento impossível
        if aproveitamento_vol > 115:
            continue
        score = calcular_score(
            valor_total,
            capacidade_max,
            peso_total,
            peso_max
        )
        
        # 🚫 remove lixo do ranking
        if score == 0:
            continue
            
        ranking.append({
            "Veículo": veic["Veículo"],
            "Status": "Viável",
            "Motivo": (
                f"Volume: {aproveitamento_vol:.1f}% | "
                f"Peso: {aproveitamento_peso:.1f}%"
            ),
            "Cenário": "RANKING",
            "Aproveitamento (%)": round(aproveitamento_vol, 2),
            "Aproveitamento Peso (%)": round(aproveitamento_peso, 2),
            "Score": round(score, 2)
        })
    
    df_rank = pd.DataFrame(ranking)
    
    if not df_rank.empty:
    
        df_rank = df_rank.sort_values(
            by="Score",
            ascending=False
        ).reset_index(drop=True)
    
        melhor_rank = df_rank.iloc[[0]]
    
    else:
        melhor_rank = pd.DataFrame()


    # ==========================================
    # FALLBACK ABSOLUTO
    # ==========================================
    
    if df_rank.empty:
    
        fallback = []
    
        for _, veic in df_testar.iterrows():
    
            nome = veic["Veículo"]
    
            volume_base = (
                  volume_veiculo(veic)
            )
    
            fator = get_fator(nome)
            eficiencia = get_eficiencia(nome)
    
            capacidade = volume_base * fator * eficiencia
    
            aproveitamento = (
                valor_total / capacidade * 100
                if capacidade > 0 else 0
            )
    
            aproveitamento_peso = (
                peso_total / veic["peso_max"] * 100
                if veic["peso_max"] > 0 else 0
            )
    
            fallback.append({
                "Veículo": nome,
                "Status": "Operação Especial",
                "Motivo": "Necessita operação especial",
                "Cenário": "FALLBACK",
                "Aproveitamento (%)": round(aproveitamento, 2),
                "Aproveitamento Peso (%)": round(aproveitamento_peso, 2),
                "Score": 1
            })
    
        df_rank = pd.DataFrame(fallback)
        
        return df_rank, {"cenario": "RANKING"}
    
    # ==========================
    # ✅ MULTI + COMBO UNIFICADO
    # ==========================
    df_multi_real = dividir_carga_multi(
        cargas,
        df_testar,
        empilhavel
    )
    
    df_combo = gerar_combinacoes(
        df_testar,
        valor_total,
        peso_total,
        empilhavel
    )
    
    df_multi_unificado = pd.concat(
        [df_multi_real, df_combo],
        ignore_index=True
    )
    
    # ✅ MULTI PRINCIPAL
    if not df_multi_unificado.empty:
    
        df_multi_unificado = df_multi_unificado.sort_values(
            by="Score",
            ascending=False
        ).reset_index(drop=True)
    
        melhor = df_multi_unificado.iloc[[0]]
    
        # ==========================================
        # PRIORIZA VEÍCULO ÚNICO SE SCORE FOR PRÓXIMO
        # ==========================================
    
        if not melhor_rank.empty:
    
            score_rank = melhor_rank.iloc[0]["Score"]
            score_multi = melhor.iloc[0]["Score"]
    
            if score_rank >= score_multi * 0.90:
                return melhor_rank, {"cenario": "RANKING"}
    
        return melhor, {"cenario": "MULTI"}
    
    # ✅ 3 — FALLBACK (nunca ficar vazio)
    # Se chegamos aqui, significa que não houve veículo "Viável" 100%
    # Vamos retornar todos os veículos testados para que o usuário veja o motivo da inviabilidade
    df_rank = pd.DataFrame(registros)
    
    # Adicionamos colunas de aproveitamento para o usuário ver o quão longe está
    def calc_aprov(row):
        nome = row["Veículo"]
        fator = get_fator(nome)
        eficiencia = get_eficiencia(nome)
    
        cap = row["Volume Máx"] * fator * eficiencia
    
        return (valor_total / cap * 100) if cap > 0 else 0
    
    df_rank["Aproveitamento (%)"] = df_rank.apply(calc_aprov, axis=1)
    
    df_rank["Aproveitamento Peso (%)"] = df_rank["Peso Máx"].apply(
        lambda v: (peso_total / v * 100) if v > 0 else 0
    )
        
    # Calcula um score simplificado para ordenar os "menos piores" primeiro
    df_rank["Score"] = (df_rank["Aproveitamento (%)"] * 0.5) + (df_rank["Aproveitamento Peso (%)"] * 0.5)
    
    df_rank = df_rank.sort_values(by="Score", ascending=False).reset_index(drop=True)
    
    return df_rank, {"cenario": "RANKING"}

def limpar_dataframe(df):
    if df.empty:
        return df

    return df.replace(
        [float("inf"), -float("inf")],
        0
    ).fillna(0)

# ============================
# 🚀 BOTÃO CALCULAR
# ============================

if st.button("🚀 Calcular Dimensionamento", disabled=not st.session_state.cargas):

    with st.spinner("Calculando melhor cenário..."):
        df_result, meta = executar_calculo(
            st.session_state.cargas,
            df_veiculos,
            selecionados,
            empilhavel
        )

        # salva no session_state
        st.session_state.df_result = limpar_dataframe(df_result)
        st.session_state.cenario = meta.get("cenario")

    # feedback básico
    if st.session_state.get("cenario") == "RANKING":
        st.success("✅ Melhor veículo identificado com base em eficiência.")
    elif st.session_state.cenario == "MULTI":
        st.warning("⚠ Planejamento com múltiplos veículos necessário.")
    else:
        st.info("Nenhum cenário definido.")

# ============================
# 📊 EXIBIÇÃO DOS RESULTADOS (AJUSTADO)
# ============================

if isinstance(st.session_state.df_result, pd.DataFrame):

    # ✅ CASO NÃO TENHA RESULTADO
    if st.session_state.df_result.empty:
        st.warning("⚠ Nenhuma combinação ou veículo atendeu aos critérios definidos.")
        st.info("💡 Dica: reduza o filtro ou aumente a quantidade da carga.")
        st.stop()

    st.divider()

    # ----------------------------
    # 🚚 CENÁRIO: VEÍCULO / RANKING
    # ----------------------------
    if st.session_state.cenario in ["UNICO", "RANKING"]:

        st.subheader("🏆 Ranking de Veículos Viáveis")

        df_rank = st.session_state.df_result.copy()
        df_rank["Ranking"] = df_rank.index + 1

        melhor = df_rank.iloc[0]["Veículo"]

        def destacar(row):
            styles = [""] * len(row)

            if row["Veículo"] == melhor:
                styles = ["background-color:#145A32;color:white;font-weight:bold"] * len(row)
            elif row["Motivo"] != "":
                styles = ["background-color:#FFF3CD;color:#856404"] * len(row)

            return styles

        st.dataframe(
            df_rank.style.apply(destacar, axis=1),
            use_container_width=True
        )

    # ----------------------------
    # 🚛 MULTI VEÍCULO
    # ----------------------------
    else:

        st.subheader("📦 Planejamento Multi-Veículo")

        st.dataframe(
            st.session_state.df_result,
            use_container_width=True
        )

        st.warning("⚠ A carga exige mais de um veículo.")

# ============================
# 🔍 SIMULAÇÃO DE EMPILHAMENTO 3D (AJUSTADA)
# ============================

if st.button("🔍 Simular Empilhamento 3D"):

    if st.session_state.df_result.empty:
        st.error("Execute o cálculo antes da simulação.")
        st.stop()

    if not empilhavel:
        st.warning("Simulação 3D disponível apenas com empilhamento ativado.")
        st.stop()
        
    # Veículo vencedor
    melhor_veiculo = st.session_state.df_result.iloc[0]["Veículo"]
    
    # ✅ TRATAMENTO DE COMBO
    if " + " in melhor_veiculo:
    
        partes = melhor_veiculo.split(" + ")
    
        df_parte = df_veiculos[df_veiculos["Veículo"].isin(partes)]
    
        if df_parte.empty:
            st.error("Erro ao carregar veículos do combo.")
            st.stop()
    
        # 🔥 cria veículo combinado
        veic = {
            "largura": df_parte["largura"].max(),
            "comprimento": df_parte["comprimento"].sum(),
            "altura": df_parte["altura"].max(),
            "peso_max": df_parte["peso_max"].sum()
        }

    # ✅ VEÍCULO NORMAL
    else:
        veic = df_veiculos[
            df_veiculos["Veículo"] == melhor_veiculo
        ].iloc[0]

    # Quantidade real de caixas
    qtd_total_real = sum(c["Quantidade"] for c in st.session_state.cargas)

    # Redução de caixas (performance)
    cargas_unitarias = reduzir_cargas_para_simulacao(
        st.session_state.cargas,
        MAX_CAIXAS_3D
    )

    # Corte antecipado por volume impossível
    fator = get_fator(melhor_veiculo)
    
    volume_total_veiculo = volume_veiculo(veic)
    
    valor_total_real = sum(
        c["Volume total (m³)"] for c in st.session_state.cargas
    )
    
    # =========================================
    # AJUSTE DE FATOR / EFICIÊNCIA PARA COMBO
    # =========================================

    def get_fator_combo(nome):
        partes = nome.split(" + ")
        fatores = [get_fator(p) for p in partes]
        return min(fatores)

    def get_eficiencia_combo(nome):
        partes = nome.split(" + ")
        eficiencias = [get_eficiencia(p) for p in partes]
        return min(eficiencias)

    if " + " in melhor_veiculo:
        fator = get_fator_combo(melhor_veiculo)
        eficiencia = get_eficiencia_combo(melhor_veiculo)
    else:
        fator = get_fator(melhor_veiculo)
        eficiencia = get_eficiencia(melhor_veiculo)

    volume_ajustado = (
        volume_total_veiculo
        * eficiencia
        * fator
    )

    # =========================================
    # VALIDAÇÃO DE CAPACIDADE
    # =========================================

    if valor_total_real > volume_ajustado:

        st.error(
            "❌ O volume das caixas excede a capacidade física do veículo."
        )

        st.stop()

    # =========================================
    # SIMULAÇÃO 3D
    # =========================================

    posicoes, caixas, volume_usado, peso_usado = simular_empilhamento_3d(
        cargas_unitarias,
        veic,
        qtd_total_real
    )

    ocupacao = (
        min(100, (volume_usado / volume_total_veiculo) * 100)
        if volume_total_veiculo > 0 else 0
    )

    st.subheader("📦 Resultado da Simulação 3D")
    st.write(f"Veículo: **{melhor_veiculo}**")
    st.write(f"Caixas alocadas: **{caixas}**")
    st.write(f"Ocupação: **{ocupacao:.2f}%**")
    st.write(f"Peso carregado: **{peso_usado:.2f} kg**")

    if caixas < qtd_total_real:
        st.error("⚠ Nem todas as caixas couberam.")
    else:
        st.success("✅ Todas as caixas foram alocadas.")

    # ============================
    # VISUALIZAÇÃO 3D (PLOTLY)
    # ============================
    fig = go.Figure()
    cores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    
    MAX_BOXES_RENDER = min(MAX_RENDER_3D, len(posicoes))
    
    for i, (x, y, z, c, l, a) in enumerate(
        posicoes[:MAX_BOXES_RENDER]
    ):
    
        fig.add_trace(go.Mesh3d(
            x=[
                x, x+c, x+c, x,
                x, x+c, x+c, x
            ],
    
            y=[
                y, y, y+l, y+l,
                y, y, y+l, y+l
            ],
    
            z=[
                z, z, z, z,
                z+a, z+a, z+a, z+a
            ],
    
            alphahull=0,
    
            opacity=0.45,
    
            color=cores[i % len(cores)],
    
            flatshading=True,
    
            showscale=False
        ))

    # Caixa do veículo
    fig.add_trace(go.Scatter3d(
        x=[0, veic["comprimento"], veic["comprimento"], 0,
           0, veic["comprimento"], veic["comprimento"], 0],
    
        y=[0, 0, veic["largura"], veic["largura"],
           0, 0, veic["largura"], veic["largura"]],
    
        z=[0, 0, 0, 0,
           veic["altura"], veic["altura"], veic["altura"], veic["altura"]],
    
        mode="markers",
    
        marker=dict(
            size=2,
            color="gray",
            opacity=0.05
        ),
    
        showlegend=False
    ))

    fig.update_layout(
        title=f"Ocupação: {ocupacao:.1f}%",
        scene=dict(
            aspectmode="manual",
            aspectratio=dict(
                x=veic["comprimento"],
                y=veic["largura"],
                z=veic["altura"]
            )
        ),
        height=700
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True
        }
    )

# ============================
# 📥 DOWNLOAD EXCEL
# ============================

if (
    isinstance(st.session_state.df_result, pd.DataFrame)
    and not st.session_state.df_result.empty
):

    excel = gerar_excel_bytes(
        st.session_state.df_result,
        st.session_state.cargas
    )

    st.download_button(
        "📥 Baixar Excel",
        data=excel,
        file_name="dimensionamento_veiculos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
