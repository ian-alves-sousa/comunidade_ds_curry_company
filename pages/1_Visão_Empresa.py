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
    page_title='Visão Empresa', layout='wide')

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

def order_metric(df1):
    """#1. Quantidade de pedidos por dia."""
    re1 = df1.loc[:,['ID','Order_Date']].groupby(['Order_Date']).count().reset_index()
    #Desenhar gráfico de linhas
    fig1 = px.bar(re1, x='Order_Date',y='ID')
            
    return fig1



def traffic_order_share(df1):
    """#3. Distribuição dos pedidos por tipo de tráfego."""
    re3 = df1.loc[:,['ID','Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
    re3 = re3.loc[(re3['Road_traffic_density'] != 'NaN'),:]
    re3['perc_entregas'] = re3['ID'] / re3['ID'].sum()
    fig2 = px.pie(re3,values='perc_entregas',names='Road_traffic_density')
                    
    return fig2

    
    
def traffic_order_city(df1):
    """#4. Comparação do volume de pedidos por cidade e tipo de tráfego."""
    re4 = df1.loc[:,['ID','Road_traffic_density','City']].groupby(['City','Road_traffic_density']).count().reset_index()
    re4 = re4.loc[(re4['Road_traffic_density'] != 'NaN'),:]
    re4 = re4.loc[(re4['City'] != 'NaN'),:]

    #Gráfico de bolhas, onde o size demonstra o tamanho da bolha
    fig3 = px.scatter(re4,x='City',y='Road_traffic_density',size='ID')
    return fig3    
    
    
    
def order_by_week(df1):
    """#2. Quantidade de pedidos por semana."""
    #Criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    re2 = df1.loc[:,['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()

    #Gráfico de linhas
    fig4 = px.line(re2,x='week_of_year',y='ID')
            
    return fig4



def order_share_by_week(df1):
    """#5. A quantidade de pedidos por entregador por semana."""
    re5_1 = df1.loc[:,['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
    re5_2 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby(['week_of_year']).nunique().reset_index()
    re5 = pd.merge(re5_1,re5_2,how='inner')
    re5['order_deliver'] = re5['ID'] / re5['Delivery_person_ID']

    #Gráfico de linhas
    fig5 = px.line(re5,x='week_of_year',y='order_deliver')
            
    return fig5


    
def country_maps(df1):
    """#6. A localização central de cada cidade por tipo de tráfego."""
    re6 = df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    re6 = re6.loc[(re6['Road_traffic_density'] != 'NaN'),:]
    re6 = re6.loc[(re6['City'] != 'NaN'),:]


    map = folium.Map()
    for index,location in re6.iterrows():
        folium.Marker([location['Delivery_location_latitude'],location['Delivery_location_longitude']],
                    popup=location[['City','Road_traffic_density']]).add_to(map)

    folium_static(map,width=1024,height=600)

    
    
    
# --------------------- Início da Estrutura Lógica do Código ---------------

# ===========================================================================
#Importar os dados
#==========================================================================
df = pd.read_csv('/dataset/train.csv')
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

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powerd By Comunidade DS')

#Ligar os dados ao filtro de barra, onde a data irá se adequar ai intervalo definido do data_slider
#Filtro de data
df1 = df1.loc[df1['Order_Date'] < data_slider,:]

#Filtro de trânsito
df1 = df1.loc[df1['Road_traffic_density'].isin(traffic_op),:]
#st.dataframe(df1)

# ===========================================================================
#Layout no Streamlit
#==========================================================================
st.header('Marketplace - Visão Cliente')
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

#TAB 1
with tab1:
    with st.container(): #Define o container do tab1
        st.markdown('# Ordens por dia')
        fig1 = order_metric(df1)
        st.plotly_chart(fig1,use_container_width=True)
        
        with st.container(): #Define o container das colunas que terão duas infos
            col1, col2 = st.columns(2)
            with col1:
                st.header('Pedidos por tráfico')
                fig2 = traffic_order_share(df1)
                st.plotly_chart(fig2,use_container_width=True)

                
            with col2:
                st.header('Pedidos por Tráfico e Cidade')
                fig3 = traffic_order_city(df1)
                st.plotly_chart(fig3,use_container_width=True)


            
#TAB 2
with tab2:
    with st.container():
        st.markdown('# Pedidos por Semana')
        fig4 = order_by_week(df1)
        st.plotly_chart(fig4,use_container_width=True)
        
        
    with st.container():
        st.markdown('# Pedidos por entregador por Semana')
        fig5 = order_share_by_week(df1) 
        st.plotly_chart(fig5,use_container_width=True)
        

#TAB 3    
with tab3:
    st.markdown('# Localização das cidades')
    country_maps(df1)
    












#print('Estou aqui')