from datetime import datetime, timedelta
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from collections import Counter
import pandas as pd
import logging
import os
import sys
sys.path.insert(1, '.')
from handlers.MongoDBHandler import MongoDBHandler

# Query the database and get documents with disease and location entities present
load_dotenv()
MONGODB_PROCESSED_COLLECTION = os.environ.get('MONGODB_PROCESSED_COLLECTION')
mongodbhandler = MongoDBHandler(MONGODB_PROCESSED_COLLECTION)

disease_query = {"disease_disorder": {"$exists": True}}
disease_documents = mongodbhandler.read_data(disease_query)

location_query = {"locations": {"$exists": True}}
location_documents = mongodbhandler.read_data(location_query)

# Fuzzy matching function
def group_similar_diseases(disease_list, frequency_list, threshold=70):
    grouped_diseases = {}

    for idx, disease in enumerate(disease_list):
        matched = False

        for existing_disease in grouped_diseases:
            similarity = fuzz.ratio(disease, existing_disease)
            if similarity >= threshold:
                frequency = grouped_diseases.get(existing_disease)
                frequency += frequency_list[idx]

                grouped_diseases.update({existing_disease: frequency})
                matched = True
                break
        
        if not matched:
            grouped_diseases[disease] = frequency_list[idx]

    return grouped_diseases

number_of_common = 100  # 100 most common entities
today = datetime.now()
diseases_counter = Counter()
locations_counter = Counter()

# Streamlit configuration
col1, col2, col3, col4 = st.columns([1, 1.7, 5.5, 1.7])

st.session_state.visibility = "hidden"
st.session_state.disabled = False

time_dict = {
    '7 days': 7,
    '30 days': 30,
    '3 months': 90,
    '6 months': 180,
    '1 year': 365
}

# Display diseases chart

with col1:
    st.markdown("<h1>Top</h1>", unsafe_allow_html=True)
with col2:
    diseases_results_option = st.selectbox(
        'Number of results: ', (5, 10, 15, 25), 
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        key='diseases_results_option'
    )
    
with col3:
    st.markdown("<h1>diseases in the past</h1>", unsafe_allow_html=True)
with col4:
    diseases_time_option = st.selectbox(
        'Time period: ', ('7 days', '30 days', '3 months', '6 months', '1 year'),
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        key='diseases_time_option'
    )

time_period = today - timedelta(days=time_dict.get(diseases_time_option))

for doc in disease_documents:
    date_str = doc.get('date')
    if isinstance(date_str, str):
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        except Exception as ex:
            logging.error(ex)
        disease_list = [d.lower() for d in doc['disease_disorder']]
        if 'infection' in disease_list or if 'death' in disease_list:
            continue
        if time_period <= date_obj <= today:
            diseases_counter.update(doc['disease_disorder'])

top_diseases = diseases_counter.most_common(number_of_common)

try:
    diseases, frequencies = zip(*top_diseases)

    sorted_indices = sorted(range(len(frequencies)), key=lambda k: frequencies[k], reverse=True)
    sorted_diseases = [diseases[i] for i in sorted_indices]
    sorted_frequencies = [frequencies[i] for i in sorted_indices]

    grouped_results = group_similar_diseases(sorted_diseases, sorted_frequencies)

    chart_data = pd.DataFrame(data={'Disease':grouped_results.keys(), 'Frequency': grouped_results.values()})
    chart_data = chart_data.sort_values('Frequency', ascending=False)[:diseases_results_option]

    st.bar_chart(chart_data, x='Disease', y='Frequency')

except:
    st.write(f"No diseases available for the past {diseases_time_option}.")


col5, col6, col7, col8 = st.columns([1.1, 1.85, 6.2, 1.7])
# Display locations chart

with col5:
    st.markdown("<h1>Top</h1>", unsafe_allow_html=True)
with col6:
    locations_results_option = st.selectbox(
        'Number of results: ', (5, 10, 15, 25), 
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        key='locations_results_option'
    )
with col7:
    st.markdown("<h1>locations in the past</h1>", unsafe_allow_html=True)
with col8:
    locations_time_option = st.selectbox(
        'Time period: ', ('7 days', '30 days', '3 months', '6 months', '1 year'),
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        key='locations_time_option'
    )

time_period = today - timedelta(days=time_dict.get(locations_time_option))
for doc in location_documents:
    date_str = doc.get('date')
    if isinstance(doc['locations'], list) and isinstance(date_str, str):
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        except Exception as ex:
            logging.error(ex)
        location_list = [l.lower() for l in doc['locations']]
        if 'hospital' in location_list:
            continue
        if time_period <= date_obj <= today:
            locations_counter.update(doc['locations'])

top_locations = locations_counter.most_common(number_of_common)

try:
    locations, frequencies = zip(*top_locations)

    sorted_indices = sorted(range(len(frequencies)), key=lambda k: frequencies[k], reverse=True)
    sorted_locations = [locations[i] for i in sorted_indices]
    sorted_frequencies = [frequencies[i] for i in sorted_indices]

    grouped_results = group_similar_diseases(sorted_locations, sorted_frequencies)

    chart_data = pd.DataFrame(data={'Location':grouped_results.keys(), 'Frequency':grouped_results.values()})
    chart_data = chart_data.sort_values('Frequency', ascending=False)[:locations_results_option]
    
    st.bar_chart(chart_data, x='Location', y='Frequency')

except:
    st.write(f"No locations available for the past {locations_time_option}.")
