import streamlit as st


st.title('Entity terminology:')
st.write('Symptoms- Refers to any symptoms of a disease identified in the text, such as “fever”, “cough”, etc.')
st.write('Diseases- Refers to the diseases identified in the text, such as “malaria”, “dengue”, etc.')
st.write('Locations- Refers to the geographic locations, names of cities, states, etc. identified in the text such as, “Lucknow”, “Jalandhar”, etc.')
st.write('Numeric values- Refers to numeric entities identified in the text which can be numbers, percentages, or qualitative descriptors such as “increasing”, “many”, etc.')
st.caption('**Note:** In the web application, all entity types are preceded with the word, “Potential” since although utmost care has been taken to ensure accuracy of the results, it is important to note that the results are computer-generated estimations and may not always be completely precise.')

st.divider()

st.title('Text color:')
st.write(':green[Green]: Indicates low severity, suggesting that the disease-related news has a relatively low impact or urgency.')
st.write(':orange[Orange]: Indicates moderate severity, implying that the disease-related news may have a significant impact or moderate urgency.')
st.write(':red[Red]: Indicates high severity, highlighting that the disease-related news is critical and requires immediate attention or action.')
st.caption('**Note:** The color-coded text is generated using a model that aims to classify disease news text based on severity. While the model has been designed with care and diligence, it is important to note that the results are computer-generated estimations. There might be instances where the model\'s performance may not accurately reflect the actual severity of the news due to the inherent complexities and variations in language.')