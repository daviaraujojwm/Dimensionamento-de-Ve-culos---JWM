import streamlit as st
import pandas as pd
from io import BytesIO
from itertools import permutations
import plotly.graph_objects as go
import math


# 🔥 PRIMEIRA COISA
st.set_page_config(
    page_title="Cubagem de Veículos - JWM",
    layout="wide"
)

MAX_CENARIOS_SIMULACAO = 5
COLUNAS_RESULTADO = [
    "Veículo", "Status", "Motivo", "Cenário",
    "Aproveitamento (%)", "Aproveitamento Peso (%)", "Score",
]



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
    st.session_state.df_result = pd.DataFrame(columns=COLUNAS_RESULTADO)
else:
    st.session_state.df_result = st.session_state.df_result.reindex(columns=COLUNAS_RESULTADO)

for k, v in {
    "cenario": None,
    "descartados": None,
    "assinatura_calculo": None,
    "mostrar_3d": False,
    "editor_v": 0,
    "cargas": [],
}.items():
    st.session_state.setdefault(k, v)

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
    if "Carreta" in nome or "Wanderleia" in nome:
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
        "Quantidade:", min_value=1, max_value=5000, value=1, step=1, key="qtd"
    )


def parse_float(valor):
    try:
        if valor is None:
            return None
        valor = str(valor).strip().replace(",", ".")
        if valor == "":
            return None
        n = float(valor)
        if math.isnan(n) or math.isinf(n):
            return None
        return round(n, 4)
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
    for nome, v in (("Comprimento", comp), ("Largura", larg), ("Altura", alt)):
        if v is not None and v > 30:
            erros.append(f"{nome} acima de 30 m — confira se não digitou em cm")
    if peso is not None and peso > 100000:
        erros.append("Peso unitário acima de 100.000 kg — confira a unidade")
        
    return erros
#.

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

if total_caixas > 500:
    st.info("ℹ A simulação considera todas as caixas; cargas grandes podem deixar o cálculo e o gráfico 3D mais lentos.")

pode_adicionar = len(erros) == 0

# ========================================
# ✅ TOGGLE DE EMPILHAMENTO (FORA DO BOTÃO)
# ========================================

# ============================
# INPUTS CARGA
# ============================

