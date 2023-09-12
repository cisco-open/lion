import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# import warnings
# warnings.filterwarnings("ignore")

# Column containing variable comparison (enter IP address)
def colV(): 

    """
    
    @

    - Add more graphs (ex. timeseries, motif, discord) to Streamlit 
    - Potentially selectable (if we select a parameter, display)
    - Ex. Input: 
    - "IP: 123.235.32.19" --> graphs specific to that ID 
    - Can do two things side by side for multiple IPs

    Dataframe stored in: st.session_state.demo_state['df']

    st.table can take in dataframes (can see use in colR.py)
        
    """

    st.title("Graph Analysis")

    df = st.session_state.demo_state['df']

    st.subheader(f'Histogram for Pid')
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Pid'], bins=20, kde=True)
    st.pyplot()

    # Custom sorting function to extract the numeric part and convert it to an integer
    def custom_sort_key(event):
        return int(''.join(filter(str.isdigit, event)))

    # Sort the DataFrame based on the 'EventId' column using the custom key
    df['EventId'] = sorted(df['EventId'], key=custom_sort_key)


    st.subheader(f'Histogram for EventId')
    plt.figure(figsize=(10, 6))
    sns.histplot(df['EventId'], bins=20, kde=True)
    st.pyplot()


    if st.checkbox('Show DataFrame'):
        st.dataframe(df)
