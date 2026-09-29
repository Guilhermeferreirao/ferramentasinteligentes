import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Radar Imobiliário", page_icon="🏢", layout="wide")

st.title("🏢 Módulo 1: Radar de Apartamentos")
st.caption("Prospecção, análise de custos e visualização geográfica")

# Dados Iniciais da Planilha
DADOS_INICIAIS = [
    {
        "id": 1,
        "titulo": "Ap 3Q - Território do Rio Branco",
        "bairro": "Pituba",
        "area_m2": 103,
        "quartos": 3,
        "suites": 1,
        "vagas": 2,
        "posicao": "Nascente",
        "valor": 950000.0,
        "condominio": 753.0,
        "iptu_mes": 420.0,
        "lat": -13.0035,
        "lon": -38.4612,
        "link": "https://www.vivareal.com.br"
    },
    {
        "id": 2,
        "titulo": "Ap 3Q - Jardim de Giverny",
        "bairro": "Pituba",
        "area_m2": 104,
        "quartos": 3,
        "suites": 1,
        "vagas": 2,
        "posicao": "Nascente",
        "valor": 1050000.0,
        "condominio": 600.0,
        "iptu_mes": 449.0,
        "lat": -13.0041,
        "lon": -38.4608,
        "link": "https://www.vivareal.com.br"
    },
    {
        "id": 3,
        "titulo": "Ap 4Q - Rua Machado Neto",
        "bairro": "Pituba",
        "area_m2": 132,
        "quartos": 4,
        "suites": 3,
        "vagas": 2,
        "posicao": "Nascente",
        "valor": 1090000.0,
        "condominio": 980.0,
        "iptu_mes": 361.0,
        "lat": -12.9980,
        "lon": -38.4650,
        "link": "https://www.chavesnamao.com.br"
    }
]

if "imoveis" not in st.session_state:
    st.session_state.imoveis = DADOS_INICIAIS

# Formulário de Cadastro
with st.expander("➕ Cadastrar Novo Imóvel", expanded=False):
    link_input = st.text_input("Link do anúncio:")
    c1, c2, c3 = st.columns(3)
    with c1:
        titulo = st.text_input("Título / Apelido", value="Ap Pituba Novo")
        bairro = st.selectbox("Bairro", ["Pituba", "Itaigara", "Caminho das Árvores", "Graça", "Barra"])
        valor = st.number_input("Valor de Venda (R$)", value=980000, step=10000)
    with c2:
        area = st.number_input("Área Útil (m²)", value=105, step=5)
        quartos = st.number_input("Quartos", value=3, step=1)
        suites = st.number_input("Suítes", value=1, step=1)
    with c3:
        condo = st.number_input("Condomínio Mensal (R$)", value=700, step=50)
        iptu = st.number_input("IPTU Mensal (R$)", value=400, step=50)
        posicao = st.selectbox("Posição Solar", ["Nascente", "Poente"])

    if st.button("Salvar no Radar"):
        novo = {
            "id": len(st.session_state.imoveis) + 1,
            "titulo": titulo,
            "bairro": bairro,
            "area_m2": area,
            "quartos": quartos,
            "suites": suites,
            "vagas": 2,
            "posicao": posicao,
            "valor": float(valor),
            "condominio": float(condo),
            "iptu_mes": float(iptu),
            "lat": -13.0020 + (len(st.session_state.imoveis) * 0.001),
            "lon": -38.4615 + (len(st.session_state.imoveis) * 0.001),
            "link": link_input or "#"
        }
        st.session_state.imoveis.append(novo)
        st.success("Apartamento registrado com sucesso!")

# Processamento
df = pd.DataFrame(st.session_state.imoveis)
df["Custo m²"] = df["valor"] / df["area_m2"]
df["Custo Fixo Mensal"] = df["condominio"] + df["iptu_mes"]
df["Custo Fixo/m²"] = df["Custo Fixo Mensal"] / df["area_m2"]

# Métricas
m1, m2, m3 = st.columns(3)
m1.metric("Imóveis em Monitoramento", len(df))
m2.metric("Preço Médio por m²", f"R$ {df['Custo m²'].mean():,.2f}")
m3.metric("Menor Custo Fixo/m²", f"R$ {df['Custo Fixo/m²'].min():,.2f}")

st.divider()

# Mapa e Tabela
col_map, col_tab = st.columns([3, 2])

with col_map:
    st.subheader("📍 Mapa de Apartamentos")
    m = folium.Map(location=[-13.002, -38.462], zoom_start=14)
    for _, item in df.iterrows():
        folium.Marker(
            location=[item["lat"], item["lon"]],
            tooltip=f"{item['titulo']} - R$ {item['valor']:,.0f}",
            popup=f"<b>{item['titulo']}</b><br>Valor: R$ {item['valor']:,.2f}<br>Custo m²: R$ {item['Custo m²']:,.2f}",
            icon=folium.Icon(color="green" if item["Custo m²"] < 9500 else "blue", icon="home")
        ).add_to(m)
    st_folium(m, width="100%", height=400)

with col_tab:
    st.subheader("📋 Comparativo Direto")
    st.dataframe(
        df[["titulo", "area_m2", "valor", "Custo m²", "Custo Fixo Mensal"]],
        use_container_width=True,
        hide_index=True
    )
