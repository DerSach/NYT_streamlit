import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from adjustText import adjust_text

#---------------------------------------
# Fonctions definition and df imports
#---------------------------------------

@st.cache
def read_content():
    comments_df = pd.read_csv('data/TOTAL_BERT_LIGHT.csv')
    articles_df = pd.read_csv('data/articles_vf6.csv')
    cloud_df = pd.read_csv('data/cloud_keywords.csv')
    df_visualisation_keywords = pd.read_csv('data/keyword_polarity_plot.csv')

    table_df = comments_df.groupby(["state_acc"], as_index=False).agg({'commentType': 'count', 'is_emo': 'sum'})
    table_df["state_metric"] =  table_df["is_emo"]/table_df["commentType"]
    table_df = table_df.rename(columns={"is_emo": "is_emo_state", "commentType":"nb_comments_state"})

    return comments_df, articles_df, cloud_df, df_visualisation_keywords, table_df

comments_df, articles_df, cloud_df, df_visualisation_keywords, table_df = read_content()

# @st.cache
# def get_line_chart_data(df, keyword1, keyword2):
#     df1 = df[df['unique_kw'].str.contains(keyword1)]
#     grouped_df = df1.groupby('month', as_index = False).agg({'debate_score':'mean'})
#     grouped_df['month'] = grouped_df['month'].map(month_dico)
#     plt.plot(grouped_df['month'], grouped_df['debate_score'], c = 'r', label = keyword1)
#     df2 = df[df['unique_kw'].str.contains(keyword2)]
#     grouped_df = df.groupby('month', as_index = False).agg({'debate_score':'mean'})
#     grouped_df['month'] = grouped_df['month'].map(month_dico)
#     plt.plot(grouped_df['month'], grouped_df['debate_score'], c = 'b', label = keyword2)
#     plt.ylabel('Debate score')
#     plt.title('Evolution of debate scores for given keywords-related articles')
#     plt.legend()
#     plt.show()

@st.cache
def plot_evolution_score(df, keyword1, keyword2):
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
    )
    return fig

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
    
#---------------------------------------
# Pages setup
#---------------------------------------

page = st.sidebar.selectbox("",['Welcome', 'Keyword mapping','Keyword analysis over time','Topic polarity', 'Keyword search'])

#---------------------------------------
# Welcome screen that loads fast
#---------------------------------------

if page == 'Welcome':
    # Overall title

    st.text("Welcome 🎙")

#---------------------------------------
# Keyword mapping
#---------------------------------------

if page == 'Keyword mapping':
    # Overall title
    st.markdown("<h1 style='text-align: center; color: DarkBlue;'>Keyword mapping</h1>", unsafe_allow_html=True)
    st.text("")
    
    '''
    # Identifying clustering of NYT articles keywords
    ''' 
    
#    sns.set()
    # Initialize figure
    fig, ax = plt.subplots(figsize = (11.7, 8.27))
    sns.scatterplot(cloud_df['x'], cloud_df['y'], alpha = 0.8)
    # Import adjustText, initialize list of texts

    texts = []
    words_to_plot = list(np.arange(0, len(cloud_df), 10))
    # Append words to list
    for word in words_to_plot:
        texts.append(plt.text(cloud_df.loc[word,'x'], cloud_df.loc[word, 'y'], cloud_df.loc[word,'kw'], fontsize = 14))
    
    # Plot text using adjust_text (because overlapping text is hard to read)
    adjust_text(texts, force_points = 0.4, force_text = 0.4, 
                expand_points = (2,1), expand_text = (1,2),
                arrowprops = dict(arrowstyle = "-", color = 'black', lw = 0.5))
    plt.show()
    
    st.pyplot(fig)

#---------------------------------------
# Keyword analysis over time
#---------------------------------------

if page == 'Keyword analysis over time':
    # Overall title
    st.markdown("<h1 style='text-align: center; color: DarkBlue;'>Keyword analysis over time</h1>", unsafe_allow_html=True)
    st.text("")
    
    '''
    # Overview of debate score evolution on certain keywords over time
    '''
    keyword1 = st.text_input('What keyword trend do you want to look at? 📉 📈')
    keyword2 = st.text_input('What other keyword trend do you want to look at? 📈 📉')

    fig1 = plot_evolution_score(articles_df, keyword1 = 'trump', keyword2 = 'biden')

    st.plotly_chart(fig1)

#---------------------------------------
# Keyword polarity
#---------------------------------------

if page == 'Topic polarity':
    # Overall title
    st.markdown("<h1 style='text-align: center; color: DarkBlue;'>Topic polarity</h1>", unsafe_allow_html=True)
    st.text("")
    
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
    fig2.update_layout(title='Keywords negative polarity')
    fig2.update_xaxes(title_text="Amount of strongly negative comments on topic")
    fig2.update_yaxes(title_text="Nb of States strongly reacting on topic")  
    
    st.plotly_chart(fig2)  
        
#---------------------------------------
# Keyword search
#---------------------------------------

if page == 'Keyword search':
    # Overall title
    st.markdown("<h1 style='text-align: center; color: DarkBlue;'>Keyword search</h1>", unsafe_allow_html=True)
    st.text("")

    '''
    # New York Times readers emotional map
    '''

    keyword = st.text_input('What keyword are you interested about? 🔍')
        
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
    title="Keyword-related articles emotional intensity across US states for this keyword",
    yaxis_title="Debate score",
    geo_scope='usa',  # Plot only the USA instead of globe
    )

    st.plotly_chart(fig)

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

    articles_selected_df = articles_df[articles_df["unique_kw"].str.contains(keyword)]
    articles_selected_df.sort_values(by = 'share_of_total_comments', ascending = False, inplace = True)
    st.write('🥇' , list(articles_selected_df['headline'])[0])
    st.write('🥈', list(articles_selected_df['headline'])[1])
    st.write('🥉' , list(articles_selected_df['headline'])[2])

    st.write(f'<style>{CSS}</style>', unsafe_allow_html=True)

