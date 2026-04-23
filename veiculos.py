import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go

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
    background-attachment: fixed;
}

/* overlay mais forte (melhora blur) */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    z-index: 0;
}

/* ============================
   CONTAINER PRINCIPAL (CARD)
============================ */
.block-container {
    position: relative;
    z-index: 1;

    max-width: 1200px;
    margin: auto;

    padding: 40px 35px;

    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);

    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.2);

    box-shadow: 0 8px 40px rgba(0,0,0,0.35);
}

/* ============================
   TEXTOS
============================ */
label {
    color: white !important;
    text-shadow: 0 1px 3px black;
}

/* ============================
   INPUTS
============================ */
.stTextInput input, 
.stNumberInput input {
    background: rgba(255,255,255,0.95);
    color: black;
    border-radius: 10px;
    padding: 10px;
    border: none;
}

/* ============================
   ESPAÇAMENTO ENTRE ELEMENTOS
============================ */
.stTextInput, 
.stNumberInput, 
.stSelectbox {
    margin-bottom: 18px;
}

h2, h3 {
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

# conversão
comp = parse_float(comp_txt)
larg = parse_float(larg_txt)
alt = parse_float(alt_txt)
peso = parse_float(peso_txt)


erros = validar_inputs(comp, larg, alt, peso, qtd)

if erros and (comp_txt or larg_txt or alt_txt or peso_txt):
    st.error(" | ".join(erros))

# aviso de performance
if qtd > 1000:
    st.warning("⚠ Quantidade muito alta pode impactar a performance.")

pode_adicionar = len(erros) == 0

#ADICIONAR CARGA

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

def calcular_totais(cargas):
    """
    Calcula volume e peso total de forma consistente.
    """
    volume = 0
    peso = 0

    for c in cargas:
        qtd = float(c.get("Quantidade", 0))

        comp = float(c["Comprimento (m)"])
        larg = float(c["Largura (m)"])
        alt = float(c["Altura (m)"])
        peso_unit = float(c["Peso unitário (kg)"])

        volume += comp * larg * alt * qtd
        peso += peso_unit * qtd

    return volume, peso

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
    """
    Cálculo único e padronizado de score.
    Deve ser usado em TODO o app.
    Retorna score entre 0 e 100.
    """
    if volume_max <= 0 or peso_max <= 0:
        return 0

    aproveitamento_volume = min(100, (volume_usado / volume_max) * 100)
    aproveitamento_peso = min(100, (peso_usado / peso_max) * 100)

    balanceamento = 100 - abs(aproveitamento_volume - aproveitamento_peso)
    penalidade_excesso = max(0, aproveitamento_peso - 100) ** 1.5

    score = (
        (aproveitamento_volume * 0.45) +
        (aproveitamento_peso * 0.35) +
        (balanceamento * 0.20)
        - penalidade_excesso
    )

    return round(max(0, min(100, score)), 2)

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
    volume_total,
    peso_total,
    volume_max,
    peso_max,
    score,
    caixas_alocadas,
    qtd_total_real
):
    aproveitamento_volume = (volume_total / volume_max) * 100
    aproveitamento_peso = (peso_total / peso_max) * 100
    equilibrio = 100 - abs(aproveitamento_volume - aproveitamento_peso)

    texto = (
        f"O veículo **{veiculo}** foi selecionado por apresentar o melhor "
        f"equilíbrio técnico entre volume e peso.\n\n"
        f"• Ocupação volumétrica: {aproveitamento_volume:.1f}%\n"
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
            if altura_usada + it["alt"] <= alt_v:
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

        orientacoes = [
            (item["comp"], item["larg"], item["alt"]),
            (item["larg"], item["comp"], item["alt"])
        ]

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

            step = max(1, min(x_max, y_max, z_max) // 10)

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

# ==========================================
# ✅ FUNÇÃO PARA COMPLEMENTO RESIDUAL
# ==========================================
def escolher_veiculo_menor_viavel(cargas_restantes, df_veiculos):
    volume_restante = sum(c["volume"] for c in cargas_restantes)
    peso_restante = sum(c["peso"] for c in cargas_restantes)

    # ✅ maior altura entre as caixas restantes
    altura_minima = max(c["alt"] for c in cargas_restantes)

    veiculos_ordenados = df_veiculos.sort_values(
        by="Capacidade Volume (m³)",
        ascending=True
    )

    for _, veic in veiculos_ordenados.iterrows():
        volume_max = veic["comprimento"] * veic["largura"] * veic["altura"]
        peso_max = veic["peso_max"]

        # ✅ valida peso + volume + ALTURA
        if (
            volume_restante <= volume_max
            and peso_restante <= peso_max
            and altura_minima <= veic["altura"]
        ):
            return veic

    return None


def calcular_multi_veiculos(cargas, df_veiculos):

    cargas_unit = expand_cargas_unitarias(cargas, limite=MAX_CAIXAS)

    # ordenar cargas maiores primeiro
    cargas_unit = sorted(
        cargas_unit,
        key=lambda x: x["comp"] * x["larg"] * x["alt"],
        reverse=True
    )

    # ordenar veículos (maior para menor)
    veiculos_ordenados = df_veiculos.sort_values(
        by="Capacidade Volume (m³)",
        ascending=False
    )

    resultado = []
    cargas_restantes = cargas_unit.copy()

    # alerta de cargas impossíveis
    if any(c["peso"] > df_veiculos["peso_max"].max() for c in cargas_restantes):
        st.warning("⚠ Existem cargas com peso maior que qualquer veículo disponível.")

    LIMIAR_MINIMO_CAIXAS = 2
    TOTAL_CAIXAS = len(cargas_unit)

    tentativas = 0
    MAX_TENTATIVAS = 50
    
    while cargas_restantes:
        tentativas += 1
        if tentativas > MAX_TENTATIVAS:
            break

        # ==================================================
        # ✅ CONSOLIDAÇÃO ECONÔMICA DO RESÍDUO
        # ==================================================
        if len(cargas_restantes) <= LIMIAR_MINIMO_CAIXAS:

            # tenta consolidar no último veículo usado
            if resultado:
                ultimo_veic = resultado[-1]["Veículo"]
                veic_info = df_veiculos[
                    df_veiculos["Veículo"] == ultimo_veic
                ].iloc[0]

                if all(
                    c["peso"] <= veic_info["peso_max"]
                    for c in cargas_restantes
                ):
                    resultado[-1]["Qtd Caixas"] += len(cargas_restantes)
                    resultado[-1]["Peso Total (kg)"] = round(
                        resultado[-1]["Peso Total (kg)"] +
                        sum(c["peso"] for c in cargas_restantes),
                        2
                    )
                    cargas_restantes = []
                    break

            # se não conseguiu consolidar, cria novo veículo
            veic_menor = escolher_veiculo_menor_viavel(
                cargas_restantes,
                df_veiculos
            )

            if veic_menor is not None:
                resultado.append({
                    "Veículo": veic_menor["Veículo"],
                    "Qtd Caixas": len(cargas_restantes),
                    "Peso Total (kg)": round(
                        sum(c["peso"] for c in cargas_restantes), 2
                    )
                })
                cargas_restantes = []
                break

        # ==================================================
        # 🚛 LOOP NORMAL DE ALOCAÇÃO
        # ==================================================
        alocou_algum = False

        for _, veic in veiculos_ordenados.iterrows():

            if not cargas_restantes:
                break

            comp_v = veic["comprimento"]
            larg_v = veic["largura"]
            alt_v = veic["altura"]
            peso_max = veic["peso_max"]

            alocadas = []
            peso_total = 0
            volume_ocupado = 0
            novas_restantes = []

            for carga in cargas_restantes:

                volume_carga = carga["volume"]

                if excede_capacidade(
                    peso_total,
                    volume_ocupado,
                    carga["peso"],
                    volume_carga,
                    peso_max,
                    comp_v * larg_v * alt_v
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

    total_alocado = sum(r["Qtd Caixas"] for r in resultado)
    return resultado, total_alocado

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
    volume_total, peso_total = calcular_totais(cargas)

    # --------------------------------
    # Viabilidade básica (peso + volume)
    # --------------------------------
    registros = []

    for _, veic in df_testar.iterrows():
        volume_max = veic["largura"] * veic["comprimento"] * veic["altura"]
        peso_max = veic["peso_max"]

        status = "Viável"
        motivo = ""

        if volume_total > volume_max:
            status = "Inviável"
            motivo = "Excede volume"
        elif peso_total > peso_max:
            status = "Inviável"
            motivo = "Excede peso"

        registros.append({
            "Veículo": veic["Veículo"],
            "Status": status,
            "Motivo": motivo,
            "Volume Máx": volume_max,
            "Peso Máx": peso_max
        })

    df_status = pd.DataFrame(registros)
    df_viaveis = df_status[df_status["Status"] == "Viável"]

    # --------------------------------
    # ❌ Nenhum veículo único → MULTI
    # --------------------------------
    if df_viaveis.empty:
        resultado_multi, _ = calcular_multi_veiculos(cargas, df_testar)
        df_final = pd.DataFrame(resultado_multi)
        return df_final, {"cenario": "MULTI"}

    # --------------------------------
    # Ranqueamento por score
    # --------------------------------
    ranking = []

    for _, row in df_viaveis.iterrows():
        score = calcular_score(
            volume_total,
            row["Volume Máx"],
            peso_total,
            row["Peso Máx"]
        )
   
        aproveitamento_volume = (volume_total / row["Volume Máx"]) * 100
        aproveitamento_peso = (peso_total / row["Peso Máx"]) * 100
        
        penalizado = aproveitamento_volume < 20 and aproveitamento_peso > 60
        
        if penalizado:
            score *= 0.85
        
        ranking.append({
            "Veículo": row["Veículo"],
            "Status": "Viável",
            "Motivo": "⚠ Baixa eficiência volumétrica" if penalizado else "",
            "Aproveitamento Volume (%)": round(aproveitamento_volume, 2),
            "Aproveitamento Peso (%)": round(aproveitamento_peso, 2),
            "Score": round(score, 2)
        })
                
    df_rank = (
        pd.DataFrame(ranking)
        .sort_values(by="Score", ascending=False)
        .reset_index(drop=True)
    )
    

    # --------------------------------
    # ✅ Simulação 3D decide o cenário
    # --------------------------------
    veiculo_principal = df_rank.iloc[0]["Veículo"]
    info_veic = df_veiculos[df_veiculos["Veículo"] == veiculo_principal].iloc[0]

    qtd_total_real = sum(c["Quantidade"] for c in cargas)

    _, caixas_alocadas, _, _ = simular_empilhamento_3d(
        expand_cargas_unitarias(cargas, MAX_CAIXAS_3D),
        info_veic,
        qtd_total_real
    )

    # --------------------------------
    # ✅ CENÁRIO FINAL
    # --------------------------------
    if caixas_alocadas >= qtd_total_real:
        return df_rank, {"cenario": "UNICO"}

    resultado_multi, _ = calcular_multi_veiculos(cargas, df_testar)
    df_final = pd.DataFrame(resultado_multi)

    return df_final, {"cenario": "MULTI"}
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
    if st.session_state.cenario == "UNICO":
        st.success("✅ Um único veículo atende 100% da carga.")
    elif st.session_state.cenario == "MULTI":
        st.warning("⚠ Planejamento com múltiplos veículos necessário.")
    else:
        st.info("Nenhum cenário definido.")

# ============================
# 📊 EXIBIÇÃO DOS RESULTADOS
# ============================

if (
    isinstance(st.session_state.df_result, pd.DataFrame)
    and not st.session_state.df_result.empty
    and st.session_state.cenario is not None
):

    st.divider()

    # ----------------------------
    # 🚚 CENÁRIO: VEÍCULO ÚNICO
    # ----------------------------
    if st.session_state.cenario == "UNICO":
    
        st.subheader("🏆 Ranking de Veículos Viáveis")
    
        df_rank = st.session_state.df_result.copy()
        df_rank["Ranking"] = df_rank.index + 1
    
        melhor = df_rank.iloc[0]["Veículo"]
    
        def destacar(row):
            styles = [""] * len(row)
        
            # ✅ melhor veículo
            if row["Veículo"] == melhor:
                styles = ["background-color:#145A32;color:white;font-weight:bold"] * len(row)
        
            # ⚠️ veículo penalizado
            elif row["Motivo"] != "":
                styles = ["background-color:#FFF3CD;color:#856404"] * len(row)
        
            return styles
    
        st.dataframe(
            df_rank.style.apply(destacar, axis=1),
            use_container_width=True
        )

        # ✅ ganho de eficiência entre 1º e 2º colocados
        if len(df_rank) >= 2:
            score_1 = df_rank.iloc[0]["Score"]
            score_2 = df_rank.iloc[1]["Score"]
        
            if score_2 > 0:
                ganho = ((score_1 - score_2) / score_2) * 100
                st.info(
                    f"📈 O veículo escolhido é **{ganho:.1f}%** mais eficiente "
                    "do que a segunda melhor opção."
                )

    
        volume_total, peso_total = calcular_totais(st.session_state.cargas)
    
        melhor_row = df_rank.iloc[0]
        info_veic = df_veiculos[df_veiculos["Veículo"] == melhor_row["Veículo"]].iloc[0]

        fator_limitante = identificar_fator_limitante(
            volume_total,
            info_veic["largura"] * info_veic["comprimento"] * info_veic["altura"],
            peso_total,
            info_veic["peso_max"]
        )

        st.info(
            gerar_justificativa_veiculo(
                melhor_row["Veículo"],
                volume_total,
                peso_total,
                info_veic["largura"] * info_veic["comprimento"] * info_veic["altura"],
                info_veic["peso_max"],
                melhor_row["Score"],
                caixas_alocadas=len(expand_cargas_unitarias(st.session_state.cargas)),
                qtd_total_real=len(expand_cargas_unitarias(st.session_state.cargas))
            )
        )

        if fator_limitante == "PESO":
            st.warning(
                "⚠ **Carga limitada por PESO.**\n\n"
                "É esperado baixo aproveitamento volumétrico neste cenário."
            )
        elif fator_limitante == "VOLUME":
            st.warning(
                "⚠ **Carga limitada por VOLUME.**\n\n"
                "O peso do veículo ainda possui margem disponível."
            )
        else:
            st.success(
                "✅ **Carga bem equilibrada entre peso e volume.**"
            )

    # ----------------------------
    # 🚛 CENÁRIO: MULTI VEÍCULO
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

    if st.session_state.cenario != "UNICO":
        st.warning("Simulação 3D disponível apenas para cenário de veículo único.")
        st.stop()

    # Veículo vencedor
    melhor_veiculo = st.session_state.df_result.iloc[0]["Veículo"]
    veic = df_veiculos[df_veiculos["Veículo"] == melhor_veiculo].iloc[0]

    # Quantidade real de caixas
    qtd_total_real = sum(c["Quantidade"] for c in st.session_state.cargas)

    # Redução de caixas (performance)
    cargas_unitarias = reduzir_cargas_para_simulacao(
        st.session_state.cargas,
        MAX_CAIXAS_3D
    )

    # Corte antecipado por volume impossível
    volume_total_caixas = sum(c["volume"] for c in cargas_unitarias)
    volume_veiculo = veic["largura"] * veic["comprimento"] * veic["altura"]

    if volume_total_caixas > volume_veiculo * 1.05:
        st.error("❌ O volume das caixas excede a capacidade física do veículo.")
        st.stop()

    # Simulação 3D
    posicoes, caixas, volume_usado, peso_usado = simular_empilhamento_3d(
        cargas_unitarias,
        veic,
        qtd_total_real
    )

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

    for i, (x, y, z, c, l, a) in enumerate(posicoes):
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
