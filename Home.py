import streamlit as st
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
sys.path.insert(1, 'Pipeline/')
from handlers.MongoDBHandler import MongoDBHandler

def sort_and_display(documents):
    st.divider()

    try:
        # Convert the date format for sorting
        documents = [doc for doc in documents if ('date' in doc and type(doc['date']) == str)]
        for doc in documents:
            doc['date'] = datetime.strptime(doc['date'], '%d/%m/%Y')
            doc['date'] = doc['date'].strftime('%d-%B-%Y')
            doc['datetime_object'] = datetime.strptime(doc['date'], '%d-%B-%Y').date()

        # Sort the documents in descending order by the 'date' key
        sorted_documents = sorted(documents, key=lambda x: x['datetime_object'], reverse=True)

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
            
            keys_to_check = ['sign_symptom', 'disease_disorder', 'locations', 'lab_value', 'summary', 'title']
            keys_found = []
            not_found_messages = {
                'summary': "No summary available.",
                'disease_disorder': "No diseases found.",
                'sign_symptom': "No symptoms found.",
                'locations': "No locations found.",
                'lab_value': "No numeric entities found.",
                'title': "No title found."
            }

            for key in keys_to_check:
                if key in doc:
                    if isNaN(doc[key]):
                        keys_found.append(not_found_messages.get(key))
                    else:
                        if key in ['disease_disorder', 'locations', 'sign_symptom', 'lab_value'] and type(doc[key]) == list:
                            if len(doc[key]) > 0:
                                doc[key] = set(doc[key])
                            else:
                                keys_found.append(not_found_messages.get(key))
                                continue
                        keys_found.append(str(doc[key]).strip('[]').strip('{}'))
                else:
                    keys_found.append(not_found_messages.get(key))
                
            for key, value in zip(keys_to_check, keys_found):
                if key == 'title':
                    st.subheader(value)
            st.write(category_string)

            for key, value in zip(keys_to_check, keys_found):
                if key == 'summary':
                    st.markdown(f"**:blue[{date}:]** :{sentiment_color}[{value}]")
            
            for key, value in zip(keys_to_check, keys_found):
                if key == 'disease_disorder':
                    st.write(f'Potential diseases: :{sentiment_color}[{value}]')
                elif key == 'sign_symptom':
                    st.write(f'Potential symptoms: :{sentiment_color}[{value}]')
                elif key == 'locations':
                    st.write(f'Potential locations: :{sentiment_color}[{value}]')
                elif key == 'lab_value':
                    st.write(f'Numeric values: :{sentiment_color}[{value}]')

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

    sort_and_display(documents)

if __name__ == "__main__":
    main()