empilhavel = st.toggle(
    "📦 Permitir empilhamento (cálculo 3D)",
    value=False,   # padrão: não empilha
    key="empilhavel"
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

    st.session_state.editor_v += 1
    st.rerun()
    
# ============================
# LISTA E EDIÇÃO DE CARGAS
# ============================

if st.session_state.cargas:

    st.subheader("📋 Cargas adicionadas (Editáveis)")

    df_cargas_edit = pd.DataFrame(st.session_state.cargas)

    st.session_state.setdefault("editor_v", 0)
    
    df_editado = st.data_editor(
        df_cargas_edit,
        use_container_width=True,
        num_rows="dynamic",
        key=f"editor_cargas_{st.session_state.editor_v}",   # versionada
        hide_index=True,
        column_config={
            "Volume total (m³)": st.column_config.NumberColumn(disabled=True),
            "Peso total (kg)": st.column_config.NumberColumn(disabled=True),
        },
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
                    campos = ["Comprimento (m)", "Largura (m)", "Altura (m)", "Peso unitário (kg)", "Quantidade"]
                    if row[campos].isna().any():
                        raise ValueError("Há campos vazios na tabela.")
                    try:
                        comp = float(row["Comprimento (m)"])
                        larg = float(row["Largura (m)"])
                        alt = float(row["Altura (m)"])
                        peso = float(row["Peso unitário (kg)"])
                    except Exception:
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
                st.session_state.editor_v += 1
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao salvar alterações: {e}")

    # ❌ LIMPAR CARGA UNITÁRIA
    with col2:
        n = len(st.session_state.cargas)
        linha_para_excluir = st.selectbox(
            "Selecione a carga para excluir:",
            options=range(n),
            format_func=lambda i: f"Carga {i+1}",
        )
        if st.button("❌ Excluir carga selecionada"):
            del st.session_state.cargas[linha_para_excluir]
            st.session_state.editor_v += 1
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

def assinatura_atual():
    return hash((str(st.session_state.cargas), empilhavel, tuple(selecionados)))

# ============================
# AUXILIARES
# ============================
def reduzir_cargas_para_simulacao(cargas, limite):
    quantidades = [int(c["Quantidade"]) for c in cargas]
    total = sum(quantidades)

    if total <= 0 or limite <= 0:
        return []

    if total <= limite:
        amostras = quantidades[:]
    else:
        proporcoes = [q * limite / total for q in quantidades]
        amostras = [int(p) for p in proporcoes]

        restantes = limite - sum(amostras)
        ordem = sorted(
            range(len(proporcoes)),
            key=lambda i: proporcoes[i] - amostras[i],
            reverse=True,
        )

        for i in ordem[:restantes]:
            amostras[i] += 1

    unidades = []

    for carga, quantidade_amostra in zip(cargas, amostras):
        comp = float(carga["Comprimento (m)"])
        larg = float(carga["Largura (m)"])
        alt = float(carga["Altura (m)"])
        peso = float(carga["Peso unitário (kg)"])
        volume = comp * larg * alt

        if min(comp, larg, alt, peso) <= 0 or quantidade_amostra <= 0:
            continue

        item = {
            "comp": comp,
            "larg": larg,
            "alt": alt,
            "peso": peso,
            "densidade": peso / volume,
            "volume": volume,
        }
        unidades.extend(item.copy() for _ in range(quantidade_amostra))

    return unidades

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
    
def calcular_score(volume_total, capacidade, peso_total, peso_max, custo, custo_max=12):
    if capacidade <= 0 or peso_max <= 0:
        return 0
    oc_vol = volume_total / capacidade
    oc_peso = peso_total / peso_max
    limitante = max(oc_vol, oc_peso)          # o que realmente "enche" o veículo

    score = limitante * 70 + (1 - custo / custo_max) * 30
    if limitante > 0.95:                      # sem folga
        score -= 10
    return round(max(1, min(100, score)), 2)
    
# ============================
# EXPORTAR RESULTADOS PARA EXCEL
# ============================
def gerar_excel_bytes(df_result, cargas):
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df_result.to_excel(writer, sheet_name="Resultados", index=False)
        if cargas:
            pd.DataFrame(cargas).to_excel(writer, sheet_name="Cargas", index=False)
    return out.getvalue()
    
from itertools import permutations

EPS = 1e-6

def calcular_centro_massa(posicoes, pesos):
    peso_total = sum(pesos)
    if peso_total <= 0:
        return None
    return sum((x + c / 2) * peso for (x, _, _, c, _, _), peso in zip(posicoes, pesos)) / peso_total


def simular_empilhamento_3d(cargas_unitarias, veiculo, empilhavel=True):
    comp_v, larg_v, alt_v = veiculo["comprimento"], veiculo["largura"], veiculo["altura"]
    peso_max = veiculo["peso_max"]
    dim_v = sorted([comp_v, larg_v, alt_v])

    itens = sorted(
        cargas_unitarias,
        key=lambda x: (-x["densidade"], -(x["comp"] * x["larg"]), -x["volume"])
    )

    posicoes = []
    pesos_posicionados = []
    peso_acum = 0.0
    livres = [(0.0, 0.0, 0.0, comp_v, larg_v, alt_v)]

    for item in itens:
        dim_i = sorted([item["comp"], item["larg"], item["alt"]])
        if any(c > v + EPS for c, v in zip(dim_i, dim_v)):
            continue
        if item["peso"] <= 0 or peso_acum + item["peso"] > peso_max:
            continue

        if empilhavel:
            orientacoes = sorted(
                {tuple(round(d, 4) for d in p)
                 for p in permutations((item["comp"], item["larg"], item["alt"]))},
                key=lambda o: o[2]
            )
        else:
            # sem empilhar: a altura da caixa fica em pé, só gira no piso
            orientacoes = list({
                (round(item["comp"], 4), round(item["larg"], 4), round(item["alt"], 4)),
                (round(item["larg"], 4), round(item["comp"], 4), round(item["alt"], 4)),
            })

        livres.sort(key=lambda s: (s[2], s[0], s[1]))

        colocado = False
        for idx, (sx, sy, sz, sc, sl, sa) in enumerate(livres):
            for co, lo, ao in orientacoes:
                if co <= sc + EPS and lo <= sl + EPS and ao <= sa + EPS:
                    posicoes.append((sx, sy, sz, co, lo, ao))
                    pesos_posicionados.append(float(item["peso"]))
                    peso_acum += item["peso"]
                    livres.pop(idx)
                    livres += [
                        (sx + co, sy, sz, sc - co, sl, sa),        # lateral
                        (sx, sy + lo, sz, co, sl - lo, sa),        # frontal
                    ]
                    if empilhavel:                                  # só abre espaço em cima se permitido
                        livres.append((sx, sy, sz + ao, co, lo, sa - ao))
                    livres = [s for s in livres if s[3] > EPS and s[4] > EPS and s[5] > EPS]
                    if len(livres) > 1500:
                        livres = sorted(livres, key=lambda s: s[3]*s[4]*s[5], reverse=True)[:1500]
                    colocado = True
                    break
            if colocado:
                break

    volume_usado = sum(c * l * a for _, _, _, c, l, a in posicoes)
    centro_x = calcular_centro_massa(posicoes, pesos_posicionados)
    return posicoes, len(posicoes), volume_usado, peso_acum, centro_x

def calcular_volume_carga(carga, empilhavel=True):

    qtd = int(carga["Quantidade"])
    comp = float(carga["Comprimento (m)"])
    larg = float(carga["Largura (m)"])
    alt = float(carga["Altura (m)"])

    if empilhavel:
        return comp * larg * alt * qtd
    else:
        return comp * larg * qtd


def calcular_peso_carga(carga):

    return (
        float(carga["Peso unitário (kg)"])
        * int(carga["Quantidade"])
    )

def carga_cabe_no_veiculo(carga, veic, empilhavel=True):
    comp = float(carga["Comprimento (m)"])
    larg = float(carga["Largura (m)"])
    alt = float(carga["Altura (m)"])

    comp_v = float(veic["comprimento"])
    larg_v = float(veic["largura"])
    alt_v = float(veic["altura"])

    if empilhavel:
        # Permite girar a carga nos três eixos.
        dimensoes_ok = any(
            c <= comp_v and l <= larg_v and a <= alt_v
            for c, l, a in permutations((comp, larg, alt))
        )
    else:
        # Sem empilhamento, a altura da carga continua sendo a altura.
        dimensoes_ok = (
            (comp <= comp_v and larg <= larg_v and alt <= alt_v)
            or
            (larg <= comp_v and comp <= larg_v and alt <= alt_v)
        )

    peso_ok = calcular_peso_carga(carga) <= float(veic["peso_max"])
    return dimensoes_ok and peso_ok


ORDEM_CATEGORIAS = ["FIORINO", "VAN", "HR", "VUC", "TRES_QUARTOS",
                    "TOCO", "TRUCK", "BITRUCK", "CARRETA"]

def categorias_compativeis(c1, c2):
    if c1 == c2:
        return True
    if c1 not in ORDEM_CATEGORIAS or c2 not in ORDEM_CATEGORIAS:
        return False
    return abs(ORDEM_CATEGORIAS.index(c1) - ORDEM_CATEGORIAS.index(c2)) <= 1


def gerar_combinacoes(df_testar, valor_total, peso_total, empilhavel, cargas):
    if sum(int(c["Quantidade"]) for c in cargas) <= 1:
        return pd.DataFrame()

    cargas_ordenadas = sorted(
        enumerate(cargas, start=1),
        key=lambda t: -calcular_volume_carga(t[1], empilhavel)   # maiores primeiro
    )
    veiculos = [v for _, v in df_testar.iterrows()]
    combos = []

    for i, v1 in enumerate(veiculos):
        for v2 in veiculos[i:]:

            if not categorias_compativeis(
                categoria_veiculo(v1["Veículo"]), categoria_veiculo(v2["Veículo"])
            ):
                continue

            cap1 = capacidade_veiculo(v1, empilhavel)
            cap2 = capacidade_veiculo(v2, empilhavel)
            pmax1, pmax2 = v1["peso_max"], v2["peso_max"]

            aprov_vol = valor_total / (cap1 + cap2) * 100
            aprov_peso = peso_total / (pmax1 + pmax2) * 100
            if aprov_vol > 100 or aprov_peso > 100 or aprov_vol < 15:
                continue

            aloc1, aloc2 = [], []
            cargas_v1, cargas_v2 = [], []
            peso1 = peso2 = vol1 = vol2 = 0.0
            ok = True

            for idx, carga in cargas_ordenadas:
                vol_c = calcular_volume_carga(carga, empilhavel)
                peso_c = calcular_peso_carga(carga)

                pode1 = (
                    carga_cabe_no_veiculo(carga, v1, empilhavel)
                    and peso1 + peso_c <= pmax1
                    and vol1 + vol_c <= cap1
                )
                pode2 = (
                    carga_cabe_no_veiculo(carga, v2, empilhavel)
                    and peso2 + peso_c <= pmax2
                    and vol2 + vol_c <= cap2
                )

                if pode1 and (vol1 / cap1) <= (vol2 / cap2):
                    aloc1.append(f"Carga {idx}")
                    cargas_v1.append(dict(carga))
                    peso1 += peso_c; vol1 += vol_c
                elif pode2:
                    aloc2.append(f"Carga {idx}")
                    cargas_v2.append(dict(carga))
                    peso2 += peso_c; vol2 += vol_c
                elif pode1:
                    aloc1.append(f"Carga {idx}")
                    cargas_v1.append(dict(carga))
                    peso1 += peso_c; vol1 += vol_c
                else:
                    ok = False
                    break

            if not ok or not aloc1 or not aloc2:   # os dois veículos precisam ser usados
                continue

            score = calcular_score(
                valor_total, cap1 + cap2, peso_total, pmax1 + pmax2,
                v1["custo"] + v2["custo"], custo_max=24
            )

            combos.append({
                "Veículo": f'{v1["Veículo"]} + {v2["Veículo"]}',
                "Status": "Viável",
                "Motivo": (
                    f"Combo 100% viável. "
                    f"{v1['Veículo']}: {', '.join(aloc1)} ({vol1:.2f} m³ / {peso1:.0f} kg). "
                    f"{v2['Veículo']}: {', '.join(aloc2)} ({vol2:.2f} m³ / {peso2:.0f} kg)."
                ),
                "Cenário": "COMBO",
                "Aproveitamento (%)": round(aprov_vol, 2),
                "Aproveitamento Peso (%)": round(aprov_peso, 2),
                "Score": score,
                "_cargas_v1": cargas_v1,
                "_cargas_v2": cargas_v2,
            })

    return pd.DataFrame(combos)

def executar_calculo(cargas, df_veiculos, selecionados, empilhavel):
    """
    Função central do sistema.
    Responsável por:
    - Calcular viabilidade
    - Ranqueamento
    - Combos
    - Simulação 3D
    """

    if not cargas:
        return pd.DataFrame(columns=COLUNAS_RESULTADO), {"cenario": None}

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
    # Viabilidade básica e validação de encaixe
    # --------------------------------
    registros, candidatos = [], []

    for _, veic in df_testar.iterrows():
        nome = veic["Veículo"]
        peso_max = veic["peso_max"]
        capacidade_max = capacidade_veiculo(veic, empilhavel)
        motivos = []

        dimensoes_ok = all(
            carga_cabe_no_veiculo(carga, veic, empilhavel)
            for carga in cargas
        )
        if not dimensoes_ok:
            motivos.append("Dimensão excede")
        if peso_total > peso_max:
            motivos.append("Excede peso")
        if valor_total > capacidade_max:
            motivos.append("Excede capacidade")

        if motivos:
            registros.append({
                "Veículo": nome,
                "Status": "Inviável",
                "Motivo": " + ".join(motivos),
            })
            continue

        aprov_vol = valor_total / capacidade_max * 100
        aprov_peso = peso_total / peso_max * 100
        registro = {
            "Veículo": nome,
            "Status": "Viável",
            "Motivo": f"Volume/área: {aprov_vol:.1f}% | Peso: {aprov_peso:.1f}%",
            "Cenário": "RANKING",
            "Aproveitamento (%)": round(aprov_vol, 2),
            "Aproveitamento Peso (%)": round(aprov_peso, 2),
            "Score": calcular_score(
                valor_total, capacidade_max, peso_total, peso_max, veic["custo"]
            ),
        }
        candidatos.append((registro, veic))

    candidatos.sort(key=lambda item: item[0]["Score"], reverse=True)
    ranking = []
    simulacoes_aprovadas = 0
    total_unidades = sum(int(c["Quantidade"]) for c in cargas)
    unidades = reduzir_cargas_para_simulacao(cargas, total_unidades)

    for candidato, veic in candidatos:
        if simulacoes_aprovadas >= MAX_CENARIOS_SIMULACAO:
            candidato = dict(candidato)
            candidato["Status"] = "Não verificado"
            candidato["Motivo"] = (
                f"Não verificado por limite de desempenho; "
                f"capacidade estimada: {candidato['Motivo']}"
            )
            ranking.append(candidato)
            continue

        _, caixas_alocadas, _, _, _ = simular_empilhamento_3d(
            unidades, veic, empilhavel
        )
        if caixas_alocadas < len(unidades):
            registros.append({
                "Veículo": candidato["Veículo"],
                "Status": "Inviável",
                "Motivo": (
                    f"Não coube na simulação "
                    f"({caixas_alocadas} de {len(unidades)} caixas)."
                ),
            })
            continue

        simulacoes_aprovadas += 1
        ranking.append(candidato)

    df_descartados = pd.DataFrame(registros)

    if ranking:
        df_rank = (
            pd.DataFrame(ranking)
            .sort_values("Score", ascending=False)
            .reset_index(drop=True)
        )
        return df_rank.reindex(columns=COLUNAS_RESULTADO), {"cenario": "RANKING", "descartados": df_descartados}

    df_combo = gerar_combinacoes(df_testar, valor_total, peso_total, empilhavel, cargas)
    if not df_combo.empty:
        df_combo = df_combo.sort_values("Score", ascending=False).reset_index(drop=True)
        combos_resultado = []
        combos_aprovados = 0
        for _, combo in df_combo.iterrows():
            resultado_combo = combo.drop(labels=["_cargas_v1", "_cargas_v2"]).to_dict()
            if combos_aprovados >= MAX_CENARIOS_SIMULACAO:
                resultado_combo["Status"] = "Não verificado"
                resultado_combo["Motivo"] = (
                    f"Não verificado por limite de desempenho. Alocação estimada: {combo['Motivo']}"
                )
                combos_resultado.append(resultado_combo)
                continue

            veiculo_1_nome, veiculo_2_nome = combo["Veículo"].split(" + ", 1)
            veiculo_1 = df_testar[df_testar["Veículo"] == veiculo_1_nome].iloc[0]
            veiculo_2 = df_testar[df_testar["Veículo"] == veiculo_2_nome].iloc[0]
            cargas_1 = combo["_cargas_v1"]
            cargas_2 = combo["_cargas_v2"]
            unidades_1 = reduzir_cargas_para_simulacao(
                cargas_1, sum(int(c["Quantidade"]) for c in cargas_1)
            )
            unidades_2 = reduzir_cargas_para_simulacao(
                cargas_2, sum(int(c["Quantidade"]) for c in cargas_2)
            )
            _, alocadas_1, _, _, _ = simular_empilhamento_3d(
                unidades_1, veiculo_1, empilhavel
            )
            _, alocadas_2, _, _, _ = simular_empilhamento_3d(
                unidades_2, veiculo_2, empilhavel
            )
            if alocadas_1 < len(unidades_1) or alocadas_2 < len(unidades_2):
                continue

            combos_aprovados += 1
            combos_resultado.append(resultado_combo)

        if combos_resultado:
            df_verificados = pd.DataFrame(combos_resultado)
            df_verificados = df_verificados.sort_values("Score", ascending=False).reset_index(drop=True)
            return df_verificados.reindex(columns=COLUNAS_RESULTADO), {"cenario": "COMBO", "descartados": df_descartados}

    return pd.DataFrame([{
        "Veículo": "Nenhum",
        "Status": "Inviável",
        "Motivo": "Nenhum veículo ou combo conseguiu acomodar 100% da carga.",
        "Cenário": "INVIÁVEL",
        "Aproveitamento (%)": 0,
        "Aproveitamento Peso (%)": 0,
        "Score": 0,
    }]).reindex(columns=COLUNAS_RESULTADO), {"cenario": None, "descartados": df_descartados}

def limpar_dataframe(df):
    df = df.reindex(columns=COLUNAS_RESULTADO)
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
            st.session_state.cargas, df_veiculos, selecionados, empilhavel
        )
        st.session_state.df_result = limpar_dataframe(df_result)
        st.session_state.cenario = meta.get("cenario")
        st.session_state.descartados = meta.get("descartados")
        st.session_state.assinatura_calculo = assinatura_atual()
        st.session_state.mostrar_3d = False

    if st.session_state.cenario == "RANKING":
        st.success("✅ Melhor opção encontrada após validação de capacidade e encaixe.")
    elif st.session_state.cenario == "COMBO":
        st.warning("⚠ Nenhum veículo único atende. Combo viável encontrado.")
    else:
        st.info("Nenhum cenário definido.")

# ============================
# 📊 EXIBIÇÃO DOS RESULTADOS
# ============================
df_res = st.session_state.df_result
calculou = st.session_state.assinatura_calculo is not None
resultado_valido = calculou and st.session_state.assinatura_calculo == assinatura_atual()
resultado_ok = (
    resultado_valido
    and not df_res.empty
    and df_res.iloc[0]["Status"] == "Viável"
)

if calculou:
    st.divider()

    if not resultado_valido:
        st.warning("⚠ Cargas ou parâmetros mudaram desde o último cálculo. Clique em **Calcular** novamente.")

    elif not resultado_ok:
        st.error(df_res.iloc[0]["Motivo"] if not df_res.empty else "Nenhum veículo atendeu aos critérios.")
        st.info("💡 Dica: reduza a carga, remova o filtro de veículos ou divida o pedido.")

    else:
        st.subheader("🏆 Ranking e verificação dos cenários")
        df_rank = df_res.copy()
        df_rank.insert(0, "Ranking", df_rank.index + 1)
        melhor = df_rank.iloc[0]

        st.markdown("### 🏆 Melhor opção encontrada")
        st.success(f"**{melhor['Veículo']}**")
        
        st.markdown("#### Motivo da escolha")
        
        if " + " in str(melhor["Veículo"]):
            st.write(melhor["Motivo"])
        else:
            tipo_ocupacao = "volume" if empilhavel else "área do piso"
        
            st.write(
                f"O veículo passou nas verificações de dimensões, peso e capacidade. "
                f"O aproveitamento de {tipo_ocupacao} é "
                f"**{float(melhor['Aproveitamento (%)']):.2f}%**."
            )
            st.write(
                f"O aproveitamento do limite de peso é "
                f"**{float(melhor['Aproveitamento Peso (%)']):.2f}%**."
            )
        
        st.write(f"Pontuação do ranking: **{float(melhor['Score']):.2f} / 100**")
        st.caption(

        )

        def destacar(row):
            if row["Veículo"] == melhor["Veículo"]:
                return ["background-color:#145A32;color:white;font-weight:bold"] * len(row)
            return [""] * len(row)

        st.dataframe(df_rank.style.apply(destacar, axis=1), use_container_width=True)

        desc = st.session_state.descartados
        if isinstance(desc, pd.DataFrame) and not desc.empty:
            with st.expander(f"Veículos descartados ({len(desc)})"):
                st.dataframe(desc[["Veículo", "Motivo"]], use_container_width=True, hide_index=True)


# ============================
# 🔍 SIMULAÇÃO 3D
# ============================
    
def criar_mesh_caixas(posicoes, cores):
    if not posicoes:
        return None

    triangulos = [
        (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
        (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7),
    ]
    xs, ys, zs = [], [], []
    ii, jj, kk, facecolors = [], [], [], []
    for n, (x, y, z, comp, larg, alt) in enumerate(posicoes):
        base = 8 * n
        xs.extend([x, x + comp, x + comp, x, x, x + comp, x + comp, x])
        ys.extend([y, y, y + larg, y + larg, y, y, y + larg, y + larg])
        zs.extend([z, z, z, z, z + alt, z + alt, z + alt, z + alt])
        for a, b, c in triangulos:
            ii.append(base + a)
            jj.append(base + b)
            kk.append(base + c)
            facecolors.append(cores[n % len(cores)])
    return go.Mesh3d(
        x=xs, y=ys, z=zs, i=ii, j=jj, k=kk,
        facecolor=facecolors, opacity=0.5, flatshading=True, showscale=False,
    )


def render_simulacao_3d():
    if not resultado_ok:
        return

    melhor_veiculo = df_res.iloc[0]["Veículo"]

    if " + " in melhor_veiculo:
        st.warning(
            "Simulação 3D para combos ainda não implementada. "
            "O combo já foi validado pela distribuição de cargas."
        )
        return

    veic = df_veiculos[df_veiculos["Veículo"] == melhor_veiculo].iloc[0]
    cargas = st.session_state.cargas

    qtd_total_real = int(sum(c["Quantidade"] for c in cargas))
    cargas_unitarias = reduzir_cargas_para_simulacao(cargas, qtd_total_real)
    qtd_simulada = len(cargas_unitarias)

    posicoes, caixas, volume_usado, peso_usado, centro_x = simular_empilhamento_3d(
        cargas_unitarias, veic, empilhavel
    )

    if empilhavel:
        ocupacao = min(100, volume_usado / volume_veiculo(veic) * 100)
        rotulo_ocup = "Ocupação (volume)"
    else:
        area_usada = sum(c * l for _, _, _, c, l, _ in posicoes)
        area_piso = veic["comprimento"] * veic["largura"]
        ocupacao = min(100, area_usada / area_piso * 100) if area_piso else 0
        rotulo_ocup = "Ocupação (área do piso)"

    st.subheader("📦 Resultado da Simulação 3D")
    st.caption("Modo: " + ("com empilhamento" if empilhavel else "sem empilhamento (somente no piso)"))
    st.write(f"Veículo: **{melhor_veiculo}**")
    st.write(f"Caixas alocadas: **{caixas}** de {qtd_total_real}")
    st.write(f"{rotulo_ocup}: **{ocupacao:.2f}%**")
    st.write(f"Peso carregado: **{peso_usado:,.2f} kg**")
    if centro_x is not None and veic["comprimento"] > 0:
        centro_pct = centro_x / veic["comprimento"] * 100
        st.caption(
            f"Centro de carga ponderado pelo peso: x = {centro_x:.2f} m "
            f"({centro_pct:.1f}% do comprimento, origem do gráfico)."
        )
    if caixas < qtd_simulada:
        st.error("⚠ Nem todas as caixas couberam.")
    else:
        st.success("✅ Todas as caixas foram alocadas.")

    fig = go.Figure()
    cores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    mesh_caixas = criar_mesh_caixas(posicoes, cores)
    if mesh_caixas is not None:
        fig.add_trace(mesh_caixas)

    C, L, A = veic["comprimento"], veic["largura"], veic["altura"]
    fig.add_trace(go.Scatter3d(
        x=[0, C, C, 0, 0, C, C, 0], y=[0, 0, L, L, 0, 0, L, L],
        z=[0, 0, 0, 0, A, A, A, A],
        mode="markers", marker=dict(size=2, color="gray", opacity=0.05),
        showlegend=False
    ))
    fig.update_layout(
        title=f"Ocupação: {ocupacao:.1f}%",
        scene=dict(aspectmode="manual", aspectratio=dict(x=C, y=L, z=A)),
        height=700
    )
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

# ============================
# 🔍 3D + EXCEL (só com resultado válido)
# ============================
if resultado_ok:

    st.divider()
    if st.button("🔍 Simular Empilhamento 3D", key="btn_3d"):
        st.session_state.mostrar_3d = True
    if st.session_state.mostrar_3d:
        render_simulacao_3d()

    st.download_button(
        "📥 Baixar Excel",
        data=gerar_excel_bytes(st.session_state.df_result, st.session_state.cargas),
        file_name="dimensionamento_veiculos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


