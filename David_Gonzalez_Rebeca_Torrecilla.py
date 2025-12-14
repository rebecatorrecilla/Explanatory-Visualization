##########################################################################################################
#
#                                VI PROJECT: EXPLANATORY VISUALIZATION
#
#                                  Rebeca Torrecilla & David González
#                                Information Visualization  2025 - 2026
##########################################################################################################

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import io
from vega_datasets import data
import re


#### LOADING AND MERGING

# Read files directly from the directory
df_nsf_terminations = pd.read_csv('nsf_terminations_airtable.csv')
df_cruz_list = pd.read_csv('cruz_list.csv')
df_flagged_words = pd.read_csv('flagged_words_trump_admin.csv')  # Asumo que también lo necesitas

# Join of the NSF terminated grants with the Ted's Cruz list
df_cruz_list[['grant_number', 'in_cruz_list']] = df_cruz_list['grant_number;in_cruz_list'].str.split(';', expand=True)
df_cruz_list['grant_number'] = pd.to_numeric(df_cruz_list['grant_number'])

df_merged = pd.merge(df_nsf_terminations, df_cruz_list, left_on='grant_id', right_on='grant_number', how='left')

# We put 'False' instead of NaNs
df_merged['in_cruz_list'] = df_merged['in_cruz_list'].fillna(False)
df_merged['in_cruz_list'] = (df_merged['in_cruz_list'] == 'TRUE') | (df_merged['in_cruz_list'] == True)


# Elimination of duplicated columns
df_merged = df_merged.drop(columns=['grant_number', 'grant_number;in_cruz_list'])

#endregion



#### EXPLORATORY ANALYSIS AND CLEANING

# Data conversion
dates = [df_merged['nsf_start_date'],
         df_merged['nsf_end_date'],
         df_merged['termination_date'],
         df_merged['reinstatement_date'],
         df_merged['usa_start_date'],
         df_merged['usa_end_date']
         ]

for data in dates:
  data = pd.to_datetime(data, errors='coerce')

# Columns with limited unique values can be more efficient as 'category'
df_merged['in_cruz_list'] = df_merged['in_cruz_list'].astype('category')

# Elimination of innecessary columns
df_merged = df_merged.drop(columns=['suspended', 'termination_date', 'reinstatement_date',
                                    'reinstatement_indicator', 'nsf_url', 'usaspending_url',
                                    'award_type', 'usa_start_date',
                                    'usa_end_date', 'nsf_program_name', 'nsf_primary_program',
                                    'usa_nsf_office', 'nsf_obligated', 'usaspending_obligated',
                                    'usaspending_outlaid', 'estimated_budget', 'estimated_outlays',
                                    'estimated_remaining', 'division', 'directorate', 'div',
                                    'dir', 'record_sha1'])

# Save cleaned data
df_merged.to_csv('df_clean.csv', index=False)
 
# endregion



#### QUESTION 1 (dichromatic coropleth map)

cancellations_by_state = df_merged['org_state'].value_counts().reset_index()
cancellations_by_state.columns = ['State', 'Cancellations']

total_cancellations = cancellations_by_state['Cancellations'].sum()

top_15_cancellations = cancellations_by_state.sort_values(by='Cancellations', ascending=False).head(15).copy()
top_15_cancellations['Percentage of Total'] = (top_15_cancellations['Cancellations'] / total_cancellations) * 100
top_15_cancellations['Percentage Label'] = top_15_cancellations['Percentage of Total'].apply(lambda x: f'{x:.1f}%')

from vega_datasets import data

# We add the Wyoming state as an state without grant cancellations
new_row = pd.DataFrame([{'State': 'WY', 'Cancellations': 0}])
cancellations_by_state = pd.concat([cancellations_by_state, new_row], ignore_index=True)

# We eliminate Puerto Rico and Virgin Islands states
territories_to_exclude = ['PR', 'VI']
cancellations_filtered = cancellations_by_state[~cancellations_by_state['State'].isin(territories_to_exclude)].copy()

# Conversion to the numeric representation verga_datasets uses for the states
state_to_fips = {
    'AL': 1, 'AK': 2, 'AZ': 4, 'AR': 5, 'CA': 6, 'CO': 8, 'CT': 9, 'DE': 10, 'DC': 11,
    'FL': 12, 'GA': 13, 'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18, 'IA': 19, 'KS': 20,
    'KY': 21, 'LA': 22, 'ME': 23, 'MD': 24, 'MA': 25, 'MI': 26, 'MN': 27, 'MS': 28,
    'MO': 29, 'MT': 30, 'NE': 31, 'NV': 32, 'NH': 33, 'NJ': 34, 'NM': 35, 'NY': 36,
    'NC': 37, 'ND': 38, 'OH': 39, 'OK': 40, 'OR': 41, 'PA': 42, 'RI': 44, 'SC': 45,
    'SD': 46, 'TN': 47, 'TX': 48, 'UT': 49, 'VT': 50, 'VA': 51, 'WA': 53, 'WV': 54,
    'WI': 55, 'WY': 56
}

