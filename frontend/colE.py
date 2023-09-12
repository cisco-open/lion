import streamlit as st 
import matplotlib.pyplot as plt
import pandas as pd


# Column containing EventID table/freq count
def colE(): 

    """
    
    @Will 

    

    - Table of all template IDs (ex. E1, E2, etc) and how many times
    - Show what they are ^^ 

    Dataframe stored in: st.session_state.demo_state['df']

    st.table can take in dataframes (can see use in colR.py)
        
    """


    df = st.session_state.demo_state['df']


    # Extract the numeric part of 'EventId' and convert it to integers for sorting
    df['EventIdNumeric'] = df['EventId'].str.extract('(\d+)').astype(int)

    # Create a new DataFrame for unique Event IDs and their counts
    unique_events = df['EventId'].value_counts().reset_index()
    unique_events.columns = ['EventId', 'Count']

    # Add EventTemplate to the table
    unique_events['EventTemplate'] = unique_events['EventId'].map(df.drop_duplicates('EventId').set_index('EventId')['EventTemplate'])

    # Sort the unique event table by the numeric part of 'EventId'
    unique_events['EventIdNumeric'] = unique_events['EventId'].str.extract('(\d+)').astype(int)
    unique_events = unique_events.sort_values(by='EventIdNumeric')
    # Streamlit app
    st.title("Event Analysis")

    st.caption("These are all the event types and frequency counts we were able to extract from your log!")

    st.table(unique_events[['EventId', 'EventTemplate', 'Count']].reset_index(drop=True))


    # Display the modified unique event table
    #st.table(unique_events.set_index('EventId').rename_axis(None, axis=0))

    # Create histograms for each event type and display within the table

    col_list = unique_events['EventId']
    col_list = list(col_list)
    print("COL_LIST", col_list)

    tab_list = st.tabs(col_list)

    for idx, tab in enumerate(tab_list): 
        event_id = unique_events['EventId'][idx]
        event_id = col_list[idx]
        print("EVENT ID: ", event_id)
        subset = df[df['EventId'] == event_id]
        
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.hist(pd.to_datetime(subset['TimeFull']), bins=20, edgecolor='k')
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Time Histogram for Event {event_id}')
        ax.grid(True)
        
        tab.write(f"**Histogram for Event {event_id}:**")
        tab.pyplot(fig)