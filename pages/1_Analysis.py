from pymongo import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import sys
sys.path.insert(1, '.')
from handlers.MongoDBHandler import MongoDBHandler

load_dotenv()
MONGODB_PROCESSED_COLLECTION = os.environ.get('MONGODB_PROCESSED_COLLECTION')

mongodbhandler = MongoDBHandler(MONGODB_PROCESSED_COLLECTION)

today = datetime.now()
thirty_days_ago = today - timedelta(days=30)

query = {"disease_disorder": {"$exists": True}}
documents = mongodbhandler.read_data(query)

diseases_counter = Counter()
for doc in documents:
    date_str = doc.get('date')
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        if thirty_days_ago <= date_obj <= today:
            diseases_counter.update(doc['disease_disorder'])

top_10_diseases = diseases_counter.most_common(10)

if top_10_diseases:
    diseases, frequencies = zip(*top_10_diseases)

    sorted_indices = sorted(range(len(frequencies)), key=lambda k: frequencies[k], reverse=True)
    sorted_diseases = [diseases[i] for i in sorted_indices]
    sorted_frequencies = [frequencies[i] for i in sorted_indices]

    chart_data = pd.DataFrame(data={'Disease':diseases, 'Frequency':frequencies})
    st.subheader('Top 10 Frequently Occurring Diseases in the Month of July')
    st.bar_chart(chart_data, x='Disease', y='Frequency')

else:
    st.write("No diseases available for the past 30 days.")

today = datetime.now()
thirty_days_ago = today - timedelta(days=30)

query = {
    'date': {'$gte': '14-Jul-2023'},  # Assuming 'date' is in the format 'dd-mmm-yyyy'
    'locations': {'$exists': True}
}

documents = collection.find(query)

# Count the frequency of each location
locations_counter = Counter()
for doc in documents:
    date_str = doc.get('date')
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, "%d-%b-%Y")
        if thirty_days_ago <= date_obj <= today:
            locations = doc.get('locations')
            if locations is not None:
                locations_counter.update(locations)

top_10_locations = locations_counter.most_common(10)

if top_10_locations:
    locations, frequencies = zip(*top_10_locations)

    sorted_indices = sorted(range(len(frequencies)), key=lambda k: frequencies[k], reverse=True)
    sorted_locations = [locations[i] for i in sorted_indices]
    sorted_frequencies = [frequencies[i] for i in sorted_indices]

    chart_data = pd.DataFrame(data={'Location': sorted_locations, 'Frequency': sorted_frequencies})
    st.title('Top 10 Frequently Occurring Locations in the Month of July')
    st.bar_chart(chart_data, x='Location', y='Frequency')

else:
    st.write("No locations available for the past 30 days.")
