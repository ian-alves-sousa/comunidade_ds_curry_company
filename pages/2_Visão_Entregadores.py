#Bibiliotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium

st.set_page_config(
    page_title='Visão Entregadores', layout='wide')

# ===========================================================================
#Funções
#==========================================================================

def clean_code(df1):
    """Função para limpar o DataFrame
    Tipos de Limpaza:
    1 - Remo~]ao dos dados NaN
    2 - Mudança do tipo de coluna de dados
    3 - Remoção dos espaços das variáveis de texto
    4 - Formatação da coluna de datas
    5 - Limpeza da coluna de tempo, remoção do texto
    
    Entreda: DataFrame
    Saída: DataFrame"""
    #Convertendo a coluna Age de texto para número
    df1 = df1.loc[(df['Delivery_person_Age'] != 'NaN '),:].copy()
    df1 = df1.loc[(df['Road_traffic_density'] != 'NaN '),:].copy()
    df1 = df1.loc[(df['City'] != 'NaN '),:].copy()
    df1 = df1.loc[(df['Festival'] != 'NaN '),:].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #Convertendo a coluna Rating de texto para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #Convertendo a coluna Order Date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'],format='%d-%m-%Y')

    #Convertendo multiple_deliveries de texto para int
    df1 = df1.loc[(df['multiple_deliveries'] != 'NaN '),:].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #Removendo os espaços dentro de strings
    #df1 = df1.reset_index(drop=True)
    #for i in range(df1.shape[0]):
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()

    #Limpando o Time_taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x : x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1


def delivers_slow(df1):
    #7. Os 10 entregadores mais lentos por cidade.
    re7 = df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']].groupby(['City','Delivery_person_ID']).max().sort_values(['City','Time_taken(min)'],ascending=False).reset_index()
    re7_1 = re7.loc[(re7['City'] == 'Metropolitian'),:].head(10)
    re7_2 = re7.loc[(re7['City'] == 'Semi-Urban'),:].head(10)
    re7_3 = re7.loc[(re7['City'] == 'Urban'),:].head(10)

    re7 = pd.concat([re7_1,re7_2,re7_3]).reset_index(drop=True)
                
    return re7



def delivers_fast(df1):
    re6 = df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']].groupby(['City','Delivery_person_ID']).min().sort_values(['City','Time_taken(min)']).reset_index()
    re6_1 = re6.loc[(re6['City'] == 'Metropolitian'),:].head(10)
    re6_2 = re6.loc[(re6['City'] == 'Semi-Urban'),:].head(10)
    re6_3 = re6.loc[(re6['City'] == 'Urban'),:].head(10)

    re6 = pd.concat([re6_1,re6_2,re6_3]).reset_index(drop=True)
    
    return re6
            
            
            
            

# --------------------- Início da Estrutura Lógica do Código ---------------

# ===========================================================================
#Importar os dados
#==========================================================================
df = pd.read_csv('dataset/train.csv')
df1 = df.copy()

# ===========================================================================
#Limpando os dados
#==========================================================================
df1 = clean_code(df1)




# ===========================================================================
#Barra lateral
#==========================================================================
path = 'logo.jpg'
image = Image.open(path)
st.sidebar.image(image,width=250)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Delivery mais rápido da cidade')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider('Até qual data?',
                 value=pd.datetime(2022,4,13),
                 min_value=pd.datetime(2022,2,11),
                 max_value=pd.datetime(2022,4,6),
                 format='DD-MM-YYYY')

st.sidebar.markdown("""---""")



traffic_op = st.sidebar.multiselect('Quais as condições do transito',
                      ['Low','Medium','High','Jam'],
                      default=['Low','Medium','High','Jam'])

clima_op = st.sidebar.multiselect('Quais as condições climáticas',
                      ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
                      default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powerd By Comunidade DS')

#Ligar os dados ao filtro de barra, onde a data irá se adequar ai intervalo definido do data_slider
#Filtro de data
df1 = df1.loc[df1['Order_Date'] < data_slider,:]

#Filtro de trânsito
df1 = df1.loc[df1['Road_traffic_density'].isin(traffic_op),:]

#Filtro de Clima
df1 = df1.loc[df1['Weatherconditions'].isin(clima_op),:]
#st.dataframe(df1)

# ===========================================================================
#Layout no Streamlit
#==========================================================================
st.header('Marketplace - Visão Entregadores')
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    with st.container(): #Define o container do tab1
        #1. Quantidade de pedidos por dia.
        st.markdown('# Métricas Gerais')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1: #1. A menor e maior idade dos entregadores.
            velho = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade',velho)

        with col2:
            novo = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade',novo)
            
        with col3:#2. A pior e a melhor condição de veículos.
            melhor = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição',melhor)
            
        with col4:
            pior = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição',pior)
            
            
            
    with st.container(): #Segundo container
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            #3. A avaliação média por entregador.
            media_entr = round(df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby(['Delivery_person_ID']).mean().reset_index(),2)
            media_entr.columns = ['ID do Entregador','Avaliação']
            st.dataframe(media_entr)

            
        with col2:
            st.markdown('##### Avaliação média por Trânsito')
            #4. A avaliação média e o desvio padrão por tipo de tráfego.
            re4 = round(df1.loc[:,['Road_traffic_density','Delivery_person_Ratings']].groupby(['Road_traffic_density']).agg(['mean','std']).reset_index(),2)
            re4.columns = ['Densidade de Tráfico','Média','Desvio Padrão']
            st.dataframe(re4)
            
            
            st.markdown('##### Avaliação média por Clima')
            #5. A avaliação média e o desvio padrão por condições climáticas.
            re5 = round(df1.loc[:,['Weatherconditions','Delivery_person_Ratings']].groupby(['Weatherconditions']).agg(['mean','std']).reset_index(),2)
            re5.columns = ['Condições do Clima','Média','Desvio Padrão']
            st.dataframe(re5)
            
            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            #6. Os 10 entregadores mais rápidos por cidade.
            re6 = delivers_fast(df1)
            st.dataframe(re6)
            
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            re7 = delivers_slow(df1)
            st.dataframe(re7)