# We add the IDs column to our dataset
cancellations_filtered['id'] = cancellations_filtered['State'].map(state_to_fips)

color_scale=alt.Scale(scheme='reds')

# Complete map
states_map = alt.topo_feature(data.us_10m.url, 'states')

capitals_df = data.us_state_capitals()

state_name_to_abbr = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
}

capitals_df['State'] = capitals_df['state'].map(state_name_to_abbr)

capitals_df = capitals_df[['State', 'lat', 'lon']]
capitals_df.columns = ['State', 'latitude', 'longitude']

data_for_circles = pd.merge(cancellations_filtered, capitals_df, on='State')




# We create a dictionary with the association of each state with their currrent political party
party_map = {
    'AL': 'Republican', 'AK': 'Republican', 'AZ': 'Democrat', 'AR': 'Republican', 'CA': 'Democrat',
    'CO': 'Democrat', 'CT': 'Democrat', 'DE': 'Democrat', 'DC': 'Democrat', 'FL': 'Republican',
    'GA': 'Democrat', 'HI': 'Democrat', 'ID': 'Republican', 'IL': 'Democrat', 'IN': 'Republican',
    'IA': 'Republican', 'KS': 'Republican', 'KY': 'Republican', 'LA': 'Republican', 'ME': 'Democrat',
    'MD': 'Democrat', 'MA': 'Democrat', 'MI': 'Democrat', 'MN': 'Democrat', 'MS': 'Republican',
    'MO': 'Republican', 'MT': 'Republican', 'NE': 'Republican', 'NV': 'Democrat', 'NH': 'Democrat',
    'NJ': 'Democrat', 'NM': 'Democrat', 'NY': 'Democrat', 'NC': 'Republican', 'ND': 'Republican',
    'OH': 'Republican', 'OK': 'Republican', 'OR': 'Democrat', 'PA': 'Democrat', 'RI': 'Democrat',
    'SC': 'Republican', 'SD': 'Republican', 'TN': 'Republican', 'TX': 'Republican', 'UT': 'Republican',
    'VT': 'Democrat', 'VA': 'Democrat', 'WA': 'Democrat', 'WV': 'Republican', 'WI': 'Democrat', 'WY': 'Republican'
}

cancellations_filtered['Party'] = cancellations_filtered['State'].map(party_map)



# Background base
base_map = alt.Chart(states_map).mark_geoshape(
    fill='lightgray',
    stroke='white'
).properties(
    width=700,
    height=400
)

# We create a domain range for the graphics' legend
max_cancellations = cancellations_filtered['Cancellations'].max()
domain_range = [0, max_cancellations]

# Republicans map, we only take into account those states that are currectly republican
red_states_layer = alt.Chart(states_map).mark_geoshape(
    stroke='white'
).encode(
    color=alt.Color('Cancellations:Q',
                    scale=alt.Scale(scheme='reds', domain=domain_range),
                    legend=alt.Legend(title=['Cancellations', '(Republicans)'], orient='left')
                   ),
    tooltip=[
        alt.Tooltip('State:N'), alt.Tooltip('Cancellations:Q', format=','), alt.Tooltip('Party:N')
    ]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(cancellations_filtered, 'id', ['Cancellations', 'State', 'Party'])
).transform_filter(
    alt.datum.Party == 'Republican'
)


# Democrats map
blue_states_layer = alt.Chart(states_map).mark_geoshape(
    stroke='white'
).encode(
    color=alt.Color('Cancellations:Q',
                    scale=alt.Scale(scheme='blues', domain=domain_range),
                    legend=alt.Legend(title=['Cancellations', '(Democrats)'], orient='left')
                   ),
    tooltip=[
        alt.Tooltip('State:N'), alt.Tooltip('Cancellations:Q', format=','), alt.Tooltip('Party:N')
    ]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(cancellations_filtered, 'id', ['Cancellations', 'State', 'Party'])
).transform_filter(
    alt.datum.Party == 'Democrat'
)


dichromatic_map = (base_map + red_states_layer + blue_states_layer).project(
    type='albersUsa'
).properties(
    title='Cancelled Grants Distribution based on the state and the politician affiliation',
    #width=800,
    height=500
).resolve_scale(
    color='independent'
)

# endregion



#### QUESTIONS 2 AND 3 (pyramid_chart_political)

