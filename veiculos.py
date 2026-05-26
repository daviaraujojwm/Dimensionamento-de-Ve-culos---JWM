import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
import itertools
import math


# 🔥 PRIMEIRA COISA
st.set_page_config(
    page_title="Cubagem de Veículos - JWM",
    layout="wide"
)

MAX_CAIXAS = 300
MAX_CAIXAS_3D = 200
MAX_ITERACOES = 5000
MAX_GRID = 10000

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

# ============================
# SESSION STATE
# ============================
if "cargas" not in st.session_state:
    st.session_state.cargas = []

# ============================
# RESET DE INPUTS
# ============================
if st.session_state.get("clear_inputs"):
    st.session_state.update({
        "comp": "",
        "larg": "",
        "alt": "",
        "peso": "",
        "qtd": 1
    })
    st.session_state.clear_inputs = False

# ============================
# TÍTULO
# ============================
col1, col2 = st.columns([6, 1])
with col1:
    st.title("Dimensionamento de Veículos - JWM")
with col2:
    try:
        st.image("JWM.png", width=80)
    except:
        pass

# ============================
# INPUTS CARGA
# ============================

st.subheader("📦 Adicionar carga")

col1, col2, col3, col4, col5 = st.columns(
    [1.2, 1.2, 1.2, 1.2, 0.8],
    gap="large"
)

with col1:
    comp_txt = st.text_input("Comprimento (m)", placeholder="ex: 1,20 ou 1.20")

with col2:
    larg_txt = st.text_input("Largura (m)", placeholder="ex: 0,80 ou 0.80")

with col3:
    alt_txt = st.text_input("Altura (m)", placeholder="ex: 1,00")

with col4:
    peso_txt = st.text_input("Peso unitário (kg)", placeholder="ex: 15,5")

with col5:
    qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)



def parse_float(valor):
    try:
        if valor is None:
            return None
        valor = str(valor).strip().replace(",", ".")
        if valor == "":
            return None
        return float(valor)
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
        except:
            return True

    if invalido(comp):
        erros.append("Comprimento inválido")
    if invalido(larg):
        erros.append("Largura inválida")
    if invalido(alt):
        erros.append("Altura inválida")
    if invalido(peso):
        erros.append("Peso inválido")

    if qtd is not None:
        try:
            if int(qtd) <= 0:
                erros.append("Quantidade inválida")
        except:
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

    st.success("Carga adicionada com sucesso!")
    st.session_state.clear_inputs = True
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
        except:
            continue

        if qtd <= 0 or min(comp, larg, alt, peso) <= 0:
            continue

        for _ in range(qtd):
            if len(lista) >= limite:
                return lista

            lista.append({
                "comp": comp,
                "larg": larg,
                "alt": alt,
                "peso": peso,
                "volume": comp * larg * alt
            })

    return lista

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

def calcular_score(volume_usado, volume_max, peso_usado, peso_max):

    if volume_max <= 0 or peso_max <= 0:
        return 0

    aproveitamento_volume = (volume_usado / volume_max) * 100
    aproveitamento_peso = (peso_usado / peso_max) * 100

    aproveitamento_volume = min(100, aproveitamento_volume)
    aproveitamento_peso = min(100, aproveitamento_peso)

    balanceamento = 100 - abs(aproveitamento_volume - aproveitamento_peso)

    score = (
        (aproveitamento_volume * 0.45) +
        (aproveitamento_peso * 0.40) +
        (balanceamento * 0.15)
    )

    # penaliza volume baixo
    if aproveitamento_volume < 30:
        score -= (30 - aproveitamento_volume) * 0.8

    # 🔥 penaliza peso alto
    if aproveitamento_peso > 80:
        score -= 20

    return max(0, round(score, 2))

