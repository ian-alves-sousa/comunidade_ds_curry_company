#Bibiliotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium
import numpy as np

st.set_page_config(
    page_title='Visão Restaurantes', layout='wide')

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



def distance(df1):
    """Funcão que calcula a distância média entre os restaurantes e os locais de entrega."""
    cols = ['Restaurant_latitude',
           'Restaurant_longitude', 'Delivery_location_latitude',
           'Delivery_location_longitude']

    df1['distance'] = df1.loc[:,cols].apply(lambda x:
                        haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
    distancia_media = round(df1['distance'].mean(),2)
                
    return distancia_media
            
            
        
def time_op(df1,festival,op):
    """
                #6. O tempo médio de entrega durantes os Festivais.
                
                Esta função calcula o Tempo Médio e Desvio Padrão do tempo de entrega.
                Parâmetros:
                    df1: DataFrame com os dados
                    festival: Filtra caso as entregas tenham sito feitas no festival ou não
                        'No': Não foram feitas durante o festival
                        'Yes': Foram feitas durante o festival
                    op: Tipo de operação que precisa ser calculada
                        'Tempo Médio': Calcula o Tempo Médio
                        'Desvio Padrão': Calcula o Desvio Padrão
                    
                Saída: DataFrame com duas colunas e uma linha
    """
    re6 = round(df1.loc[:,['Festival','Time_taken(min)']].groupby(['Festival']).agg(['mean','std']).reset_index(),2)
    re6.columns = ['Festival','Tempo Médio','Desvio Padrão']
    re6 = re6.loc[(re6['Festival'] == festival),op]
                
    return re6





def chart_bar(df1):
    """#3. O tempo médio e o desvio padrão de entrega por cidade."""
    re3 = df1.loc[:,['City','Time_taken(min)']].groupby(['City']).agg(['mean','std']).reset_index()
    re3.columns = ['City','Tempo Médio','Desvio Padrão']

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Controle',
                        x=re3['City'],
                        y=re3['Tempo Médio'],
                        error_y=dict(type='data', array=re3['Desvio Padrão'])))
    fig.update_layout(barmode='group')
                
    return fig
            
    
    
    
    
def pie_chart(df1):
    """Função para criar o gráfico de pizza"""
    cols = ['Restaurant_latitude',
           'Restaurant_longitude', 'Delivery_location_latitude',
           'Delivery_location_longitude']

    df1['distance'] = df1.loc[:,cols].apply(lambda x:
                            haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
    distancia_media = round(df1['distance'].mean(),2)
    frame_distance = df1.loc[:,['distance','City']].groupby(['City']).mean().reset_index()
    fig = go.Figure(data=go.Pie(labels=frame_distance['City'],values=frame_distance['distance'],pull=[0,0.1,0]))
                
    return fig


def sunburst_chart(df1):
    """#5. O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego."""
    re5 = df1.loc[:,['City','Time_taken(min)','Road_traffic_density']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']}).reset_index()
    re5.columns = ['City','Road_traffic_density','Tempo Médio','Desvio Padrão']

    fig = px.sunburst(re5,path=['City','Road_traffic_density'],values='Tempo Médio',
                                 color='Desvio Padrão',color_continuous_scale='RdBu',
                                 color_continuous_midpoint=np.average(re5['Desvio Padrão']))
                
    return fig



# --------------------- Início da Estrutura Lógica do Código ---------------

# ===========================================================================
#Importar os dados
#==========================================================================
df = pd.read_csv('../dataset/train.csv')
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
st.header('Marketplace - Visão Retaurantes')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    #Container 1
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            #1. A quantidade de entregadores únicos.
            qtde = len(df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregador',qtde)
        
            
        with col2:
            distancia_media = distance(df1)
            col2.metric('Distância média',distancia_media)
            
        with col3:
            re6 = time_op(df1,'Yes','Tempo Médio')
            col3.metric('Tempo Médio',re6)
                          
        with col4:         
            re6 = time_op(df1,'Yes','Desvio Padrão')
            col4.metric('STD da Entrega',re6)
            
        with col5:
            re6 = time_op(df1,'No','Tempo Médio')
            col5.metric('Tempo Médio',re6)
            
        with col6:
            re6 = time_op(df1,'No','Desvio Padrão')
            col6.metric('STD da Entrega',re6)
            
        
        
        
        
        
    #Container 2    
    with st.container():
        st.markdown("""---""")
        st.title('Distruibuição do Tempo')
        col1, col2 = st.columns(2)
        
        with col1:
            fig = chart_bar(df1)
            st.plotly_chart(fig,use_container_width=True)
            
        with col2:
            #4. O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.
            re4 = df1.loc[:,['City','Time_taken(min)','Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']}).reset_index()
            re4.columns = ['City','Type_of_order','Tempo Médio','Desvio Padrão']
            st.dataframe(re4)
            

    
    
    
    
    
    #Container 3
    with st.container():
        st.markdown("""---""")
        st.title('Distruibuição do Tempo')
        col1, col2 = st.columns(2)
        with col1:
            fig = pie_chart(df1)
            st.plotly_chart(fig,use_container_width=True)
            
            
        with col2:
            fig = sunburst_chart(df1)
            st.plotly_chart(fig,use_container_width=True)
        
        