import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#---------------------------------------
# Fonctions definition and df imports
#---------------------------------------

@st.cache
def read_content():
    comments_df = pd.read_csv('data/TOTAL_BERT_LIGHT.csv')
    
    articles_df = pd.read_csv('data/articles_vf6.csv')
    
    np.random.seed(11)
    cloud_df = pd.read_csv('data/cloud_keywords.csv',index_col=[0])
    # Crée une palette de couleur
    # Passer sous 15 pour des couleurs plus pastelles
    cloud_df['color']=round(np.random.randn(1)*(cloud_df.x+cloud_df.y))+15

    df_visualisation_keywords = pd.read_csv('data/keyword_polarity_plot.csv')

    table_df = pd.read_csv('data/table_df.csv')

    return comments_df, articles_df, cloud_df, df_visualisation_keywords, table_df

comments_df, articles_df, cloud_df, df_visualisation_keywords, table_df = read_content()

#---------------------------------------
# Topic mapping functions and variables
#---------------------------------------

list_a_plot = ['donald','biden','harris','barack','iraq',
               'wine','cooking','video','internet','science','biology',
               'factory','manufacturing','impeachment','law','justice',
               'hospital','medicine','care','vaccination','epidemic','coronavirus','mexico','liberty',
               'tennis','discrimination','sport','twitter','facebook','police','safety']

x_coords =[9, 9, -5, 10, 9, -9, -5, -9, 9, -9, 5, 5, -5,
           5, 5, -9, -9, 10, 5, -5, -5, 10,5,5,-50,-15,-40,-30,19,9,-15] 
y_coords =[-10, 25, -25, 10, 22, 5, 10, 20, -20, -20, 20,
           25, 10, 25, 10, -25, 22, -15, 5, 10, -10, 22,-30,-25,0,-20,0,3,-15,-20,-20]

@st.cache
def annote(mot,ind,fig):
  fig.add_annotation(
        x=cloud_df[cloud_df.kw==mot].x.values[0],
        y=cloud_df[cloud_df.kw==mot].y.values[0],
        xref="x",
        yref="y",
        text=mot,
        showarrow=True,
        font=dict(
            family="Courier New, monospace",
            size=16,
            color="#3C2100"
            ),
        align="center",
        arrowhead=1,
        arrowsize=1,
        arrowwidth=0.5,
        arrowcolor="#636363",
        ax=x_coords[ind],
        ay=y_coords[ind],
        opacity=1)

@st.cache
def plot_cloud_kw(cloud_df):
    fig = go.Figure(data=go.Scatter(x=cloud_df['x'],
                                y=cloud_df['y'],
                                mode='markers',
                                marker_color=cloud_df['color'],
                                text=cloud_df['kw'])) # hover text goes here
    fig.update_layout(title='Keywords clustering', width=900,height=600)
    for el in enumerate(list_a_plot): # Permet de ploter les mots voulus sur certains points
        annote(el[1],el[0],fig)
        
    return fig

#---------------------------------------
# Topic analysis over time functions
#---------------------------------------

@st.cache
def plot_evolution_score(df, keyword1 = 'trump', keyword2 = 'biden'):
    df1 = df[df['unique_kw'].str.contains(keyword1)]
    grouped_df = df1.groupby('month', as_index = False).agg({'debate_score':'mean'})
    grouped_df['month'] = grouped_df['month'].map(month_dico)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grouped_df['month'], y=grouped_df['debate_score']*1000,
                    name=keyword1))
    df2 = df[df['unique_kw'].str.contains(keyword2)]
    grouped_df = df.groupby('month', as_index = False).agg({'debate_score':'mean'})
    grouped_df['month'] = grouped_df['month'].map(month_dico)
    fig.add_trace(go.Scatter(x=grouped_df['month'], y=grouped_df['debate_score']*1000,
                name=keyword2))
    fig.update_layout(
    title="Evolution of debate scores for given keywords-related articles",
    yaxis_title="Debate score",
    width=900,height=600
    )
    return fig

#---------------------------------------
# Topic search functions
#---------------------------------------

@st.cache
def search_word(word,df):
    custom_search = df[df["unique_kw"].str.contains(word)]
    custom_search_metrics = custom_search.groupby(["state_acc"]).agg({'commentType': 'count', 'is_emo': 'sum'})
    custom_search_metrics["topic_state_metric"] =  custom_search_metrics["is_emo"]/custom_search_metrics["commentType"]
    custom_search_metrics = custom_search_metrics.reset_index()
    custom_search_metrics = custom_search_metrics.merge(table_df, on="state_acc")
    custom_search_metrics["distance_to_state"] = custom_search_metrics["topic_state_metric"] - custom_search_metrics["state_metric"]
    custom_search_metrics["distance_to_country"] = custom_search_metrics["topic_state_metric"] - table_df["state_metric"].mean()
    custom_search_metrics.loc[custom_search_metrics['distance_to_state'] < 0,'distance_to_state'] = 0
    custom_search_metrics.loc[custom_search_metrics['distance_to_country'] < 0,'distance_to_country'] = 0
    custom_search_metrics = custom_search_metrics.sort_values(by="distance_to_country", ascending = False)
    return custom_search_metrics

