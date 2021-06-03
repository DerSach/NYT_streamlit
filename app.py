import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#---------------------------------------
# Fonctions definition and df imports
#---------------------------------------

@st.cache
def read_content():
    comments_df = pd.read_csv('data/TOTAL_BERT_LIGHTv3.csv')
    
    articles_df = pd.read_csv('data/articles_vf8.csv')

    table_df = pd.read_csv('data/table_df.csv')

    return comments_df, articles_df, table_df

comments_df, articles_df, table_df = read_content()

#---------------------------------------
# 'Topic analysis' functions and variables
#---------------------------------------

us_state_abbrev = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
}

@st.cache
def search_word(word,df):
    custom_search = df[df["unique_kw"].str.contains(word)]
    custom_search_metrics = custom_search.groupby(["state_acc"]).agg({'commentType': 'count', 'is_emo': 'sum'})
    custom_search_metrics["topic_state_metric"] =  custom_search_metrics["is_emo"]/custom_search_metrics["commentType"]
    custom_search_metrics = custom_search_metrics.reset_index()
    custom_search_metrics = custom_search_metrics.merge(table_df, on="state_acc")
    custom_search_metrics["distance_to_country"] = custom_search_metrics["topic_state_metric"] - table_df["state_metric"].mean()
    custom_search_metrics.loc[custom_search_metrics['distance_to_country'] < 0,'distance_to_country'] = 0
    custom_search_metrics = custom_search_metrics.sort_values(by="distance_to_country", ascending = False)
    custom_search_metrics['state_name'] = custom_search_metrics['state_acc'].map(us_state_abbrev)
    custom_search_metrics["distance_to_country"] = custom_search_metrics["distance_to_country"] * 100
    return custom_search_metrics

@st.cache
def plot_map(df):
    fig = px.choropleth(df,  # Input Pandas DataFrame
                    locations="state_acc",  # DataFrame column with locations 
                    color='distance_to_country',  # DataFrame column with color values
                    hover_name="state_name", # DataFrame column hover info
                    locationmode = 'USA-states',
                    range_color = [df['distance_to_country'].min(),df['distance_to_country'].max()],
                    color_continuous_scale=px.colors.diverging.Portland,
                    labels={'distance_to_country':'% of overreaction'},
                    ) # Set to plot as US States
    fig.update_layout(
    title=f"{keyword.capitalize()}-related articles emotional intensity across US states for this topic",
    title_font_size = 18,
    font_size = 16,
    yaxis_title="Debate score",
    geo_scope='usa',  # Plot only the USA instead of globe
    font=dict(size=12),
    width=700,height=550)
    return fig

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
  fig = px.line(custom_search_metrics, x='months', y="is_emo")
  fig.update_layout(
      xaxis_title="",
      yaxis_title="Polarized comments",
      title_font_size = 20,
        font_size = 20,
      font=dict(size=16),
      width=700,
      height=600)
  max_months = custom_search_metrics["months"].iloc[custom_search_metrics["is_emo"].idxmax()]
  articles_copy = articles_df.copy()
  articles_copy["month"] = articles_copy["month"].map(month_dico)
  search_articles = articles_copy[articles_copy["unique_kw"].str.contains(word)]
  search_articles = search_articles[search_articles["month"]==max_months] 
  return fig, search_articles.sort_values(by="debate_score", ascending=False)

#---------------------------------------
# 'Topic comparison' functions
#---------------------------------------

@st.cache
def plot_evolution_score(df, keyword1, keyword2):
    df1 = df[df['unique_kw'].str.contains(keyword1)]
    grouped_df = df1.groupby('month', as_index = False).agg({'debate_score':'mean'})
    grouped_df['month'] = grouped_df['month'].map(month_dico)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grouped_df['month'], y=grouped_df['debate_score']*1000,
                    name=keyword1))
    df2 = df[df['unique_kw'].str.contains(keyword2)]
    grouped_df = df2.groupby('month', as_index = False).agg({'debate_score':'mean'})
    grouped_df['month'] = grouped_df['month'].map(month_dico)
    fig.add_trace(go.Scatter(x=grouped_df['month'], y=grouped_df['debate_score']*1000,
                name=keyword2))
    fig.update_layout(
    title=f'''Evolution of debate scores for {keyword1} and {keyword2}-related articles''',
    title_font_size = 20,
    font_size = 20,
    yaxis_title="Debate score",
    font=dict(size=16),
    width=750,
    height=600,
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1.0)
    )
    return fig
    
#---------------------------------------
# Pages setup
#---------------------------------------

page = st.sidebar.selectbox("",['Welcome', 'Topic analysis', 'Topics comparison'])

#---------------------------------------
# Welcome screen that loads fast
#---------------------------------------

if page == 'Welcome':
    # Overall title

    st.text("Welcome 🎙")
    
#---------------------------------------
# Topic analysis
#---------------------------------------

if page == 'Topic analysis':
    CSS1 = """
    p {
        color: black;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        background-color: white;
    }
    .stApp {
        background-image: url(https://www.poynter.org/wp-content/uploads/2020/07/AP_18228529433873.jpg);
        background-size: cover;
        backdrop-filter: blur(1px);
    }
    .block-container {
        background-color: white;
        margin-top: -60px;
    }
    .css-145kmo2 {
        font-size: 1.2rem;
    }
    """
    st.write(f'<style>{CSS1}</style>', unsafe_allow_html=True)
    '''
    # New York Times readers emotional map
    '''
    # Keyword input
    keyword = st.text_input('Which topic are you interested about? 🔍')
    custom_df = search_word(keyword,comments_df)
    
    # US map
    fig1 = plot_map(custom_df)
    st.plotly_chart(fig1, width=700,height=550)

    # Evolution over time
    st.write('When readers are the most emotionally engaged')
    st.write(f'for {keyword}-related articles')

    fig_art, art_df = plot_articles(keyword)
    st.plotly_chart(fig_art, width=700,height=600)

    # Top 3 articles
    '''
    🔥🔥🔥 Hottest articles 🔥🔥🔥
    '''

    st.write('🥇' , list(art_df['headline'])[0])
    st.write('🥈', list(art_df['headline'])[1])
    st.write('🥉' , list(art_df['headline'])[2])

#---------------------------------------
# Topics comparison
#---------------------------------------

if page == 'Topics comparison':
    # Overall title
    st.markdown("<h1 style='text-align: center; color: DarkBlue;'>Overview of debate score evolution on topic-related articles over time</h1>", unsafe_allow_html=True)
    st.text("")
    
    CSS2 = """
    .stApp {
        background-image: url(https://static01.nyt.com/images/2020/10/24/us/politics/22debate-ledeall-top1/22debate-ledeall-top1-videoSixteenByNine3000-v2.jpg);
        background-size: cover;
        backdrop-filter: blur(5px);
    }
    .block-container {
        background-color: white;
        margin-top: -60px;
    }
    .css-145kmo2 {
        font-size: 1.2rem;
    }
    """
    keyword1 = st.text_input('What topic trend do you want to look at? 📉 📈')
    keyword2 = st.text_input('What other topic trend do you want to look at? 📈 📉')
    
    st.write(f'<style>{CSS2}</style>', unsafe_allow_html=True)

    fig1 = plot_evolution_score(articles_df, keyword1, keyword2)

    st.plotly_chart(fig1,  width=750,height=600)
