#==============================================
# Libraries
#==============================================
import pandas as pd
import plotly.express as px 
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
from datetime import datetime

#==============================================
# Funções
#==============================================

# Função para limpar o dataframe:
def clean_code(df):
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
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    # Resetando o index:
    df = df.reset_index(drop = True)
    
    return df

# Função para obter os 10 entregadores mais lentos ou mais rápidos da cidade:
def top_delivers(df, top_asc):
    """ Essa função calcula os 10 entregadores mais lentos ou mais rápidos por cidade.
        Ela utiliza as colunas Delivery_person_ID, City e Time_taken(min), agrupando por City e Delivery_person_ID e ordenando Time_taken(min) com respeito
        à City. O parâmetro top_asc deve ser definido como True ou False, a depender do tipo de ordenação desejada (ascendente ou descendente).
        É feita uma seleção das 10 primeiras linhas por tipo de cidade e uma junção disso num novo dataframe.
        Essa função não exibe o dataframe, é preciso um comando separado para isso.
        
        Input: Dataframe
        Output: Dataframe
    """
    #  Os 10 entregadores mais lentos ou mais rápidos por cidade
    df_aux1 = (df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                 .groupby(['City', 'Delivery_person_ID'])
                 .mean()
                 .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
                 .reset_index())

    df_aux2 = df_aux1.loc[df_aux1['City'] == 'Metropolitian',:].head(10)
    df_aux3 = df_aux1.loc[df_aux1['City'] == 'Urban',:].head(10)
    df_aux4 = df_aux1.loc[df_aux1['City'] == 'Semi-Urban',:].head(10)

    df_aux5 = pd.concat([df_aux2, df_aux3, df_aux4]).reset_index(drop=True)    

    return df_aux5
                                
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
st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

#==============================================
# Barra Lateral
#==============================================
st.markdown('# Marketplace - Visão Entregadores')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.markdown('## Overall metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        
        with col1:
            
            # A maior idade dos entregadores:
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            
            col1.metric('Maior idade', maior_idade)
        
        with col2:
            
             # A menor idade dos entregadores:            
            menor_idade = df.loc[:, 'Delivery_person_Age'].min() # Poderia fazer também sort_values
            
            col2.metric('Menor idade', menor_idade)
        
        with col3:
           
            # A melhor condição de veículos:
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
            
            col3.metric('Melhor condição', melhor_condicao)
            
            
        with col4:
           
            # A pior condição de veículos:
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            
            col4.metric('Pior condição', pior_condicao)
            
    with st.container():
        st.markdown("""____""")
        st.markdown('## Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação média por entregador')
            
            # A avaliação média por entregador:
            df_avg_rating_by_deliver = (df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index())
            st.dataframe(df_avg_rating_by_deliver, use_container_width=True)
            
        with col2:
            st.markdown( '##### Avaliação média por trânsito' )
            
            # A avaliação média e o desvio padrão por tipo de tráfego
            df_avg_std_rating_by_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                              .groupby('Road_traffic_density')
                                              .agg({'Delivery_person_Ratings': ['mean','std']})) 

            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()

            st.dataframe(df_avg_std_rating_by_traffic, use_container_width=True)
            
            st.markdown('##### Avaliação média por clima')
            
            # A avaliação média e o desvio padrão por condições climáticas
            df_avg_std_rating_by_weather = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                              .groupby('Weatherconditions')
                                              .agg({'Delivery_person_Ratings': ['mean','std']})) 

            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()

            st.dataframe(df_avg_std_rating_by_weather, use_container_width=True)
            
        with st.container():
            st.markdown("""____""")
            st.markdown('## Velocidade de entrega')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('##### Top entregadores mais rápidos')
                
                # Os 10 entregadores mais rápidos por cidade
                
                df_aux5 = top_delivers(df, top_asc=True)
                
                st.dataframe(df_aux5, use_container_width=True)
                
            with col2:
                st.markdown('##### Top entregadores mais lentos')
                
                # Os 10 entregadores mais lentos por cidade
                
                df_aux5 = top_delivers(df, top_asc=False)      
                
                st.dataframe(df_aux5, use_container_width=True)