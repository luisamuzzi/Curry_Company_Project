#==============================================
# Libraries
#==============================================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import numpy as np
from datetime import datetime

#==============================================
# Funções
#==============================================

# Função para limpar o dataframe:
def clean_code( df ):
    """ Essa função tem a responsabilidade de limpar o dataframe.
    
        Tipos de limpeza:
        1. Remoção dos NaN
        2. Remoção dos espaços das variáveis de texto
        3. Mudança do tipo da coluna de dados
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        
        Também foi resetado o index.
        
        Imput: Dataframe
        Output: Dataframe    
    """

    # Limpeza dos dados e transformação de variáveis:
    # Eliminando 'NaN ':
    df = df.loc[df['Delivery_person_Ratings'] != 'NaN ', :]
    df = df.loc[df['Weatherconditions'] != 'NaN ', :]
    df = df.loc[df['Road_traffic_density'] != 'NaN ', :]
    df = df.loc[df['multiple_deliveries'] != 'NaN ', :]
    df = df.loc[df['Festival'] != 'NaN ', :]
    df = df.loc[df['City'] != 'NaN ', :]
    df = df.loc[df['Delivery_person_Age'] != 'NaN ', :]

    # Eliminando espaço no final das strings:
    df['City'] = df['City'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip()
    df['Type_of_order'] = df['Type_of_order'].str.strip()
    df['Type_of_vehicle'] = df['Type_of_vehicle'].str.strip()
    df['Festival'] = df['Festival'].str.strip()
    df['City'] = df['City'].str.strip()

    # # Alterando variáveis de objeto para número:
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

    # Alterando variáveis de objeto para data:
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

    # Limpando a coluna Time_taken:
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    # Resetando o index:
    df = df.reset_index(drop=True)
    
    return df

# Função para para calcular e gerar um gráfico da distância média dos resturantes e dos locais de entrega:
def distance(df, fig):
    """ Essa função tem por objetivo calcular a distância média dos resturantes e dos locais de entrega e gerar um gráfico de pizza. Ela utiliza as colunas
        Restaurant_latitude, Restaurant_longitude, Delivery_location_latitude e Delivery_location_longitude para calcular a distância e armazenar numa coluna
        criada chamada distance. Em seguida, a média das distâncias da coluna distance é calculada e o valor arredondado considerando 2 casas decimais.
    
        Input: dataframe
            - fig = True ou False
        Output: float ou gráfico
    """
    if fig == False:
    
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df['distance'] = df.loc[:, cols].apply(lambda x: 
                                   haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                       (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

        avg_distance = np.round(df['distance'].mean(), 2)
        
        return avg_distance
        
    else:

        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df['distance'] = df.loc[:, cols].apply(lambda x: 
                                       haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                           (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

        avg_distance = df.loc[:,['City', 'distance']].groupby('City').mean().reset_index()

        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
    
        return fig

# Função para calcular o tempo médio de entrega durantes os Festivais:
def avg_std_time_delivery(df, festival, op):
    """ 
        Essa função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo.
                - festival: A ocorrência ou não do festival durante as entregas
                    'Yes': ocorreu festival
                    'No': não ocorreu festival.
                - op: Tipo de operação que precisa ser calculada
                    'avg_time': Calcula o  tempo médio
                    'std_time': Calcula o desvio padrão do tempo.
                
            Output:
                - df: Dataframe com 2 colunas e 1 linha
    """


    df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)' : ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux

# Função para gerar um gráfico  do tempo médio e o desvio padrão de entrega por cidade:
def avg_std_time_graph(df):  
    """
        Essa função gera um gráfico de barras com desvio padrão do tempo de entrega por cidade.
        Não exibe o gráfico, é preciso um comando separado para isso.
        
        Input: dataframe
        Output: o gráfico gerado
        
    """   
    df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar( name='Control',
                           x=df_aux['City'],
                           y=df_aux['avg_time'],
                           error_y=dict(type='data', array=df_aux['std_time'])))

    fig.update_layout(barmode='group')

    return fig

# Função para gerar um gráfico do tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego:
def avg_std_time_on_traffic(df):
    """
        Essa função tem por objetivo gerar um gráfico do tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.
        Não exibe o gráfico. É preciso um comando separado para isso.
        
        Input: dataframe
        Output: O gráfico gerado.    
    """
    df_aux = (df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .agg( {'Time_taken(min)': ['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'],
                      values='avg_time', color='std_time',
                      color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']), labels={'std_time': 'Desvio padrão'})

    return fig

# -------------------------------------------- Início da estrutura lógica do código ----------------------------------------------------------------

#==============================================
# Import dataset
#==============================================
df_original = pd.read_csv('dataset/train.csv')

#==============================================
# Limpeza dos dados
#==============================================
df = clean_code(df_original)

#==============================================
# Configuração da largura da página
#==============================================
st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽', layout='wide')

#==============================================
# Barra Lateral
#==============================================
st.markdown('# Marketplace - Visão Restaurantes')

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider('Até qual valor?',
                                value=datetime(2022, 4, 13),
                                min_value=datetime(2022, 2, 11),
                                max_value=datetime(2022, 4, 6),
                                format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito?',
                                        ['Low', 'Medium', 'High', 'Jam'],
                                         default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""___""")

st.sidebar.markdown('### Powered by CDS')

# Filtro de data:
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

# Filtro de trânsito:
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#==============================================
# Layout no streamlit
#==============================================
tab1, tab2, tab3 = st.tabs(['Visão Geral', '_', '_'])

with tab1:
    with st.container():
        st.markdown('## Overall metrics')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            
            # A quantidade de entregadores únicos:
            
            delivery_unique = len(df.loc[:, 'Delivery_person_ID'].unique())
            
            col1.metric('Entregadores únicos', delivery_unique)
            
        with col2:
            
            # A distância média dos resturantes e dos locais de entrega:
            
            avg_distance = distance(df, fig=False)
            
            col2.metric('Distância média das entregas', avg_distance)

        with col3:
                
            # O tempo médio de entrega durantes os Festivais:
            
            df_aux = avg_std_time_delivery(df, festival='Yes', op='avg_time')
            
            col3.metric('Tempo médio de entrega com o festival', df_aux)
        
    with st.container():
        col4, col5, col6 = st.columns(3)
        
        with col4:
            
            # O desvio padrão das entrega durantes os Festivais:
            
            df_aux = avg_std_time_delivery(df, 'Yes', 'std_time')
            
            col4.metric('Desvio padrão das entregas com o festival', df_aux)
        
        with col5:
            
             # O tempo médio de entrega sem os Festivais:
            
            df_aux = avg_std_time_delivery(df, 'No', 'avg_time')
            
            col5.metric('Tempo médio de entrega sem o festival', df_aux)
        
        with col6:
            
            # O desvio padrão das entrega sem os Festivais:
            
            df_aux = avg_std_time_delivery(df, 'No', 'std_time')
            
            col6.metric('Desvio padrão das entregas sem o festival', df_aux)
    
    with st.container():
        st.markdown("""___""")
        st.markdown('## Tempo médio de entrega por cidade')
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            # O tempo médio e o desvio padrão de entrega por cidade:
                
            fig = avg_std_time_graph(df)

            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            
            # O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido:
                
            df_aux = (df.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                        .groupby(['City', 'Type_of_order'])
                        .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['mean_time', 'std_time']

            df_aux = df_aux.reset_index()

            st.dataframe(df_aux, use_container_width=True)
                
    with st.container():
        st.markdown("""___""")
        st.markdown('## Distribuição do tempo')
        
        col1, col2 = st.columns(2)
        
        with col1:

            # A distância média dos resturantes e dos locais de entrega:
            
            fig = distance(df, fig=True)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
                      
             # O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego:
                
            fig = avg_std_time_on_traffic(df)
            
            st.plotly_chart(fig, use_container_width=True)