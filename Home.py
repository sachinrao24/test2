import streamlit as st
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
import logging
from dotenv import load_dotenv
import os
import sys
sys.path.insert(1, 'Pipeline/')
from handlers.MongoDBHandler import MongoDBHandler

def filter_documents(documents, timespan):
    filtered_documents = []  # Initialize an empty list to store filtered documents
    
    for doc in documents:
        if isinstance(doc['date'], str):  # Use isinstance() instead of type()
            try:
                doc['datetime_object'] = datetime.strptime(doc['date'], '%d/%m/%Y')
            except Exception as ex:
                logging.error(ex)
    
    try:
        if timespan == 'this week':
            start_date = datetime.now() - relativedelta(days=7)
        elif timespan == 'this month':
            start_date = datetime.now().replace(day=1)
        elif timespan == 'past 3 months':
            start_date = datetime.now() - relativedelta(months=3)
        elif timespan == 'past 6 months':
            start_date = datetime.now() - relativedelta(months=6)
        elif timespan == 'past 1 year':
            start_date = datetime.now() - relativedelta(years=1)
        elif timespan == 'all time':
            start_date = datetime.now() - relativedelta(years=100)
        
        if start_date:
            filtered_documents = [doc for doc in documents if ('datetime_object' in doc and doc['datetime_object'] >= start_date)]
    except Exception as ex:
        logging.error(ex)
    
    return filtered_documents

def group_documents_by_cluster(documents):
    clustered_documents = {}

    for doc in documents:
        try:
            cluster_id = doc.get('cluster_id')
            display_document = doc.get('display_document')
            article_links = doc.get('article_links')

            if cluster_id not in clustered_documents:
                clustered_documents[cluster_id] = {'display': None, 'links': []}

            if display_document == 'yes':
                clustered_documents[cluster_id]['display'] = doc
            else:
                if article_links and isinstance(article_links, list):
                    clustered_documents[cluster_id]['links'].extend(article_links)
        except Exception as ex:
            logging.error(ex)
            continue

    return clustered_documents

def display_clustered_documents(clustered_documents):
    for cluster_id, cluster_data in clustered_documents.items():
        try:
            display_doc = cluster_data['display']
            links = cluster_data['links']

            if display_doc:
                st.write('Cluster ID:', cluster_id)
                st.write('Display Document:')
                st.write('Date:', display_doc.get('date'))
                st.write('Sentiment Color:', display_doc.get('sentiment_color'))
                # Add more display fields as needed

                st.write('Full Article:', display_doc.get('article_links'))

                with st.expander('See similar articles'):
                    for link in links:
                        st.markdown(f'- {link}')

                st.divider()
        except Exception as ex:
            logging.error(ex)
            continue

