# import streamlit as st
# from datetime import datetime, timedelta
# import pandas as pd
# from dateutil.relativedelta import relativedelta
# import logging
# from dotenv import load_dotenv
# import os
# import sys
# sys.path.insert(1, 'Pipeline/')
# from handlers.MongoDBHandler import MongoDBHandler

# def filter_documents(documents, timespan):
#     filtered_documents = []  # Initialize an empty list to store filtered documents
    
#     for doc in documents:
#         if isinstance(doc['date'], str):  # Use isinstance() instead of type()
#             try:
#                 doc['datetime_object'] = datetime.strptime(doc['date'], '%d/%m/%Y')
#             except Exception as ex:
#                 logging.error(ex)
    
#     try:
#         if timespan == 'this month':
#             start_date = datetime.now().replace(day=1)
#         elif timespan == 'past 3 months':
#             start_date = datetime.now() - relativedelta(months=3)
#         elif timespan == 'past 6 months':
#             start_date = datetime.now() - relativedelta(months=6)
#         elif timespan == 'past 1 year':
#             start_date = datetime.now() - relativedelta(years=1)
        
#         if start_date:
#             filtered_documents = [doc for doc in documents if ('datetime_object' in doc and doc['datetime_object'] >= start_date)]
#     except Exception as ex:
#         logging.error(ex)
    
#     return filtered_documents

# def sort_and_display(documents):
#     sorted_documents = []
#     st.divider()

#     try:
#         # Convert the date format for sorting
#         documents = [doc for doc in documents if ('date' in doc and 'sentiment_score' in doc and type(doc['date']) == str)]
#         for doc in documents:
#             try:
#                 doc['date'] = datetime.strptime(doc['date'], '%d/%m/%Y')
#                 doc['date'] = doc['date'].strftime('%d-%B-%Y')
#                 doc['datetime_object'] = datetime.strptime(doc['date'], '%d-%B-%Y').date()
#             except Exception as ex:
#                 logging.error(ex)

#         # Sort the documents in descending order by the 'date' key
#         sorted_documents = sorted(documents, key=lambda x: (x['datetime_object'], x['sentiment_score']), reverse=True)

#     except Exception as ex:
#             logging.error(ex)
    
#     def isNaN(string):
#         return (string != string)

#     for doc in sorted_documents:
#         try:
#             if 'category' not in doc or 'date' not in doc:
#                 continue
#             if type(doc['date']) != str:
#                 continue

#             date = doc['date']
#             article_links = doc['article_links']
#             try:
#                 sentiment_color = doc['sentiment_color']
#             except:
#                 continue
#             category_key = doc['category']
#             category_string='Categories: '

#             if isinstance(category_key, str):
#                 category_string += category_key
#             elif isinstance(category_key, list):
#                 category_string += str(category_key).strip('[]').replace("'", "")
            
#             keys_to_check = ['sign_symptom', 'disease_disorder', 'locations', 'numeric_value', 'summary', 'title']
#             keys_found = []
#             not_found_messages = {
#                 'summary': "No summary available.",
#                 'disease_disorder': "No diseases found.",
#                 'sign_symptom': "No symptoms found.",
#                 'locations': "No locations found.",
#                 'numeric_value': "No numeric entities found.",
#                 'title': "No title found."
#             }

#             for key in keys_to_check:
#                 if key in doc:
#                     if isNaN(doc[key]):
#                         keys_found.append(not_found_messages.get(key))
#                     else:
#                         if key in ['disease_disorder', 'locations', 'sign_symptom', 'numeric_value'] and type(doc[key]) == list:
#                             if len(doc[key]) > 0:
#                                 doc[key] = set(doc[key])
#                                 if key == 'numeric_value':
#                                     numeric_values_list = []
#                                     value = doc[key]
#                                     for entity in value:
#                                         number_and_qualifying_words = entity.split(': ')
#                                         numeric_values_list.append(number_and_qualifying_words)
#                             else:
#                                 keys_found.append(not_found_messages.get(key))
#                                 continue
#                         if key == 'numeric_value':
#                             keys_found.append(numeric_values_list)
#                         else:
#                             keys_found.append(str(doc[key]).strip('[]').strip('{}'))
#                 else:
#                     keys_found.append(not_found_messages.get(key))
                
#             for key, value in zip(keys_to_check, keys_found):
#                 if key == 'title':
#                     st.subheader(value)
#             st.write(category_string)

#             skip_entities = False
#             for key, value in zip(keys_to_check, keys_found):
#                 if key == 'summary':
#                     st.markdown(f"**:blue[{date}:]** :{sentiment_color}[{value}]")
#                     if value == 'No summary available.' or value == 'Text could not be translated.':
#                         skip_entities = True

