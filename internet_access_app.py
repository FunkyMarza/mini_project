import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from copy import deepcopy
from plotly.subplots import make_subplots

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

st.set_page_config(layout="wide")

st.title("Internet Access Around the Globe")
st.header("Data visualization project - Constructor Academy")
st.subheader("January 2025 - Marisa Davis")
st.text('To select individual countries, open the left sidebar')

#Loading my data
internet_df_raw = load_data(path="./data/raw/share-of-individuals-using-the-internet.csv")
df = deepcopy(internet_df_raw)

    #Dataset prep
df.rename(columns = {'Entity': 'country', 'Year':'year', 'Individuals using the Internet (% of population)':'users_pop'}, inplace=True)
   
    #Getting continents from gapminder
gapminder_data = px.data.gapminder()
country_continent = gapminder_data.set_index('country')['continent'].to_dict()
df['continent'] = df['country'].map(country_continent)
df = df.dropna()

    #Continent subsets
df_asia = df[df['continent']=='Asia']
df_europe = df[df['continent']=='Europe']
df_americas = df[df['continent']=='Americas']
df_africa = df[df['continent']=='Africa']
df_oceania = df[df['continent']=='Oceania']

    #Continent means
def get_yearly_means(df):
    mean_internet_user_prop = df.groupby('year')['users_pop'].mean().reset_index()
    return mean_internet_user_prop
    
means_asi = get_yearly_means(df_asia)
means_eu = get_yearly_means(df_europe)
means_ame = get_yearly_means(df_americas)
means_afr = get_yearly_means(df_africa)
means_oce = get_yearly_means(df_oceania) 
    #Concatenating to a single dataframe for use in the continent selector
means_asi['continent'] = 'Asia'
means_eu['continent'] = 'Europe'
means_ame['continent'] = 'Americas'
means_afr['continent'] = 'Africa'
means_oce['continent'] = 'Oceania'

merged_means_df = pd.concat(
    [means_asi, means_eu, means_ame, means_afr, means_oce],
    ignore_index=True)


#showing the dataframe
if st.checkbox("Show dataframe"):
    st.subheader("Used dataset:")
    st.dataframe(data = df)

#creating the world means by year df
mean_internet_user_prop = df.groupby('year')['users_pop'].mean().reset_index()
mean_df = mean_internet_user_prop

#defining layout
left_column, middle_column, right_column = st.columns([2, 1, 1])

#show country selector SIDEBAR
st.sidebar.header('Select countries to display')
sorted_unique_countries = sorted(pd.unique(df['country']))
selected_countries = st.sidebar.multiselect("Countries", sorted_unique_countries, [])
#country = ["All"]+sorted(pd.unique(df['country']))
#country = left_column.selectbox("Choose a country", country)

#show continent selector
continent = ["All"]+["None"]+sorted(pd.unique(df['continent']))
continent = left_column.selectbox("Choose a continent", continent)

#show context selector
show_context = right_column.radio(
    label='Show context info', options=['Yes', 'No'])

#show world mean selector
show_means = middle_column.radio(
    label='Show world mean', options=['Yes', 'No'])

#creating subsets for countries
df_selected_countries = df[(df.country.isin(selected_countries))]

#Plot
fig = make_subplots()

#Plot for countries
for country in df_selected_countries['country'].unique():
    reduced_df = df_selected_countries[df_selected_countries['country'] == country]
    fig.add_trace(
        go.Scatter(x=reduced_df['year'], y=reduced_df['users_pop'],
                   name = country, mode="lines"))

#Plot for continents

if continent == "All":
    fig.add_trace(
        go.Scatter(x=means_asi['year'], y=means_asi['users_pop'], name="Asia",
               mode="lines"))
    fig.add_trace(
        go.Scatter(x=means_eu['year'], y=means_eu['users_pop'], name="Europe",
                mode="lines"))
    fig.add_trace(
        go.Scatter(x=means_ame['year'], y=means_ame['users_pop'], name="Americas",
                mode="lines"))
    fig.add_trace(
        go.Scatter(x=means_afr['year'], y=means_afr['users_pop'], name="Africa",
                mode="lines"))
    fig.add_trace(
        go.Scatter(x=means_oce['year'], y=means_oce['users_pop'], name="Oceania",
                mode="lines"))
elif continent == "None": pass
else:
    reduced_df = merged_means_df[merged_means_df["continent"] == continent]
    fig.add_trace(
        go.Scatter(x=reduced_df['year'], y=reduced_df['users_pop'],
                   name = continent, mode="lines"))

# Plot features
fig.update_yaxes(title={"text": "Individuals using the Internet (% of population)", "font": {"size": 12}})
fig.update_xaxes(title={"text": "Year", "font": {"size": 12}})
fig.update_layout(height=550,
    plot_bgcolor="whitesmoke",
    paper_bgcolor='lightsteelblue',
    hovermode="x",
    title={"text": "Internet user proportion through the years", "font": {"size": 24}})

#Showing the world mean
if show_means == "Yes":
    fig.add_trace(
        go.Scatter(x=mean_df['year'], y=mean_df['users_pop'], name="World mean",
                marker={"color": "navy"}, line_dash="dash",
                mode="lines"))

#Showing context
if show_context == "Yes":
    fig.add_vline(x=1991, line_width=2, line_dash="dash", line_color="green", 
                annotation_text="1991: Web opened to the public", annotation_position="top right")

    fig.add_vline(x=1995, line_width=2, line_dash="dash", line_color="green", 
                annotation_text="1995: The Rise of Commercial Internet", annotation_position="bottom right")

    fig.add_vrect(x0=2001, x1=2005, 
                annotation_text="Pioneering Platforms and the Rise of Social Media", annotation_position="top left",
                fillcolor="green", opacity=0.25, line_width=0)

    fig.add_vline(x=2014, line_width=2, line_dash="dash", line_color="green", 
                annotation_text="2014: Mobile Internet Overtakes Desktop", annotation_position="bottom left")


st.plotly_chart(fig)

####################

# Defining layout
left_column, middle_column, right_column = st.columns([2, 1, 1])

#show year selector
years = sorted(pd.unique(df['year']))
#year = left_column.selectbox("Choose a Year", years)

#slider
year = st.select_slider("Slide to display the map for this year", options = years)

#creating subsets for years
year_map_df = df[df["year"] == year]

means = reduced_df.groupby('year').mean(numeric_only=True)

# creating the map view
with open("./data/raw/countries.geojson") as f:
    geojson_countries = json.load(f)

fig2 = px.choropleth_mapbox(
    year_map_df,
    geojson = geojson_countries,
    locations = year_map_df["Code"],              
    featureidkey = "properties.ISO_A3",  
    color = year_map_df["users_pop"],               
    title = f"Internet user proportion in {year}",
    color_continuous_scale = "Viridis",
    mapbox_style = "carto-positron",    
    zoom = 1,                          
    center = {"lat": 54, "lon": 15},  
    custom_data=["country", "users_pop"]
    ) 

fig2.update_traces(marker_line_width=0)
fig2.update_traces(
    hovertemplate="<b>Country:</b> %{customdata[0]}<br>"
                  "<b>% of population:</b> %{customdata[1]:.2f}"
)
fig2.update_layout(height=600, width=1300)

st.plotly_chart(fig2)