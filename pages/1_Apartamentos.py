import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image

st.set_page_config(page_title="Radar Imobiliário", page_icon="🏢", layout="wide")

# ==========================================
# 1. ESTILIZAÇÃO VISUAL (CSS MODERNIZADO)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .metric-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-title { font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; color: #0f172a; font-weight: 700; margin-top: 5px; }
    
    .prop-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); transition: transform 0.2s ease;
    }
    .prop-card:hover { transform: translateY(-3px); border-color: #3b82f6; }
    .prop-title { font-size: 1.2rem; font-weight: 700; color: #1e293b; margin-bottom: 10px; }
    .prop-tag { background: #eff6ff; color: #2563eb; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; margin-right: 5px; }
    .prop-price { font-size: 1.4rem; color: #059669; font-weight: 700; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DADOS (COM SUPORTE A FOTOS)
# ==========================================
if "imoveis" not in st.session_state:
    st.session_state.imoveis = [
        {
            "id": 1, "titulo": "Ap 3Q • Território do Rio Branco", "bairro": "Pituba",
            "area_m2": 103, "quartos": 3, "suites": 1, "vagas": 2, "posicao": "Nascente",
            "valor": 950000.0, "condominio": 753.0, "iptu_mes": 420.0,
            "lat": -13.0035, "lon": -38.4612, "link": "https://www.vivareal.com.br", "fotos": []
        },
        {
            "id": 2, "titulo": "Ap 3Q • Ed. Jardim de Giverny", "bairro": "Pituba",
            "area_m2": 104, "quartos": 3, "suites": 1, "vagas": 2, "posicao": "Nascente",
            "valor": 1050000.0, "condominio": 600.0, "iptu_mes": 449.0,
            "lat": -13.0041, "lon": -38.4608, "link": "https://www.vivareal.com.br", "fotos": []
        }
    ]

# Função para atualizar cálculos dinâmicos
def get_df():
    df = pd.DataFrame(st.session_state.imoveis)
    df["Custo_m2"] = df["valor"] / df["area_m2"]
    df["Custo_Fixo"] = df["condominio"] + df["iptu_mes"]
    return df

df = get_df()

st.title("🏢 Radar Imobiliário Inteligente")
st.markdown("Gerencie seus apartamentos favoritos, compare preços e monte sua galeria de fotos.")
st.write("")

# ==========================================
# 3. ORGANIZAÇÃO EM ABAS (TABS)
# ==========================================
tab_dashboard, tab_catalogo, tab_cadastro = st.tabs([
    "📍 Dashboard & Mapa", 
    "🖼️ Catálogo & Fotos", 
    "➕ Cadastrar Novo Imóvel"
])

# ------------------------------------------
# ABA 1: DASHBOARD & MAPA
# ------------------------------------------
with tab_dashboard:
    # KPIs Topo
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-box'><div class='metric-title'>Imóveis Analisados</div><div class='metric-value'>{len(df)}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-box'><div class='metric-title'>Média Preço / m²</div><div class='metric-value'>R$ {df['Custo_m2'].mean():,.0f}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-box'><div class='metric-title'>Melhor Preço / m²</div><div class='metric-value' style='color:#059669;'>R$ {df['Custo_m2'].min():,.0f}</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-box'><div class='metric-title'>Custo Fixo Médio</div><div class='metric-value'>R$ {df['Custo_Fixo'].mean():,.0f}</div></div>", unsafe_allow_html=True)
    
    st.write("---")
    
    col_mapa, col_rank = st.columns([2, 1])
    with col_mapa:
        st.subheader("Mapa de Oportunidades")
        m = folium.Map(location=[-13.002, -38.462], zoom_start=15, tiles="CartoDB positron")
        for _, row in df.iterrows():
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=f"<b>{row['titulo']}</b><br>R$ {row['valor']:,.0f}<br>R$ {row['Custo_m2']:,.0f}/m²",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
        st_folium(m, width="100%", height=450)
        
    with col_rank:
        st.subheader("🏆 Ranking (Custo/m²)")
        st.dataframe(
            df.sort_values(by="Custo_m2")[["titulo", "Custo_m2", "valor"]].style.format({"Custo_m2": "R$ {:.0f}", "valor": "R$ {:.0f}"}),
            hide_index=True, use_container_width=True
        )

# ------------------------------------------
# ABA 2: CATÁLOGO DE IMÓVEIS E FOTOS
# ------------------------------------------
with tab_catalogo:
    st.subheader("🖼️ Galeria de Apartamentos")
    
    # Grid de Cartões
    for imovel in st.session_state.imoveis:
        custo_m2 = imovel['valor'] / imovel['area_m2']
        custo_fixo = imovel['condominio'] + imovel['iptu_mes']
        
        with st.container():
            st.markdown(f"""
            <div class="prop-card">
                <div class="prop-title">{imovel['titulo']}</div>
                <div>
                    <span class="prop-tag">📐 {imovel['area_m2']} m²</span>
                    <span class="prop-tag">🛌 {imovel['quartos']} Quartos ({imovel['suites']} Suítes)</span>
                    <span class="prop-tag">🚗 {imovel['vagas']} Vagas</span>
                    <span class="prop-tag">☀️ {imovel['posicao']}</span>
                </div>
                <div class="prop-price">R$ {imovel['valor']:,.0f} <span style="font-size:0.9rem; color:#64748b; font-weight:500;">(R$ {custo_m2:,.0f}/m²)</span></div>
                <div style="font-size:0.9rem; color:#64748b; margin-top:5px;">Custo Fixo (Condomínio + IPTU): R$ {custo_fixo:,.0f}/mês</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Exibir Fotos
            if imovel.get("fotos"):
                st.write("**Galeria de Fotos:**")
                cols = st.columns(min(len(imovel["fotos"]), 4)) # Mostra até 4 fotos lado a lado
                for idx, foto in enumerate(imovel["fotos"]):
                    with cols[idx % 4]:
                        st.image(foto, use_column_width=True)
            else:
                st.caption("Nenhuma foto anexada a este imóvel.")
                
            st.write("---")

# ------------------------------------------
# ABA 3: CADASTRO COM UPLOAD DE FOTOS
# ------------------------------------------
with tab_cadastro:
    st.subheader("➕ Novo Apartamento")
    
    with st.form("form_novo_imovel", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**1. Informações Básicas**")
            titulo = st.text_input("Identificação (Ex: Edf. Vista Mar)")
            bairro = st.selectbox("Bairro", ["Pituba", "Itaigara", "Caminho das Árvores", "Graça"])
            link = st.text_input("Link do Anúncio (Opcional)")
            
            st.markdown("**2. Valores**")
            valor = st.number_input("Valor Pedido (R$)", min_value=0.0, value=900000.0, step=10000.0)
            cond = st.number_input("Condomínio (R$)", min_value=0.0, value=700.0, step=50.0)
            iptu = st.number_input("IPTU Mensal (R$)", min_value=0.0, value=300.0, step=50.0)
            
        with col2:
            st.markdown("**3. Características**")
            area = st.number_input("Área Útil (m²)", min_value=1.0, value=100.0, step=5.0)
            qts = st.number_input("Quartos", min_value=1, value=3, step=1)
            sts = st.number_input("Suítes", min_value=0, value=1, step=1)
            vagas = st.number_input("Vagas de Garagem", min_value=0, value=2, step=1)
            posicao = st.selectbox("Posição Solar", ["Nascente", "Poente", "Norte", "Sul"])
            
            st.markdown("**4. Galeria de Imagens**")
            # Upload múltiplo de fotos
            fotos_upload = st.file_uploader("Arraste fotos do imóvel aqui", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            
        submit = st.form_submit_button("Salvar Imóvel e Fotos", type="primary")
        
        if submit and titulo:
            # Lendo as imagens carregadas
            fotos_processadas = []
            if fotos_upload:
                for img_file in fotos_upload:
                    img = Image.open(img_file)
                    fotos_processadas.append(img)
            
            novo = {
                "id": len(st.session_state.imoveis) + 1,
                "titulo": titulo,
                "bairro": bairro,
                "area_m2": area,
                "quartos": qts,
                "suites": sts,
                "vagas": vagas,
                "posicao": posicao,
                "valor": valor,
                "condominio": cond,
                "iptu_mes": iptu,
                "lat": -13.0030 + (len(st.session_state.imoveis) * 0.001), # Simulação no mapa
                "lon": -38.4610 + (len(st.session_state.imoveis) * 0.001),
                "link": link if link else "#",
                "fotos": fotos_processadas
            }
            st.session_state.imoveis.append(novo)
            st.success("✅ Imóvel cadastrado com sucesso! Acesse a aba 'Catálogo & Fotos' para visualizar.")
            st.rerun()