def sort_and_display(documents):
    sorted_documents = []
    st.divider()

    try:
        # Convert the date format for sorting
        documents = [doc for doc in documents if ('date' in doc and 'sentiment_score' in doc and type(doc['date']) == str)]
        for doc in documents:
            try:
                doc['date'] = datetime.strptime(doc['date'], '%d/%m/%Y')
                doc['date'] = doc['date'].strftime('%d-%B-%Y')
                doc['datetime_object'] = datetime.strptime(doc['date'], '%d-%B-%Y').date()
            except Exception as ex:
                logging.error(ex)

        # Sort the documents in descending order by the 'date' key
        sorted_documents = sorted(documents, key=lambda x: (x['datetime_object'], x['sentiment_score']), reverse=True)

    except Exception as ex:
            logging.error(ex)
    
    def isNaN(string):
        return (string != string)

    displayed_clusters = []
    for doc in sorted_documents:
        try:
            if 'category' not in doc or 'date' not in doc or 'cluster_id' not in doc:
                continue
            if type(doc['date']) != str:
                continue
            if doc['cluster_id'] in displayed_clusters:
                continue

            cluster_id = doc['cluster_id']
            same_cluster_documents = []
            display_document = None
            non_display_links = []
            for document in sorted_documents:
                if document['cluster_id'] == cluster_id:
                    same_cluster_documents.append(documents)
                    if document['display_document'] == 'yes':
                        display_document = document
                    else:
                        non_display_links.append(document['article_links'])

            displayed_clusters.append(cluster_id)

            if display_document:
                date = display_document['date']
                article_links = display_document['article_links']
                try:
                    sentiment_color = display_document['sentiment_color']
                except:
                    continue
                category_key = display_document['category']
                category_string='Categories: '

                if isinstance(category_key, str):
                    category_string += category_key
                elif isinstance(category_key, list):
                    category_string += str(category_key).strip('[]').replace("'", "")
                
                keys_to_check = ['sign_symptom', 'disease_disorder', 'locations', 'numeric_value', 'summary', 'title']
                keys_found = []
                not_found_messages = {
                    'summary': "No summary available.",
                    'disease_disorder': "No diseases found.",
                    'sign_symptom': "No symptoms found.",
                    'locations': "No locations found.",
                    'numeric_value': "No numeric entities found.",
                    'title': "No title found."
                }

                skip_document = False
                for key in keys_to_check:
                    if key in display_document:
                        if isNaN(display_document[key]):
                            keys_found.append(not_found_messages.get(key))
                        else:
                            if key in ['disease_disorder', 'locations', 'sign_symptom', 'numeric_value'] and type(display_document[key]) == list:
                                if len(display_document[key]) > 0:
                                    display_document[key] = set(display_document[key])
                                    if key == 'numeric_value':
                                        numeric_values_list = []
                                        value = display_document[key]
                                        for entity in value:
                                            number_and_qualifying_words = entity.split(': ')
                                            numeric_values_list.append(number_and_qualifying_words)
                                else:
                                    keys_found.append(not_found_messages.get(key))
                                    continue
                            if key == 'numeric_value':
                                keys_found.append(numeric_values_list)
                            else:
                                keys_found.append(str(display_document[key]).strip('[]').strip('{}'))
                    else:
                        keys_found.append(not_found_messages.get(key))
                        if key == 'summary' and not_found_messages[key] == display_document[key]:
                            skip_document = True
                            
                if skip_document:
                    continue
                    
                for key, value in zip(keys_to_check, keys_found):
                    if key == 'title':
                        st.subheader(value)
                st.write(category_string)

                skip_entities = False
                for key, value in zip(keys_to_check, keys_found):
                    if key == 'summary':
                        st.markdown(f"**:blue[{date}:]** :{sentiment_color}[{value}]")
                        if value == 'No summary available.' or value == 'Text could not be translated.':
                            skip_entities = True

                if not skip_entities:
                    for key, value in zip(keys_to_check, keys_found):
                        if key == 'disease_disorder':
                            st.write(f'Potential diseases: :{sentiment_color}[{value}]')
                        elif key == 'sign_symptom':
                            st.write(f'Potential symptoms: :{sentiment_color}[{value}]')
                        elif key == 'locations':
                            st.write(f'Potential locations: :{sentiment_color}[{value}]')
                        elif key == 'numeric_value':
                            st.write('Numeric entities: ')
                            table_data = pd.DataFrame([{'Number': entity_list[0], 'Related words': entity_list[1]} for entity_list in numeric_values_list])
                            table_date_without_index = table_data.style.hide(axis='index')
                            st.write(table_date_without_index.to_html(), unsafe_allow_html=True)
                            st.text('')

                st.write("Full article: ", article_links)

                with st.expander("See similar articles"):
                    for article_link in non_display_links:
                        st.markdown(f'- {article_link}')

                st.divider()
        except Exception as ex:
            logging.error(ex)
            continue

def main():

    st.set_page_config(page_title='Precision Health EBS', page_icon='favicon-32x32-1.png')

    title_style = '''
        <link href="https://db.onlinewebfonts.com/c/7ccc732353a266bee0d99b75cf08e134?family=Helvetica+83+Black+Extended" rel="stylesheet">
        <h1 style=
                "font-family: 'Helvetica 83 Black Extended';
                font-weight: bolder;
                font-stretch: ultra-expanded;
                color: #3687B6;">
            Precision Health
        </h1>
        <h1>Event Based Surveillance</h1>
    '''
    st.markdown(title_style, unsafe_allow_html=True)
    
    load_dotenv()

    try:
        processed_collection = str(os.environ.get("MONGODB_PROCESSED_COLLECTION"))
        mongodbhandler = MongoDBHandler(processed_collection)

        query = {
            'cluster_id': {
                '$exists': True
            },
            'display_document': {
                '$exists': True
            }
        }
        documents = list(mongodbhandler.read_data(query))

        st.write()

        col1, col2, _ = st.columns([3, 4.5, 8])
        
        with col1:
            st.write('Select date range: ')
        with col2:
            timespan = st.selectbox(
                "Select Timespan:", ['this week', 'this month', 'past 3 months', 'past 6 months', 'past 1 year', 'all time'],
                label_visibility='collapsed',
                disabled=False,
                key='articles_time_option'
            )
        
        filtered_documents = filter_documents(documents, timespan)
        sorted_documents = sort_and_display(filtered_documents)

        clustered_documents = group_documents_by_cluster(sorted_documents)

        display_clustered_documents(clustered_documents)
    except Exception as ex:
        logging.error(ex)

if __name__ == "__main__":
    main()