#             if not skip_entities:
#                 for key, value in zip(keys_to_check, keys_found):
#                     if key == 'disease_disorder':
#                         st.write(f'Potential diseases: :{sentiment_color}[{value}]')
#                     elif key == 'sign_symptom':
#                         st.write(f'Potential symptoms: :{sentiment_color}[{value}]')
#                     elif key == 'locations':
#                         st.write(f'Potential locations: :{sentiment_color}[{value}]')
#                     elif key == 'numeric_value':
#                         st.write('Numeric entities: ')
#                         table_data = pd.DataFrame([{'Number': entity_list[0], 'Related words': entity_list[1]} for entity_list in numeric_values_list])
#                         table_date_without_index = table_data.style.hide(axis='index')
#                         st.write(table_date_without_index.to_html(), unsafe_allow_html=True)
#                         st.text('')
                        
#             st.write("Full article: ", article_links)

#             st.divider()
#         except Exception as ex:
#             logging.error(ex)
#             continue

# def main():
#     st.title("**:violet[Precision Health]**")
#     st.title("Event Based Surveillance")

#     load_dotenv()
#     processed_collection = str(os.environ.get("MONGODB_PROCESSED_COLLECTION"))
#     mongodbhandler = MongoDBHandler(processed_collection)

#     documents = list(mongodbhandler.read_data())

#     st.write()

#     col1, col2, _ = st.columns([3, 4.5, 8])
    
#     with col1:
#         st.write('Select date range: ')
#     with col2:
#         timespan = st.selectbox(
#             "Select Timespan:", ['this month', 'past 3 months', 'past 6 months', 'past 1 year', 'all time'],
#             label_visibility='collapsed',
#             disabled=False,
#             key='articles_time_option'
#         )
#     filtered_documents = filter_documents(documents, timespan)

#     sort_and_display(filtered_documents)

# if __name__ == "__main__":
#     main()

import streamlit as st
from datetime import datetime, timedelta
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
        if timespan == 'this month':
            start_date = datetime.now().replace(day=1)
        elif timespan == 'past 3 months':
            start_date = datetime.now() - relativedelta(months=3)
        elif timespan == 'past 6 months':
            start_date = datetime.now() - relativedelta(months=6)
        elif timespan == 'past 1 year':
            start_date = datetime.now() - relativedelta(years=1)
        
        if start_date:
            filtered_documents = [doc for doc in documents if ('datetime_object' in doc and doc['datetime_object'] >= start_date)]
    except Exception as ex:
        logging.error(ex)
    
    return filtered_documents

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

    for doc in sorted_documents:
        try:
            if 'category' not in doc or 'date' not in doc:
                continue
            if type(doc['date']) != str:
                continue

            date = doc['date']
            article_links = doc['article_links']
            try:
                sentiment_color = doc['sentiment_color']
            except:
                continue
            category_key = doc['category']
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

            for key in keys_to_check:
                if key in doc:
                    if isNaN(doc[key]):
                        keys_found.append(not_found_messages.get(key))
                    else:
                        if key in ['disease_disorder', 'locations', 'sign_symptom', 'numeric_value'] and type(doc[key]) == list:
                            if len(doc[key]) > 0:
                                doc[key] = set(doc[key])
                                if key == 'numeric_value':
                                    numeric_values_list = []
                                    value = doc[key]
                                    for entity in value:
                                        number_and_qualifying_words = entity.split(': ')
                                        numeric_values_list.append(number_and_qualifying_words)
                            else:
                                keys_found.append(not_found_messages.get(key))
                                continue
                        if key == 'numeric_value':
                            keys_found.append(numeric_values_list)
                        else:
                            keys_found.append(str(doc[key]).strip('[]').strip('{}'))
                else:
                    keys_found.append(not_found_messages.get(key))
                
            skip_doc = False
            for key, value in zip(keys_to_check, keys_found):
                if key == 'summary':
                    # st.markdown(f"**:blue[{date}:]** :{sentiment_color}[{value}]")
                    if value == 'No summary available.' or value == 'Text could not be translated.':
                        skip_doc = True
            
            if skip_doc:
                continue
            else:
                for key, value in zip(keys_to_check, keys_found):
                    if key == 'title':
                        st.subheader(value)
                st.write(category_string)

                skip_entities = False
                for key, value in zip(keys_to_check, keys_found):
                    if key == 'summary':
                        # st.markdown(f"**:blue[{date}:]** :{sentiment_color}[{value}]")
                        if value == 'No summary available.' or value == 'Text could not be translated.':
                            pass
                            # skip_entities = True

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

                st.divider()
        except Exception as ex:
            logging.error(ex)
            continue

def main():
    st.title("**:violet[Precision Health]**")
    st.title("Event Based Surveillance")

    load_dotenv()
    processed_collection = str(os.environ.get("MONGODB_PROCESSED_COLLECTION"))
    mongodbhandler = MongoDBHandler(processed_collection)

    documents = list(mongodbhandler.read_data())

    st.write()

    col1, col2, _ = st.columns([3, 4.5, 8])
    
    with col1:
        st.write('Select date range: ')
    with col2:
        timespan = st.selectbox(
            "Select Timespan:", ['this month', 'past 3 months', 'past 6 months', 'past 1 year', 'all time'],
            label_visibility='collapsed',
            disabled=False,
            key='articles_time_option'
        )
    filtered_documents = filter_documents(documents, timespan)

    sort_and_display(filtered_documents)

if __name__ == "__main__":
    main()