def escolher_veiculo_unico_completo(cargas_unit, df_veiculos):

    if empilhavel:
        valor_total = sum(c["volume"] for c in cargas_unit)
    else:
        valor_total = sum(c["comp"] * c["larg"] for c in cargas_unit)

    peso_total = sum(c["peso"] for c in cargas_unit)

    melhor_score = -1
    melhor_veiculo = None

    df_ordenado = df_veiculos.sort_values(
        by="Capacidade Volume (m³)"
    )

    max_comp = max(c["comp"] for c in cargas_unit)
    max_larg = max(c["larg"] for c in cargas_unit)
    max_alt  = max(c["alt"] for c in cargas_unit)

    for _, veic in df_ordenado.iterrows():

        # ✅ BLOQUEIO FÍSICO
        if (
            max_comp > veic["comprimento"]
            or max_larg > veic["largura"]
            or max_alt > veic["altura"]
        ):
            continue

        capacidade = (
            veic["largura"]
            * veic["comprimento"]
            * veic["altura"]
        ) * get_fator(veic["Veículo"])

        peso_max = veic["peso_max"]

        if valor_total > capacidade or peso_total > peso_max:
            continue

        score = calcular_score(
            valor_total,
            capacidade,
            peso_total,
            peso_max
        )

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
    todas = expand_cargas_unitarias(cargas, limite=10**9)

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

            # Cria nova camada (empilhamento)
            if altura_usada + it["alt"] <= alt_v * 0.98:
                camadas.append({"len": comp_i})
                altura_usada += it["alt"]
                colocado = True
                break

        # Não foi possível colocar a caixa
        if not colocado:
            return False

    return True

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
    caixas_alocadas = 0
    peso_acumulado = 0

    contador = 0
    estourou_limite = False

    cargas_unitarias = sorted(
        cargas_unitarias,
        key=lambda x: x["comp"] * x["larg"] * x["alt"],
        reverse=True
    )

    for item in cargas_unitarias:

        if estourou_limite:
            break

        if item["peso"] <= 0:
            continue

        
        orientacoes = list(itertools.permutations(
            (item["comp"], item["larg"], item["alt"])
        ))


        for comp_o, larg_o, alt_o in orientacoes:

            try:
                x_max = int(comp_veic // comp_o)
                y_max = int(larg_veic // larg_o)
                z_max = int(alt_veic // alt_o)
            except:
                continue

            grid_size = x_max * y_max * z_max
            if grid_size <= 0:
                continue

            if grid_size > max_grid:
                fator = (grid_size / max_grid) ** (1/3)
                x_max = max(1, int(x_max / fator))
                y_max = max(1, int(y_max / fator))
                z_max = max(1, int(z_max / fator))

            step = 1

            # ================================
            # ✅ LOOP EM CAMADAS (Z FORÇADO)
            # ================================
            
            alturas_camadas = [i * alt_o for i in range(z_max)]
            
            for z in alturas_camadas:
                for x in range(0, x_max, step):
                    for y in range(0, y_max, step):

                        contador += 1
                        if contador > limite_iter:
                            estourou_limite = True
                            break

                        nova = (
                            x * comp_o,
                            y * larg_o,
                            z, 
                            comp_o,
                            larg_o,
                            alt_o
                        )

                        if colide(nova, posicoes_ocupadas):
                            continue
                        if not tem_base(nova, posicoes_ocupadas):
                            continue
                        if peso_acumulado + item["peso"] > peso_max:
                            continue

                        posicoes_ocupadas.append(nova)
                        caixas_alocadas += 1
                        peso_acumulado += item["peso"]

                        if caixas_alocadas >= qtd_total_real:
                            estourou_limite = True
                            break
                    if estourou_limite:
                        break
                if estourou_limite:
                    break

    volume_usado = sum(c * l * a for (_, _, _, c, l, a) in posicoes_ocupadas)

    return posicoes_ocupadas, caixas_alocadas, volume_usado, peso_acumulado

def gerar_cenarios_multi(cargas, df_veiculos, empilhavel=True, max_opcoes=5):

    cargas_unit = expand_cargas_unitarias(cargas)

    if empilhavel:
        volume_total = sum(c["volume"] for c in cargas_unit)
    else:
        volume_total = sum(c["comp"] * c["larg"] for c in cargas_unit)

    peso_total = sum(c["peso"] for c in cargas_unit)

    cenarios = []

    veiculos_ordenados = df_veiculos.sort_values(
        by="Capacidade Volume (m³)"
    )

    for _, veic in veiculos_ordenados.iterrows():
    
        nome = veic["Veículo"]
    
        # ✅ classificação mais inteligente por tipo
        if "Carreta" in nome:
            eficiencia = 0.85
    
        elif "Bi-Truck" in nome or "Bitruck" in nome:
            eficiencia = 0.82
    
        elif "Truck" in nome:
            eficiencia = 0.78
    
        elif "3/4" in nome or "Toco" in nome:
            eficiencia = 0.77
    
        elif "HR" in nome or "VUC" in nome:
            eficiencia = 0.75
    
        else:
            eficiencia = 0.72

        # capacidade
        if empilhavel:
            cap_vol = (
                veic["largura"]
                * veic["comprimento"]
                * veic["altura"]
            )
        else:
            cap_vol = (
                veic["largura"]
                * veic["comprimento"]
            )
    
        # ✅ aplica eficiência nos DOIS
        cap_vol *= eficiencia
        cap_peso = veic["peso_max"] * eficiencia

        qtd_por_volume = math.ceil(volume_total / cap_vol)
        qtd_por_peso = math.ceil(peso_total / cap_peso)

        qtd = max(qtd_por_volume, qtd_por_peso)
        
        if qtd <= 0 or qtd > 10:
        
            continue
        # ✅ 🔥 impede MULTI com 1 veículo
        if qtd == 1:
            continue

        aproveitamento_vol = volume_total / (cap_vol * qtd)
        aproveitamento_peso = peso_total / (cap_peso * qtd)

        aproveitamento_vol = min(1, aproveitamento_vol)
        aproveitamento_peso = min(1, aproveitamento_peso)

        if aproveitamento_vol < 0.05:
            continue

        if volume_total < cap_vol * 0.2:
            continue

        balanceamento = 1 - abs(aproveitamento_vol - aproveitamento_peso)

        score = (
            (aproveitamento_vol * 50) +
            (aproveitamento_peso * 30) +
            (balanceamento * 20) -
            (qtd * 1.2)
        )

        cenarios.append({
            "Veículo": veic["Veículo"],
            "Configuração": f"{qtd}x {veic['Veículo']}",
            "Aproveitamento (%)": round(aproveitamento_vol * 100, 1),
            "Aproveitamento Peso (%)": round(aproveitamento_peso * 100, 1),
            "Score": round(score, 2)
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

    df_multi["Status"] = "Viável"
    df_multi["Motivo"] = df_multi.apply(
        lambda row: (
            f"A carga exige múltiplos veículos.\n"
            f"Solução ideal: {row['Configuração']} para atender 100% do volume e peso."
        ),
        axis=1
    )
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
            if chave in usados:
                continue
            usados.add(chave)

            f1 = get_fator(v1["Veículo"])
            f2 = get_fator(v2["Veículo"])
            
            if empilhavel:
                cap1 = (
                    v1["largura"] * v1["comprimento"] * v1["altura"]
                ) * f1
            
                cap2 = (
                    v2["largura"] * v2["comprimento"] * v2["altura"]
                ) * f2
            else:
                cap1 = (v1["largura"] * v1["comprimento"]) * f1
                cap2 = (v2["largura"] * v2["comprimento"]) * f2


            cap_total = cap1 + cap2
            cap_peso = (v1["peso_max"] * f1) + (v2["peso_max"] * f2)
            peso_cap = cap_peso

            if valor_total > cap_total:
                continue

            if peso_total > peso_cap * 1.3:
                continue

            aproveitamento_vol = valor_total / cap_total * 100
            aproveitamento_peso = peso_total / peso_cap * 100

            if aproveitamento_vol < 30:
                continue

            score = (
                (aproveitamento_vol * 0.55)
                + (aproveitamento_peso * 0.30)
                + ((100 - abs(aproveitamento_vol - aproveitamento_peso)) * 0.15)
            )

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

def executar_calculo(cargas, df_veiculos, selecionados):
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
    valor_total, peso_total = calcular_totais(cargas, empilhavel)
    
    # --------------------------------
    # Viabilidade básica (peso + volume)
    # --------------------------------
    registros = []

    # 🔒 Dimensões máximas unitárias da carga
    max_comp = max(c["Comprimento (m)"] for c in cargas)
    max_larg = max(c["Largura (m)"] for c in cargas)
    max_alt  = max(c["Altura (m)"] for c in cargas)

    for _, veic in df_testar.iterrows():
        volume_max = veic["largura"] * veic["comprimento"] * veic["altura"]
        peso_max = veic["peso_max"]
    
        status = "Viável"
        motivo = ""
    
        # 🚫 REGRAS FÍSICAS (Agora apenas marcam como 'Limitado' em vez de remover totalmente do cálculo inicial)
        if max_larg > veic["largura"]:
            status = "Inviável"
            motivo = "Largura excede"
        
        elif max_comp > veic["comprimento"]:
            status = "Inviável"
            motivo = "Comprimento excede"
        
        elif max_alt > veic["altura"]:
            status = "Inviável"
            motivo = "Altura excede"
    
        # 🚫 REGRAS OPERACIONAIS (PESO / CAPACIDADE)
        
        nome = veic["Veículo"]
        
        # capacidade base
        if empilhavel:
            capacidade_base = veic["largura"] * veic["comprimento"] * veic["altura"]
        else:
            capacidade_base = veic["largura"] * veic["comprimento"]
        
        fator = get_fator(nome)
        capacidade_max = capacidade_base * fator

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
        
            df_multi = df_multi.sort_values(by="Score", ascending=False).reset_index(drop=True)
        
            # 🔥 seleciona apenas a melhor opção
            melhor = df_multi.iloc[[0]]
        
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
    
    cargas_unit = expand_cargas_unitarias(cargas)
    
    veic_unico = escolher_veiculo_unico_completo(
        cargas_unit,
        df_testar
    )
        
    # ==================================================
    # PRIORIZA O MENOR VEÍCULO COMPATÍVEL (COM FILTRO)
    # ==================================================

    if veic_unico is not None:
    
        # =========================
        # CAPACIDADE DO VEÍCULO
        # =========================
        if empilhavel:
            capacidade = (
                veic_unico["largura"]
                * veic_unico["comprimento"]
                * veic_unico["altura"]
            )
        else:
            capacidade = (
                veic_unico["largura"]
                * veic_unico["comprimento"]
            )
    
        # =========================
        # APROVEITAMENTO
        # =========================
        aproveitamento_vol = min(100, (valor_total / capacidade) * 100)
        aproveitamento_peso = min(100, (peso_total / veic_unico["peso_max"]) * 100)
    
        # =========================
        # SCORE
        # =========================
        score = calcular_score(
            valor_total,
            capacidade,
            peso_total,
            veic_unico["peso_max"]
        )
    
        # =========================
        # RETORNO FINAL
        # =========================
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
        if (
            max_comp > veic["comprimento"]
            or max_larg > veic["largura"]
            or max_alt > veic["altura"]
        ):
            continue

        nome = veic["Veículo"]
        
        # capacidade base
        if empilhavel:
            capacidade_base = veic["largura"] * veic["comprimento"] * veic["altura"]
        else:
            capacidade_base = veic["largura"] * veic["comprimento"]
        
        nome = veic["Veículo"]
        fator = get_fator(nome)

        capacidade_max = capacidade_base * fator
    
        peso_max = veic["peso_max"]
    
        # remove inviáveis
        if peso_total > peso_max or valor_total > capacidade_max:
            continue
    
        aproveitamento_vol = min(100, (valor_total / capacidade_max) * 100)
        aproveitamento_peso = min(100, (peso_total / peso_max) * 100)

        score = calcular_score(
            valor_total,
            capacidade_max,
            peso_total,
            peso_max
        )
    
        ranking.append({
            "Veículo": veic["Veículo"],
            "Status": "Viável",
            "Motivo": "",
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
    
    if not df_multi_unificado.empty:
    
        df_multi_unificado = df_multi_unificado.sort_values(
            by="Score",
            ascending=False
        ).reset_index(drop=True)
    
        # 🔥 pega automaticamente o melhor cenário
        melhor = df_multi_unificado.iloc[[0]]
    
        return melhor, {"cenario": "MULTI"}
    

    # ✅ 3 — FALLBACK (nunca ficar vazio)
    # Se chegamos aqui, significa que não houve veículo "Viável" 100%
    # Vamos retornar todos os veículos testados para que o usuário veja o motivo da inviabilidade
    df_rank = pd.DataFrame(registros)
    
    # Adicionamos colunas de aproveitamento para o usuário ver o quão longe está
    df_rank["Aproveitamento (%)"] = (valor_total / (df_rank["Volume Máx"])) * 100
    df_rank["Aproveitamento Peso (%)"] = (peso_total / df_rank["Peso Máx"]) * 100
    
    # Calcula um score simplificado para ordenar os "menos piores" primeiro
    df_rank["Score"] = (df_rank["Aproveitamento (%)"] * 0.5) + (df_rank["Aproveitamento Peso (%)"] * 0.5)
    
    df_rank = df_rank.sort_values(by="Score", ascending=False).reset_index(drop=True)
    
    return df_rank, {"cenario": "RANKING"}

# ============================
# 🚀 BOTÃO CALCULAR
# ============================

if st.button("🚀 Calcular Dimensionamento", disabled=not st.session_state.cargas):

    with st.spinner("Calculando melhor cenário..."):
        df_result, meta = executar_calculo(
            st.session_state.cargas,
            df_veiculos,
            selecionados
        )

        # salva no session_state
        st.session_state.df_result = df_result
        st.session_state.cenario = meta.get("cenario")

    # feedback básico
    if st.session_state.cenario == "RANKING":
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
    
    volume_veiculo = (
        veic["largura"] * veic["comprimento"] * veic["altura"]
    ) * fator
    
    valor_total_caixas = sum(c["volume"] for c in cargas_unitarias)
    
    if valor_total_caixas > volume_veiculo * 1.05:
        st.error("❌ O volume das caixas excede a capacidade física do veículo.")
        st.stop()
    
    # Simulação 3D
    posicoes, caixas, volume_usado, peso_usado = simular_empilhamento_3d(
        cargas_unitarias,
        veic,
        qtd_total_real
    )
    
    # Agora sim calcula ocupação
    ocupacao = min(100, (volume_usado / volume_veiculo) * 100)


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

    for i, (x, y, z, c, l, a) in enumerate(posicoes[:150]):
        fig.add_trace(go.Mesh3d(
            x=[x, x+c, x+c, x, x, x+c, x+c, x],
            y=[y, y, y+l, y+l, y, y, y+l, y+l],
            z=[z, z, z, z, z+a, z+a, z+a, z+a],
            color=cores[i % len(cores)],
            opacity=0.9,
            showscale=False
        ))

    # Caixa do veículo
    fig.add_trace(go.Mesh3d(
        x=[0, veic["comprimento"], veic["comprimento"], 0,
           0, veic["comprimento"], veic["comprimento"], 0],
        y=[0, 0, veic["largura"], veic["largura"],
           0, 0, veic["largura"], veic["largura"]],
        z=[0, 0, 0, 0,
           veic["altura"], veic["altura"], veic["altura"], veic["altura"]],
        color="gray",
        opacity=0.05,
        showscale=False
    ))

    fig.update_layout(
        title=f"Ocupação: {ocupacao:.1f}%",
        scene=dict(aspectmode="data"),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

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