#Compute cancellations and budget per institution
cancellations_by_institution = df_merged['org_name'].value_counts().reset_index()
cancellations_by_institution.columns = ['Institution', 'Number of Cancellations']
budget_by_institution = df_merged.groupby('org_name')['nsf_total_budget'].sum().sort_values(ascending=False).reset_index()
budget_by_institution.columns = ['Institution', 'Total Budget Cancelled']
comparison_df = pd.merge(cancellations_by_institution, budget_by_institution, on='Institution')

# Get top 15 for cancellations and budget
top_15_count = cancellations_by_institution.head(15)['Institution'].tolist()
top_15_budget = budget_by_institution.head(15)['Institution'].tolist()
institutions_to_show = list(set(top_15_count + top_15_budget))
final_comparison_with_party = comparison_df[comparison_df['Institution'].isin(institutions_to_show)].copy()

# Add state and party
institution_to_state = df_merged[['org_name', 'org_state']].drop_duplicates()
institution_to_state.columns = ['Institution', 'State']
final_comparison_with_party = pd.merge(final_comparison_with_party, institution_to_state, on='Institution')
final_comparison_with_party['Party'] = final_comparison_with_party['State'].map(party_map)
sort_order = final_comparison_with_party.sort_values('Total Budget Cancelled', ascending=False)['Institution'].tolist()

#Text chart with the names of the institutions
middle = alt.Chart(final_comparison_with_party).mark_text(
    align='center', baseline='middle'
).encode(
    y=alt.Y('Institution:N', axis=None, sort=sort_order),
    text='Institution:N'
).properties(
    width=120        
)


# Left bars chart
left_bars = alt.Chart(final_comparison_with_party).mark_bar().encode(
    y=alt.Y('Institution:N', axis=None, sort=sort_order),
    x=alt.X('Number of Cancellations:Q', title='Avg Number of cancellations', sort='descending'),
    color=alt.Color('Party:N', legend=None,
                    scale=alt.Scale(domain=['Republican', 'Democrat'],
                                    range=['#bf3d2a', '#4c78a8'])),
    tooltip=['Institution:N','Party:N',
             alt.Tooltip('Number of Cancellations:Q', format=',')]
).properties(
    width=230     
)

left_average_line = alt.Chart(comparison_df).mark_rule(
    color='black', strokeDash=[3,3], size=2
).encode(x='average(Number of Cancellations):Q')

avg_value = comparison_df['Number of Cancellations'].mean()

left_average_text = alt.Chart(pd.DataFrame({'dummy': [1]})).mark_text(
    align='left',
    baseline='bottom',  
    color='black', 
    fontSize=11
).encode(
    x=alt.value(5),
    y=alt.value(390), 
    text=alt.value(f'Average: {avg_value:.1f}')
)


left = (left_bars + left_average_line + left_average_text).properties(width=230)



# Right bars chart
right_bars = alt.Chart(final_comparison_with_party).mark_bar().encode(
    y=alt.Y('Institution:N', axis=None, sort=sort_order),
    x=alt.X('Total Budget Cancelled:Q',
            title='Total Budget Cancelled ($)',
            axis=alt.Axis(format='s')),
    color=alt.Color('Party:N', legend=None,
                    scale=alt.Scale(domain=['Republican','Democrat'],
                                    range=['#bf3d2a','#4c78a8'])),
    tooltip=['Institution:N','Party:N',
             alt.Tooltip('Total Budget Cancelled:Q', format='$,.0f')]
).properties(
    width=230
)

right_average_line = alt.Chart(comparison_df).mark_rule(
    color='black', strokeDash=[3,3], size=2
).encode(x='average(Total Budget Cancelled):Q')

avg_budget = comparison_df['Total Budget Cancelled'].mean()

right_average_text = alt.Chart(pd.DataFrame({'dummy': [1]})).mark_text(
    align='right',    
    baseline='bottom',
    color='black', 
    fontSize=11
).encode(
    x=alt.value(220),   
    y=alt.value(390),  
    text=alt.value(f'Average: ${avg_budget:,.0f}')  
)

right = (right_bars + right_average_line + right_average_text).properties(width=230)



# Aggregate the three charts
pyramid_chart_political = alt.concat(
    left, middle, right,
    columns=3,
    spacing=10
).properties(
    title='Comparison Between Cancelled Grants vs. Budget by Institutions and Political Affiliation'
).resolve_scale(x='independent').configure_title(
    anchor='middle'     
)

# endregion



#### QUESTION 4 (proportion_chart)


# Load flagged words
flagged_words_df = pd.read_csv('flagged_words_trump_admin.csv')
flagged_words_set = set(flagged_words_df['flagged_word'])

# Clean the abstract
df_merged['abstract_clean'] = df_merged['abstract'].fillna('').str.lower()

def contains_flagged_word(text, flagged_words):
    """ Busca si alguna palabra marcada está en el abstract. """
    for word in flagged_words:
        # Precise search with re.search
        if re.search(r'\b' + re.escape(word) + r'\b', text): 
            return True
    return False

