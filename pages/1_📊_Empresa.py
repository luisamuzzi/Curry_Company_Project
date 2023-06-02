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
    df = df.reset_index(drop=True)
    
    return df

# Função para gerar um gráfico de entregas por dia:
def order_metric(df):  
    """ Essa função tem a responsabilidade de gerar um gráfico de barras do número de entregas (y) por dia (x).
        Utiliza as colunas ID e Order_Date do dataframe, agrupando por Order_Date e fazendo a contagem de ID.
        A função não exibe o gráfico na tela, isso precisa ser feito por um comando separado.
        
        Input: df
        Output: fig (o gráfico gerado)
    """
    df_aux = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()

    fig = px.bar(df_aux, x='Order_Date', y='ID', labels={'Order_Date': 'Dia',
                                                  'ID': 'Quantidade de pedidos'})

    return fig

# Função para gerar um gráfico dos pedidos por tipo de tráfego:    
def traffic_order_share(df):
    """ Essa função tem a responsabilidade de gerar um gráfico de pizza dos tipos de pedido por tipo de tráfego.
        Utiliza as colunas ID e Road_traffic_density do dataframe, agrupando por Road_traffic_densit e fazendo a contagem de ID.
        A função não exibe o gráfico na tela, isso precisa ser feito por um comando separado.
        
        Input: df
        Output: fig (o gráfico gerado)
    """
    df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

    df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()

    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

# Função para gerar um gráfico comparando o número de pedidos por cidade e tipo de tráfego:
def traffic_order_city(df): 
    """ Essa função tem a responsabilidade de gerar um gráfico de pontos (scatter) comparando o número de pedidos por cidade e tipo de tráfego.
        Utiliza as colunas ID, City e Road_traffic_density do dataframe, agrupando por City e Road_traffic_densit e fazendo a contagem de ID.
        A função não exibe o gráfico na tela, isso precisa ser feito por um comando separado.
        
        Input: df
        Output: fig (o gráfico gerado)
    """
    df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()

    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City', labels={'City': 'Cidade',
                                                  'Road_traffic_density': 'Densidade de tráfego'})

    return fig

# Função para gerar um gráfico da quantidade de pedidos por semana:
def order_by_week(df):   
    """ Essa função tem a responsabilidade de gerar um gráfico de linha com o número de pedidos (y) por semana do ano (x).
        Cria a coluna week_of_year a partir da coluna Order_Date.
        Utiliza as colunas ID e week_of_year(), agrupando por week_of_year e fazendo a contagem de ID.
        A função não exibe o gráfico na tela, isso precisa ser feito por um comando separado.
        
        Input: df
        Output: fig (o gráfico gerado)
    """   
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')

    df_aux = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    fig = px.line(df_aux, x='week_of_year', y='ID', labels={'week_of_year': 'Semana do ano',
                                                  'ID': 'Quantidade de pedidos'})

    return fig
    
# Função para gerar um gráfico da quantidade de pedidos por entregador por semana:
def order_share_by_week(df):
    """ Essa função tem a responsabilidade de gerar um gráfico de linha com o número de pedidos por entregador (y) por semana do ano (x).
        Utiliza as colunas ID e week_of_year(), agrupando por week_of_year e fazendo a contagem de ID.
        Utiliza as colunas Delivery_person_Id e week of year, agrupando por week_of_year e obtendo o número de valores únicos de Delivery_person_ID.
        Realiza a junção das duas tabelas obtidas.
        Cria a culuna order_by_deliver, que consiste na divisão das colunas ID por 'Delivery_person_ID obtidas dos agrupamentos e cálculos anteriores.
        A função não exibe o gráfico na tela, isso precisa ser feito por um comando separado.
        
        Input: df
        Output: fig (o gráfico gerado)
    """  
    df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge(df_aux1, df_aux2, how='inner')

    df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver', labels={'week_of_year': 'Semana do ano',
                                                  'order_by_deliver': 'Pedidos por entregador'})

    return fig

# Função para gerar e exibir um mapa com a localização central de cada cidade por tipo de tráfego:
def country_maps(df):   
    """ Essa função tem a responsabilidade de gerar um mapa com as marcações da localização central de cada cidade por tipo de tráfego.
        Utiliza as colunas Delivery_location_latitude, Delivery_location_longitude, City e Road_traffic_density, agrupadas por City e Road_traffic_density,
        e a média das colunas de latitude/longitude.
        Gera um mapa mundial.
        Adiciona marcadores no mapa que correspondem às localizações médias obtidas nos passos anteriores.
        Exibe o mapa na tela.
        
        Input: df
        Output: Não tem return.
    """       
    df_aux = (df.loc[:, ['Delivery_location_latitude', 'Delivery_location_longitude', 'City', 'Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .median()
                .reset_index())

    map = folium.Map()

    for index, location_info in df_aux.iterrows(): 
        
        popup = folium.Popup(f""" City: {location_info['City']}<br>
        Densidade de tráfego: {location_info['Road_traffic_density']}
        """,
        max_width=500,
        )
        
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=popup).add_to(map)

    folium_static( map, width=1024, height=600 )

    return None
    
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
st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')

#==============================================
# Barra Lateral
#==============================================
st.markdown('# Marketplace - Visão Cliente')

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider('Até qual valor?',
                                value = datetime(2022, 4, 13),
                                min_value = datetime(2022, 2, 11),
                                max_value = datetime(2022, 4, 6),
                                format = 'DD-MM-YYYY')

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
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas, :]

#==============================================
# Layout no streamlit
#==============================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
    
        st.markdown('## Orders by day')
        
        # Quantidade de pedidos por dia
        fig = order_metric(df)

        st.plotly_chart(fig, use_container_width=True)
    
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('## Orders by traffic condition')
            
            # Distribuição dos pedidos por tipo de tráfego
            fig = traffic_order_share(df)
            
            st.plotly_chart(fig, use_container_width=True)
            
        
        with col2:
            st.markdown('## Orders by city and traffic condition')
            
            # Comparação do volume de pedidos por cidade e tipo de tráfego
            fig = traffic_order_city(df)
            
            st.plotly_chart(fig, use_container_width=True)
    
    
with tab2:
    with st.container():
        st.markdown('## Orders by week')
        
        # Quantidade de pedidos por semana
        fig = order_by_week(df)
        
        st.plotly_chart(fig, use_container_width=True)
              
        
    with st.container():
        st.markdown('## Orders by delivery person by week')
        
        # A quantidade de pedidos por entregador por semana
        fig = order_share_by_week(df)
        
        st.plotly_chart(fig, use_container_width=True)
        
           
with tab3:
    st.markdown('## Central location of cities by traffic condition')
    
    # A localização central de cada cidade por tipo de tráfego
    country_maps(df) 