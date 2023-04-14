import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home')



image_path = 'logo.jpg'
image = Image.open(image_path)
st.sidebar.image(image,width=250)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Delivery mais rápido da cidade')
st.sidebar.markdown("""---""")

st.write('# Dashboard de crescimento da Cury Company')
st.markdown(
    """
        Este Dashboard foi construido para acompanhar as métricas de crecimento dos Entregadores e Restaurantes.
        ### Como utilizar esse Dashboard?
        
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamento.
            - Visão Tática: Indicadores semanais de crescimento.
            - Visão Geográfica: Insights de geolocalização.
        - Visão Entregador:
            - Acompanhamento dos indicadores semanais de crescimento.
        - Visão Restaurante:
            - Indicadores semanais de crescimento dos restaurantes
        ### Ask for Help
        - Comunidade DS
            - iansous@gmail.com

""")
