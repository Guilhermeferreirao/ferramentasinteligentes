import streamlit as st

st.set_page_config(
    page_title="Obras Inteligentes - Hub",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Obras Inteligentes - Plataforma Integrada")
st.markdown("Bem-vindo ao seu ecossistema central de gestão imobiliária, financeira e de obras.")

st.info("💡 **Dica de Navegação:** Utilize o menu na barra lateral à esquerda para alternar entre os módulos da plataforma.")

# Cards dos Módulos
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🏢 Radar Imobiliário")
    st.write("Catalogação inteligente de apartamentos, mapa de oportunidades, custo por m² e índices de segurança.")
    st.caption("Acesse pelo menu lateral: **1 Apartamentos**")

with col2:
    st.subheader("💰 Controle de Gastos")
    st.write("Gestão de custos de aquisição (ITIV, cartório), fluxo de caixa, entrada e despesas correntes.")
    st.caption("Acesse pelo menu lateral: **2 Controle de Gastos**")

with col3:
    st.subheader("🔨 Gestão de Obras")
    st.write("Planejamento de reforma, cronograma de execução, etapas de obra e checklist de compras de materiais.")
    st.caption("Acesse pelo menu lateral: **3 Gestao de Obras**")

st.divider()
st.caption("Plataforma Obras Inteligentes • Salvador - BA")