df_merged['has_flagged_word'] = df_merged['abstract_clean'].apply(
    lambda abstract: contains_flagged_word(abstract, flagged_words_set)
)

# General summary
general_summary = df_merged['has_flagged_word'].value_counts().reset_index()
general_summary.columns = ['Contains Flagged Word', 'Number of Grants']
general_summary['Contains Flagged Word'] = general_summary['Contains Flagged Word'].map({True: 'Yes', False: 'No'})



percentage_flaggedw = (1787 * 100) / 1970
percentage_text = f"{percentage_flaggedw:.1f}"

label_flagged = alt.Chart().mark_text(
    text=f'{percentage_text}%',
    align='right',
    fontWeight='bold',
    color = 'white',
    fontSize=20,
    x=80,
    y=70
)

# Percentage of abstracts without flagged words
percentage_text2 = f"{100 - percentage_flaggedw:.1f}"

label_not_flagged = alt.Chart().mark_text(
    text=f'{percentage_text2}%',
    align='right',
    fontWeight='bold',
    color = '#4f4f4f',
    fontSize=15,
    x=70,
    y=25
)


# Aggregated bars chart
stacked_bar_chart = alt.Chart(general_summary).mark_bar().encode(
    y=alt.Y('Number of Grants:Q'),
    color=alt.Color('Contains Flagged Word:N',
                    title=['Did the abstract', 'contain a flagged', 'word?'],
                    scale=alt.Scale(domain=['No', 'Yes'], range=['#d3d3d3', '#965493']),
                    legend=alt.Legend(orient="right")
                   ),
    tooltip=['Contains Flagged Word:N', 'Number of Grants:Q']
).properties(
    title=['Proportion of Cancelled Grants', 'with and without Flagged Words'],
    height=400,
)


# Final chart
proportion_chart = alt.layer(
    stacked_bar_chart, 
    label_flagged, 
    label_not_flagged, 
    data=general_summary
).properties(
    title=['Proportion of Cancelled Grants', 'with and without Flagged Words']
)

# endregion



#### QUESTION 5 (heatmap)


# Summary of reinstations and Cruz's list
reinstated_cruz_summary = df_merged.groupby(['reinstated', 'in_cruz_list']).size().reset_index(name='count')
reinstated_cruz_summary['reinstated'] = reinstated_cruz_summary['reinstated'].map({True: 'Reinstated', False: "Don't reinstated"})
reinstated_cruz_summary['in_cruz_list'] = reinstated_cruz_summary['in_cruz_list'].map({True: "In Cruz's list", False: "Not in Cruz's list"})

# Compute percentages
group_totals = reinstated_cruz_summary.groupby('reinstated')['count'].transform('sum')
reinstated_cruz_summary['Percentage based on reintegration'] = (reinstated_cruz_summary['count'] / group_totals) * 100
reinstated_cruz_summary['Percentage based on reintegration'] = reinstated_cruz_summary['Percentage based on reintegration'].round(2)
reinstated_cruz_summary['TextLabel'] = reinstated_cruz_summary['Percentage based on reintegration'].apply(lambda x: f'{x:.1f}%')

# Heatmap
heatmap = alt.Chart(reinstated_cruz_summary).mark_rect().encode(
    x=alt.X('reinstated:N', title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y('in_cruz_list:N', title=None),
    color=alt.Color('count:Q',
                    title='Number of Grants',
                    scale=alt.Scale(scheme='goldorange')
                   ),
    tooltip=['reinstated:N', 'in_cruz_list:N', 'count:Q', 'TextLabel:N']
)

# Text layer
text = alt.Chart(reinstated_cruz_summary).mark_text(
    color='white',
    fontSize=14,
    fontWeight='bold'
).encode(
    x='reinstated:N',
    y='in_cruz_list:N',
    text=alt.Text('count_and_percent:N')
).transform_calculate(
    count_and_percent="[datum.count, datum.TextLabel]"
)

# Final heatmap
q5_heatmap = (heatmap + text).properties(
    title=['Crossed Analysis: Reinstatements vs. Cruz\'s list', ''],
    height=400
)

# endregion



#### STREAMLIT VISUALIZATION

st.title("NSF terminated grants")
st.write("Rebeca Torrecilla, David Gonzalez")

st.altair_chart(dichromatic_map, theme=None, use_container_width=True)
st.altair_chart(pyramid_chart_political, theme=None, use_container_width=True)

st.write("")   

col21, col22 = st.columns([2, 3])

with col21:
    st.altair_chart(
        proportion_chart, 
        theme=None, 
        use_container_width=True
    )

with col22:
    st.altair_chart(
        q5_heatmap, 
        theme=None, 
        use_container_width=True
    )

# endregion