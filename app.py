import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Radar Imobiliário - Salvador", layout="wide")

# Dados Iniciais da sua Planilha
DADOS_INICIAIS = [
    {
        "id": 1,
        "titulo": "Ap 3Q - Território do Rio Branco",
        "bairro": "Pituba",
        "area_m2": 103,
        "quartos": 3,
        "suites": 1,
        "vagas": 2,
        "andar": 8,
        "posicao": "Nascente",
        "valor": 950000.0,
        "condominio": 753.0,
        "iptu_mes": 420.0,
        "lat": -13.0035,
        "lon": -38.4612,
        "link": "https://www.vivareal.com.br/imovel/apartamento-3-quartos-pituba-bairros-salvador-com-garagem-103m2-venda-RS950000-id-2714961945/"
    },
    {
        "id": 2,
        "titulo": "Ap 3Q - Jardim de Giverny",
        "bairro": "Pituba",
        "area_m2": 104,
        "quartos": 3,
        "suites": 1,
        "vagas": 2,
        "andar": 5,
        "posicao": "Nascente",
        "valor": 1050000.0,
        "condominio": 600.0,
        "iptu_mes": 449.0,
        "lat": -13.0041,
        "lon": -38.4608,
        "link": "https://www.vivareal.com.br/imovel/apartamento-3-quartos-pituba-bairros-salvador-com-garagem-104m2-venda-RS1040000-id-2697518430/"
    },
    {
        "id": 3,
        "titulo": "Ap 4Q - Rua Machado Neto",
        "bairro": "Pituba",
        "area_m2": 132,
        "quartos": 4,
        "suites": 3,
        "vagas": 2,
        "andar": 7,
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

st.title("🏢 Radar Imobiliário Inteligente")
st.caption("Módulo de Prospecção e Análise Multicritério - Obras Inteligentes")

# 1. Formulário de Cadastro via Link
with st.expander("➕ Cadastrar Novo Apartamento por Link", expanded=False):
    link_input = st.text_input("Cole aqui o link do anúncio (VivaReal, Zap, etc.):")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        titulo = st.text_input("Título / Apelido do Imóvel", value="Ap Pituba")
        bairro = st.selectbox("Bairro", ["Pituba", "Itaigara", "Caminho das Árvores", "Graça", "Barra", "Horto Florestal"])
        valor = st.number_input("Valor de Venda (R$)", value=950000, step=10000)
    with col2:
        area = st.number_input("Área Útil (m²)", value=100, step=5)
        quartos = st.number_input("Quartos", value=3, step=1)
        suites = st.number_input("Suítes", value=1, step=1)
    with col3:
        condo = st.number_input("Condomínio (R$)", value=650, step=50)
        iptu = st.number_input("IPTU Mensal (R$)", value=400, step=50)
        posicao = st.selectbox("Posição Solar", ["Nascente", "Poente"])

    if st.button("Salvar Imóvel no Radar"):
        novo_imovel = {
            "id": len(st.session_state.imoveis) + 1,
            "titulo": titulo,
            "bairro": bairro,
            "area_m2": area,
            "quartos": quartos,
            "suites": suites,
            "vagas": 2,
            "andar": 5,
            "posicao": posicao,
            "valor": float(valor),
            "condominio": float(condo),
            "iptu_mes": float(iptu),
            "lat": -13.0010 + (len(st.session_state.imoveis) * 0.001), # Pequena variação geográfica
            "lon": -38.4620 + (len(st.session_state.imoveis) * 0.001),
            "link": link_input or "#"
        }
        st.session_state.imoveis.append(novo_imovel)
        st.success("Imóvel cadastrado com sucesso!")

# 2. Processamento e Tabela
df = pd.DataFrame(st.session_state.imoveis)
df["Custo m²"] = df["valor"] / df["area_m2"]
df["Custo Fixo Mensal"] = df["condominio"] + df["iptu_mes"]
df["Custo Fixo/m²"] = df["Custo Fixo Mensal"] / df["area_m2"]

# Avaliação de Segurança com base no contexto Fogo Cruzado
bairros_atencao = ["Jardim Nova Esperança", "Mata Escura", "Paripe", "São Cristóvão", "Areia Branca", "IAPI", "São Marcos"]
df["Segurança"] = df["bairro"].apply(lambda b: "Atenção (Incidentes Recentes)" if b in bairros_atencao else "Estável / Monitorado")

# 3. Métricas Resumo
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Cadastrados", len(df))
col_m2.metric("Média Preço/m²", f"R$ {df['Custo m²'].mean():,.2f}")
col_m3.metric("Menor Custo Fixo/m²", f"R$ {df['Custo Fixo/m²'].min():,.2f}")
col_m4.metric("Bairro Principal", df["bairro"].mode()[0])

st.divider()

# 4. Visualização no Mapa
st.subheader("📍 Mapa dos Apartamentos e Entorno")
col_map, col_list = st.columns([2, 1])

with col_map:
    # Centraliza o mapa em Salvador (Pituba)
    m = folium.Map(location=[-13.002, -38.462], zoom_start=14)
    
    for _, item in df.iterrows():
        popup_html = f"""
        <b>{item['titulo']}</b><br>
        Área: {item['area_m2']} m² | {item['quartos']}Q ({item['suites']}S)<br>
        <b>Valor:</b> R$ {item['valor']:,.2f}<br>
        <b>Custo/m²:</b> R$ {item['Custo m²']:,.2f}<br>
        <b>Custo Fixo:</b> R$ {item['Custo Fixo Mensal']:,.2f}/mês<br>
        <a href="{item['link']}" target="_blank">Abrir Anúncio</a>
        """
        folium.Marker(
            location=[item["lat"], item["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{item['titulo']} - R$ {item['valor']:,.0f}",
            icon=folium.Icon(color="green" if item["Custo m²"] < 9500 else "blue", icon="home")
        ).add_to(m)

    st_folium(m, width="100%", height=450)

with col_list:
    st.subheader("🏆 Ranking por Custo/m²")
    df_ranking = df.sort_values(by="Custo m²")[["titulo", "Custo m²", "Custo Fixo Mensal", "Segurança"]]
    st.dataframe(df_ranking, use_container_width=True, hide_index=True)

# 5. Tabela Geral com Dados Tratados
st.subheader("📋 Planilha Completa e Tratada")
st.dataframe(
    df[["titulo", "bairro", "area_m2", "quartos", "posicao", "valor", "Custo m²", "Custo Fixo Mensal", "Custo Fixo/m²", "Segurança"]],
    use_container_width=True
)