month_dico = {1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec'}

@st.cache    
def plot_articles(word):
  custom_search = comments_df[comments_df["unique_kw"].str.contains(word)]
  custom_search_metrics = custom_search.groupby(["months"]).sum()["is_emo"]
  custom_search_metrics = custom_search_metrics.reset_index()
  custom_search_metrics["months"] = custom_search_metrics["months"].map(month_dico)
  fig = px.line(custom_search_metrics, x="months", y="is_emo", title=f'Evolution over time of sentiment score for {word}')
  max_months = custom_search_metrics["months"].iloc[custom_search_metrics["is_emo"].idxmax()]
  articles_df["month"] = articles_df["month"].map(month_dico)
  search_articles = articles_df[articles_df["unique_kw"].str.contains(word)]
  search_articles = search_articles[search_articles["month"]==max_months] 
  return fig, search_articles.sort_values(by="engagement_score", ascending=False)
    
#---------------------------------------
# Pages setup
#---------------------------------------


page = st.sidebar.selectbox("",['Welcome', 'Topic mapping','Topic analysis over time', 'Topic search'])

#---------------------------------------
# Welcome screen that loads fast
#---------------------------------------

if page == 'Welcome':
    # Overall title

    st.text("Welcome 🎙")

#---------------------------------------
# Keyword mapping
#---------------------------------------

if page == 'Topic mapping':
    # Overall title
    st.markdown("<h1 style='text-align: center; color: DarkBlue;'>Topic mapping</h1>", unsafe_allow_html=True)
    st.text("")
    
    '''
    # Identifying clustering of NYT articles topics
    ''' 

    fig_kw = plot_cloud_kw(cloud_df)
    
    st.plotly_chart(fig_kw, width=900,height=600)
    
    '''
    # Which topics unleashed the most passions among readers?
    '''
    
    df_visualisation_keywords['sized_polarize']=df_visualisation_keywords.nb_polarizes_comments #Scaling
    fig2 = go.Figure(data=go.Scatter(x=df_visualisation_keywords['sized_polarize'], 
                                    y=df_visualisation_keywords['state_indifference'],
                                    #color = df_visualisation_keywords["nb_occ"], 
                                    mode='markers',
                                    marker=dict(
                                        size=16,
                                        color=df_visualisation_keywords['nb_occ'], #set color equal to a variable
                                        colorscale='Agsunset', # one of plotly colorscales
                                        showscale=True
                                    ),
                                    text=df_visualisation_keywords.keyword)) # hover text goes here
    fig2.update_layout(title='Topic negative polarity')
    fig2.update_xaxes(title_text="Amount of strongly negative comments on topic")
    fig2.update_yaxes(title_text="Nb of States strongly reacting on topic")  
    
    st.plotly_chart(fig2)  

#---------------------------------------
# Topic analysis over time
#---------------------------------------

if page == 'Topic analysis over time':
    # Overall title
    st.markdown("<h1 style='text-align: center; color: DarkBlue;'>Topic analysis over time</h1>", unsafe_allow_html=True)
    st.text("")
    
    '''
    # Overview of debate score evolution on certain topics over time
    '''
    keyword1 = st.text_input('What topic trend do you want to look at? 📉 📈')
    keyword2 = st.text_input('What other topic trend do you want to look at? 📈 📉')

    fig1 = plot_evolution_score(articles_df, keyword1, keyword2)

    st.plotly_chart(fig1,  width=900,height=600)
        
#---------------------------------------
# Keyword search
#---------------------------------------

if page == 'Topic search':
    # Overall title
    st.markdown("<h1 style='text-align: center; color: DarkBlue;'>Topic search</h1>", unsafe_allow_html=True)
    st.text("")

    '''
    # New York Times readers emotional map
    '''

    keyword = st.text_input('Which topic are you interested about? 🔍')
        
    custom_df = search_word(keyword,comments_df)

    #VISUALISATION
    fig = px.choropleth(custom_df,  # Input Pandas DataFrame
                    locations="state_acc",  # DataFrame column with locations 
                    color='distance_to_country',  # DataFrame column with color values
                    hover_name="state_acc", # DataFrame column hover info
                    locationmode = 'USA-states',
                    color_continuous_scale=px.colors.diverging.Portland,
                    ) # Set to plot as US States
    fig.update_layout(
    title="Topic-related articles emotional intensity across US states for this topic",
    yaxis_title="Debate score",
    geo_scope='usa',  # Plot only the USA instead of globe
    width=900,height=600)

    st.plotly_chart(fig, width=900,height=600)
    
    fig_art, art_df = plot_articles(keyword)
    
    st.plotly_chart(fig_art, width=900,height=600)

    CSS = """
    p {
        color: black;
        font-size: 30px;
        font-weight: bold;
        text-align: center;
    }
    """

    '''
    🔥🔥🔥 Hottest articles 🔥🔥🔥
    '''

    st.write('🥇' , list(art_df['headline'])[0])
    st.write('🥈', list(art_df['headline'])[1])
    st.write('🥉' , list(art_df['headline'])[2])

    st.write(f'<style>{CSS}</style>', unsafe_allow_html=True)

