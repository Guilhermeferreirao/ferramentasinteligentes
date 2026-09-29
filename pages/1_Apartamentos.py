import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(page_title="Radar Imobiliário", page_icon="✨", layout="wide")

# ==========================================
# 1. MOTOR DE DESIGN ULTRA-MODERNO (CSS)
# ==========================================
st.markdown("""
<style>
    /* Fonte Moderna (Outfit) */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
        background-color: #F8FAFC;
    }
    
    /* Esconder elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Título com Gradiente */
    .gradient-text {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    /* Subtítulo */
    .sub-text { color: #64748B; font-size: 1.1rem; font-weight: 400; margin-bottom: 2rem; }

    /* Estilização das Abas (Tabs) do Streamlit */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: white;
        padding: 10px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 10px;
        padding: 0px 20px;
        background-color: transparent;
        border: none !important;
        font-weight: 600;
        color: #64748B;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #EFF6FF 0%, #F5F3FF 100%);
        color: #2563EB !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* Cartões de Métricas Modernos */
    .metric-glass {
        background: white;
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.02);
        transition: transform 0.3s ease;
    }
    .metric-glass:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05); }
    .m-title { font-size: 0.85rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;}
    .m-value { font-size: 2rem; color: #0F172A; font-weight: 800; margin-top: 8px; line-height: 1;}
    .m-highlight { color: #10B981; } /* Verde Esmeralda */

    /* Cartão do Catálogo de Imóveis (Estilo Airbnb) */
    .prop-card {
        background: white;
        border-radius: 24px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
        transition: all 0.3s ease;
        margin-bottom: 24px;
        display: flex;
        flex-direction: column;
    }
    .prop-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.08);
        border-color: #CBD5E1;
    }
    .prop-img-container {
        height: 220px;
        width: 100%;
        background-color: #F1F5F9;
        background-size: cover;
        background-position: center;
        position: relative;
    }
    .prop-badge {
        position: absolute;
        top: 16px;
        left: 16px;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(4px);
        padding: 6px 12px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #0F172A;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .prop-content { padding: 24px; }
    .prop-title { font-size: 1.25rem; font-weight: 700; color: #1E293B; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .prop-address { font-size: 0.9rem; color: #64748B; margin-bottom: 16px; display: flex; align-items: center; gap: 4px;}
    .prop-features { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
    .feat-item { font-size: 0.85rem; font-weight: 600; color: #475569; background: #F8FAFC; padding: 6px 10px; border-radius: 8px; border: 1px solid #E2E8F0;}
    .prop-footer { display: flex; justify-content: space-between; align-items: flex-end; border-top: 1px solid #F1F5F9; padding-top: 16px; margin-top: auto;}
    .prop-price-label { font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;}
    .prop-price { font-size: 1.5rem; font-weight: 800; color: #2563EB; line-height: 1.2;}
    .prop-m2 { font-size: 0.9rem; font-weight: 600; color: #10B981;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNÇÕES AUXILIARES (IMAGENS BASE64)
# ==========================================
def image_to_base64(img):
    """Converte imagem do upload para renderizar no HTML/CSS"""
    buffered = BytesIO()
    # Converte RGBA para RGB se necessário (previne erro em JPEGs)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img.save(buffered, format="JPEG", quality=80)
    return base64.b64encode(buffered.getvalue()).decode()

# Imagem padrão caso o imóvel não tenha foto
DEFAULT_IMG = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"

# ==========================================
# 3. BASE DE DADOS VIRTUAL
# ==========================================
if "imoveis" not in st.session_state:
    st.session_state.imoveis = [
        {
            "id": 1, "titulo": "Ed. Território do Rio Branco", "bairro": "Pituba",
            "area_m2": 103, "quartos": 3, "suites": 1, "vagas": 2, "posicao": "Nascente",
            "valor": 950000.0, "condominio": 753.0, "iptu_mes": 420.0,
            "lat": -13.0035, "lon": -38.4612, "fotos_b64": []
        },
        {
            "id": 2, "titulo": "Jardim de Giverny", "bairro": "Pituba",
            "area_m2": 104, "quartos": 3, "suites": 1, "vagas": 2, "posicao": "Nascente",
            "valor": 1050000.0, "condominio": 600.0, "iptu_mes": 449.0,
            "lat": -13.0041, "lon": -38.4608, "fotos_b64": []
        }
    ]

df = pd.DataFrame(st.session_state.imoveis)
if not df.empty:
    df["Custo_m2"] = df["valor"] / df["area_m2"]
    df["Custo_Fixo"] = df["condominio"] + df["iptu_mes"]

# ==========================================
# 4. CABEÇALHO DA PÁGINA
# ==========================================
st.markdown('<div class="gradient-text">Radar Imobiliário</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Prospecção inteligente, análise espacial e portfólio visual.</div>', unsafe_allow_html=True)

# ==========================================
# 5. ABAS MODERNAS
# ==========================================
tab_dash, tab_galeria, tab_cad = st.tabs(["📊 Dashboard & Mapa", "🖼️ Galeria de Imóveis", "✨ Novo Cadastro"])

# ------------------------------------------
# ABA 1: DASHBOARD
# ------------------------------------------
with tab_dash:
    if df.empty:
        st.info("Cadastre seu primeiro imóvel na aba 'Novo Cadastro'.")
    else:
        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-glass"><div class="m-title">Total Analisado</div><div class="m-value">{len(df)}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-glass"><div class="m-title">Preço Médio / m²</div><div class="m-value">R$ {df["Custo_m2"].mean():,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-glass"><div class="m-title">Melhor Preço / m²</div><div class="m-value m-highlight">R$ {df["Custo_m2"].min():,.0f}</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-glass"><div class="m-title">Custo Fixo Médio</div><div class="m-value">R$ {df["Custo_Fixo"].mean():,.0f}</div></div>', unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        
        col_map, col_list = st.columns([2, 1.2])
        with col_map:
            st.markdown("### 📍 Inteligência Espacial")
            # Mapa estendido e limpo
            m = folium.Map(location=[-13.002, -38.462], zoom_start=15, tiles="CartoDB positron")
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=9,
                    color="#2563EB", fill=True, fill_opacity=0.9,
                    tooltip=f"<b>{row['titulo']}</b><br>R$ {row['valor']:,.0f}",
                ).add_to(m)
            st_folium(m, width="100%", height=500, returned_objects=[])

        with col_list:
            st.markdown("### 🏆 Top Oportunidades")
            df_rank = df.sort_values(by="Custo_m2").head(5)
            for _, r in df_rank.iterrows():
                st.markdown(f"""
                <div style="background: white; padding: 16px; border-radius: 16px; margin-bottom: 12px; border: 1px solid #E2E8F0; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-weight: 700; color: #0F172A;">{r['titulo']}</div>
                        <div style="font-size: 0.85rem; color: #64748B;">{r['area_m2']} m² • {r['quartos']} Quartos</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 800; color: #10B981;">R$ {r['Custo_m2']:,.0f}/m²</div>
                        <div style="font-size: 0.8rem; color: #64748B;">R$ {r['valor']:,.0f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ------------------------------------------
# ABA 2: GALERIA DE IMÓVEIS (STYLE AIRBNB)
# ------------------------------------------
with tab_galeria:
    if not st.session_state.imoveis:
        st.warning("Nenhum imóvel cadastrado ainda.")
    else:
        # Cria um grid de 3 colunas
        cols = st.columns(3)
        for idx, imovel in enumerate(st.session_state.imoveis):
            custo_m2 = imovel['valor'] / imovel['area_m2']
            
            # Se tiver foto em base64, usa a primeira, senão usa imagem padrão
            bg_image = f"data:image/jpeg;base64,{imovel['fotos_b64'][0]}" if imovel.get('fotos_b64') else DEFAULT_IMG
            
            html_card = f"""
            <div class="prop-card">
                <div class="prop-img-container" style="background-image: url('{bg_image}');">
                    <div class="prop-badge">☀️ {imovel['posicao']}</div>
                </div>
                <div class="prop-content">
                    <div class="prop-title">{imovel['titulo']}</div>
                    <div class="prop-address">📍 {imovel['bairro']}, Salvador</div>
                    
                    <div class="prop-features">
                        <span class="feat-item">📐 {imovel['area_m2']} m²</span>
                        <span class="feat-item">🛌 {imovel['quartos']} Qtos</span>
                        <span class="feat-item">🚗 {imovel['vagas']} Vagas</span>
                    </div>
                    
                    <div class="prop-footer">
                        <div>
                            <div class="prop-price-label">Valor de Venda</div>
                            <div class="prop-price">R$ {imovel['valor']:,.0f}</div>
                        </div>
                        <div class="prop-m2">R$ {custo_m2:,.0f}/m²</div>
                    </div>
                </div>
            </div>
            """
            # Renderiza no grid
            with cols[idx % 3]:
                st.markdown(html_card, unsafe_allow_html=True)

# ------------------------------------------
# ABA 3: NOVO CADASTRO
# ------------------------------------------
with tab_cad:
    st.markdown("### Adicionar ao Portfólio")
    st.write("Preencha os dados e faça o upload das fotos reais do apartamento.")
    
    with st.form("form_ultra", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            titulo = st.text_input("Nome do Edifício / Identificação")
            bairro = st.selectbox("Bairro", ["Pituba", "Itaigara", "Graça", "Horto Florestal"])
            posicao = st.selectbox("Posição Solar", ["Nascente", "Poente", "Norte", "Sul"])
        with col2:
            valor = st.number_input("Valor Pedido (R$)", value=950000)
            area = st.number_input("Área Útil (m²)", value=100)
            vagas = st.number_input("Vagas", value=2)
        with col3:
            cond = st.number_input("Condomínio Mensal (R$)", value=800)
            iptu = st.number_input("IPTU Mensal (R$)", value=350)
            quartos = st.number_input("Quartos", value=3)
            
        st.markdown("#### 📸 Fotos do Imóvel")
        fotos_upload = st.file_uploader("Arraste as imagens (JPG, PNG)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        
        st.write("")
        submit = st.form_submit_button("✨ Salvar Imóvel no Portfólio", use_container_width=True)
        
        if submit and titulo:
            fotos_b64_list = []
            if fotos_upload:
                for img_file in fotos_upload:
                    img_pil = Image.open(img_file)
                    fotos_b64_list.append(image_to_base64(img_pil))
                    
            novo = {
                "id": len(st.session_state.imoveis) + 1,
                "titulo": titulo, "bairro": bairro, "area_m2": area,
                "quartos": quartos, "suites": 1, "vagas": vagas, "posicao": posicao,
                "valor": float(valor), "condominio": float(cond), "iptu_mes": float(iptu),
                "lat": -13.0030 + (len(st.session_state.imoveis) * 0.0015), 
                "lon": -38.4610 + (len(st.session_state.imoveis) * 0.0015),
                "fotos_b64": fotos_b64_list
            }
            st.session_state.imoveis.append(novo)
            st.success("Imóvel cadastrado! Verifique a aba 'Galeria de Imóveis'.")
            st.rerun()
