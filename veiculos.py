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

if "df_result" not in st.session_state:
    st.session_state.df_result = pd.DataFrame()

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

col1, col2, col3, col4, col5 = st.columns(5)

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


# conversão
comp = parse_float(comp_txt)
larg = parse_float(larg_txt)
alt = parse_float(alt_txt)
peso = parse_float(peso_txt)


erros = validar_inputs(comp, larg, alt, peso, qtd)

if erros:
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
            alt  = float(c["Altura (m)"])
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


def cabe_no_piso_heuristica(items, comp_v, larg_v, alt_v):
    """
    Heurística simplificada de empacotamento 2D + camadas.
    Retorna True se a heurística indicar que cabe,
    False se claramente não cabe.
    """

    if not items:
        return True

    items = sorted(
        items,
        key=lambda x: x["comp"] * x["larg"] * x["alt"],
        reverse=True
    )

    camadas = []
    altura_usada = 0

    for it in items:

        colocado = False

        for comp_i, larg_i in (
            (it["comp"], it["larg"]),
            (it["larg"], it["comp"])
        ):

            if comp_i > comp_v or larg_i > larg_v:
                continue

            # tenta encaixar na camada atual
            for camada in camadas:
                if camada["len"] + comp_i <= comp_v:
                    camada["len"] += comp_i
                    colocado = True
                    break

            if colocado:
                break

            # cria nova camada
            if altura_usada + it["alt"] <= alt_v:
                camadas.append({"len": comp_i})
                altura_usada += it["alt"]
                colocado = True
                break

        if not colocado:
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

    # ordenar veículos
    veiculos_ordenados = df_veiculos.sort_values(
        by="Capacidade Volume (m³)",
        ascending=True
    )

    resultado = []
    cargas_restantes = cargas_unit.copy()
    
    # alerta de cargas impossíveis
    if any(c["peso"] > df_veiculos["peso_max"].max() for c in cargas_restantes):
        st.warning("⚠ Existem cargas com peso maior que qualquer veículo disponível.")

    # ✅ TUDO DENTRO DA FUNÇÃO
    while cargas_restantes:

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

#AJUSTE

def executar_calculo(cargas, df_veiculos, selecionados):
    """
    Executa todo o cálculo de dimensionamento.
    Retorna:
        df_result (DataFrame)
        is_multi_veiculo (bool)
    """

    if not cargas:
        return pd.DataFrame(), False

    # filtrar veículos
    if selecionados:
        df_testar = df_veiculos[df_veiculos["Veículo"].isin(selecionados)]
    else:
        df_testar = df_veiculos.copy()

    volume_total, peso_total = calcular_totais(cargas)

    cargas_unit = expand_cargas_unitarias(cargas)

    resultados_viabilidade = []

    for _, veic in df_testar.iterrows():
        comp = veic["comprimento"]
        larg = veic["largura"]
        alt = veic["altura"]
        peso_max = veic["peso_max"]

        volume_veic = comp * larg * alt

        status = "Viável"
        motivo = ""

        if volume_total > volume_veic:
            status = "Inviável"
            motivo = "Excede volume"
        elif peso_total > peso_max:
            status = "Inviável"
            motivo = "Excede peso"
        elif not cabe_no_piso_heuristica(cargas_unit, comp, larg, alt):
            status = "Inviável"
            motivo = "Não cabe fisicamente"

        resultados_viabilidade.append({
            "Veículo": veic["Veículo"],
            "Status": status,
            "Motivo": motivo,
            "Volume Veículo": volume_veic,
            "Peso Máx": peso_max
        })

    df_status = pd.DataFrame(resultados_viabilidade)

    if (df_status["Status"] == "Viável").any():
        # ranking
        resultados = []

        for _, row in df_status[df_status["Status"] == "Viável"].iterrows():
            score = calcular_score(
                volume_total,
                row["Volume Veículo"],
                peso_total,
                row["Peso Máx"]
            )

            resultados.append({
                "Veículo": row["Veículo"],
                "Status": "Viável",
                "Motivo": "",
                "Aproveitamento Volume (%)": round(volume_total / row["Volume Veículo"] * 100, 2),
                "Aproveitamento Peso (%)": round(peso_total / row["Peso Máx"] * 100, 2),
                "Score": score
            })

        return pd.DataFrame(resultados), False

    # fallback multi-veículo
    resultado_multi, _ = calcular_multi_veiculos(cargas, df_testar)
    return pd.DataFrame(resultado_multi), True

# ============================
# 🚀 BOTÃO CALCULAR
# ============================
btn_calcular = st.button(
    "🚀 Calcular Dimensionamento",
    disabled=not st.session_state.cargas
)

executar_melhor_veiculo = True

if btn_calcular:
    with st.spinner("Calculando melhor cenário..."):
        df_result, eh_multi = executar_calculo(
            st.session_state.cargas,
            df_veiculos,
            selecionados
        )

    if df_result.empty:
        st.warning("Nenhum resultado encontrado.")
    else:
        st.session_state.df_result = df_result

        if eh_multi:
            st.warning("⚠ Resultado gerado em modo multi-veículo.")
        else:
            st.success("✅ Cálculo concluído com sucesso!")

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
    else:
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
    else:

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
            
            STEP = max(1, min(x_max, y_max, z_max) // 10)
            
            for x in range(0, x_max, STEP):
                if estourou_limite:
                    break
            
                for y in range(0, y_max, STEP):
                    if estourou_limite:
                        break
            
                    for z in range(0, z_max, STEP):
        
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

    eficiencia = calcular_score(
        volume_usado,
        volume_veiculo,
        peso_acumulado,
        veic["peso_max"]
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
