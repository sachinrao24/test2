import streamlit as st
import numpy as np
import pandas as pd

df = pd.read_csv('rag_results.csv')
data = []

for index, row in df.iterrows():
    container = st.container(border=True)

    title = row['title']
    text = row['text']
    with container:

        st.subheader(title)
        st.write(text)

        st.subheader('Keyword Search Results')
        st.markdown(f':blue[{row['keyword search response']}]')

        with st.expander("See classification basis: "):
            st.write(f"**Relevant Text 1**: {row['keyword source node 1']}")
            # st.write(f"Similarity Score: {round(int(row['keyword source node 1 similarity score']), 2)}")
            if not type(row['keyword source node 2']) == float:
                st.write(f"**Relevant Text 2**: {row['keyword source node 2']}")
                # st.write(f"Similarity Score: {round(int(row['keyword source node 2 similarity score']), 2)}")


        st.subheader('Vector Search Results')
        st.markdown(f':blue[{row['vector search response']}]')
        with st.expander("See classification basis: "):
            st.write(f"Relevant Text 1: {row['vector source node 1']}")
            st.write(f"Similarity Score: {np.round(float(row['vector source node 1 similarity score']), 2)}")
            st.write(f"Relevant Text 2: {row['vector source node 2']}")
            st.write(f"Similarity Score: {np.round(float(row['vector source node 2 similarity score']), 2)}")

        st.write("Select the accurate classification: ")
        keyword_checkbox = st.checkbox("Keyword search", key=f"keyword_checkbox_{index}")
        vector_checkbox = st.checkbox("Vector search", key=f"vector_checkbox_{index}")
        both_checkbox = st.checkbox("Both", key=f"both_checkbox_{index}")
        neither_checkbox = st.checkbox("Neither (Mention reason)", key=f"neither_checkbox_{index}")
        neither_reason = st.text_input("If neither are relevant, please mention the reason:", key=f"text_input_{index}")

        data.append({
            'index': index,
            'title': title,
            # 'text': text,
            'Keyword search': keyword_checkbox,
            'Vector search': vector_checkbox,
            'Both': both_checkbox,
            'Neither': neither_checkbox,
            'Reason': neither_reason
        })

df = pd.DataFrame(data)

st.write("Collected Data:")
st.dataframe(df)

csv = df.to_csv(index=False)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='user_feedback_data.csv',
    mime='text/csv',
)