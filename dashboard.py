# Importando as bibliotecas:
import streamlit as st
import requests
import pandas as pd
import plotly.express as px


# formato da pagina:
st.set_page_config(layout = 'wide', 
                   page_title='DASH - Vendas',
                   page_icon=':shopping_trolley:')

# Salvar em cache:
@st.cache_data

## Funções do Código:
# 01 formata numero:
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# Rodando o aplicativo: (pagina do navegador)
st.title('DASHBOARD DE VENDAS :shopping_trolley::full_moon::flag-ba::peach:')

# Endereco dos repositorio (base de dados) - Buscando os dados e salvando em uma variável: # alteração do tipo de dados da coluna data
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
anos = ['2020', '2021', '2022', '2023']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes) # filtro do exercicio - barra lateral
#regiao = st.pills('Região', regioes) # filtro alternativo dentro da pagina

# se brasil == sem filtros de regioes
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

# se todos os anos == sem filtro para os anos
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023) # filtro do exercicio - barra lateral
    #ano = st.pills('Ano', anos) # filtro alternativo dentro da pagina

query_string = {'regiao':regiao.lower(), 'ano':ano}
response = requests.get(url, params= query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') 

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# configurações diversas:
# Mapeamento de meses em português # Criando o dicionário de mapeamento de inglês para português
meses_traducao = {
    'January': 'janeiro', 'February': 'fevereiro', 'March': 'março', 'April': 'abril',
    'May': 'maio', 'June': 'junho', 'July': 'julho', 'August': 'agosto',
    'September': 'setembro', 'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
}

## Tabelas:
### 01 Tabelas receita:
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Traduzindo os meses para português
receita_mensal['Mês'] = receita_mensal['Mes'].map(meses_traducao)
# Removendo a coluna dos meses em ingles
receita_mensal = receita_mensal.drop(columns=['Mes'])

# tabela base para o grafico - receita categorias - aba 01
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### 02 Tabelas vendas: 
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

# Traduzindo os meses para português
vendas_mensal['Mês'] = vendas_mensal['Mes'].map(meses_traducao)
# Removendo a coluna dos meses em ingles
vendas_mensal = vendas_mensal.drop(columns=['Mes'])

# tabela base para o grafico - vendas categorias - aba 02
vendas_categorias = dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False)


### 03 Tabelas vendedores:

# tabela base para o grafico - vendedores - aba 03
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


## Gráficos
### 01 Graficos de Receita:
fig_mapa_receita = px.scatter_geo(receita_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color='Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 Estados em Receitas')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por Categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

### 02 Graficos de Vendas:
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Vendas por Estado')

fig_vendas_mensal = px.line(vendas_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, vendas_mensal.max()),
                             color='Ano',
                             line_dash = 'Ano',
                             title = 'Quant. de Vendas Mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados')
fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                                text_auto = True,
                                title = 'Vendas por Categoria')
fig_vendas_categorias.update_layout(yaxis_title = 'Quantidade de Vendas')


# Visualização do Streamlit

# construindo abas: (três abas)
# aba1, aba2, aba3 = st.tabs(3)
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

# construindo colunas: (quatro colunas)
# col1, col2, col3, col4 = st.columns(4)
# Adicionando as primeiras métricas em colunas:

with aba1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
    with col2:
        st.metric('Quant. Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
    with col3:
        st.metric('Quant. Produtos', dados['Produto'].nunique())
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with col4:
        st.metric('Preço Médio', formata_numero(dados['Preço'].mean(), 'R$'))
        st.plotly_chart(fig_receita_categorias, use_container_width = True)
    st.dataframe(dados.head())

with aba2:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
    with col2:
        st.metric('Quant. Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_estados, use_container_width = True)
    with col3:
        st.metric('Quant. Produtos', dados['Produto'].nunique())
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
    with col4:
        st.metric('Preço Médio', formata_numero(dados['Preço'].mean(), 'R$'))
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    #col1, col2, col3, col4 = st.columns(4)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.metric('Preço Médio', formata_numero(dados['Preço'].mean(), 'R$'))
        fig_receita_vendedores = px.bar(
            vendedores[['sum']].sort_values('sum', ascending = True).head(qtd_vendedores),
            x='sum',
            y=vendedores[['sum']].sort_values('sum', ascending=True).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (Total de Vendas)')
        fig_receita_vendedores.update_layout(yaxis_title = 'Vendedor')
        fig_receita_vendedores.update_layout(xaxis_title = 'Total de Vendas')
        st.plotly_chart(fig_receita_vendedores)
        
           
    with col2:
        st.metric('Quant. Vendas', formata_numero(dados.shape[0]))
        st.metric('Quant. Produtos', dados['Produto'].nunique())
        fig_vendas_vendedores = px.bar(
            vendedores[['count']].sort_values('count', ascending=True).head(qtd_vendedores),
            x='count',
            y=vendedores[['count']].sort_values('count', ascending=True).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (Quantidade de Vendas)')
        fig_vendas_vendedores.update_layout(yaxis_title = 'Vendedor')
        fig_vendas_vendedores.update_layout(xaxis_title = 'Quantidade de Vendas')
        st.plotly_chart(fig_vendas_vendedores)
        
    #with col3:
    #    st.metric('Quant. Produtos', dados['Produto'].nunique())
        
    #with col4:
    #    st.metric('Preço Médio', formata_numero(dados['Preço'].mean()))        


# # Adicionando as primeiras métricas:
# col1, col2, col3 = st.columns(3)
# col1.metric('Receita', dados['Preço'].sum())
# col2.metric('Quant. de vendas', dados.shape[0])
# col3.metric('Quant. de Produtos', dados['Produto'].nunique())



#st.write(dados)
# st.dataframe(dados[['Produto', 'Preço']].head())
#st.dataframe(dados.head(10))

#print("Olá Mundo!")
