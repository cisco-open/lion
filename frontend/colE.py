
# Copyright 2022 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""

This file contains: 

- def extract_unique_events(df) 
- def generate_individual_timeseries_plot(df, event_id) 

- def colE() {STREAMLIT}

"""

import streamlit as st 
import matplotlib.pyplot as plt
import pandas as pd


def extract_unique_events(df): 
    
    """
    Extracts unique events from a DataFrame and provides additional information.

    This function takes a DataFrame containing event data, extracts unique events,
    and provides additional information about each unique event, including its count
    and associated event template.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing event data.

    Returns:
    pd.DataFrame: A DataFrame containing unique events with the following columns:
      - 'EventId': The unique event identifier.
      - 'Count': The number of occurrences of the unique event.
      - 'EventTemplate': The template associated with the unique event.
      - 'EventIdNumeric': The numeric part of 'EventId' used for sorting.

    Example:
    >>> import pandas as pd
    >>> data = {'EventId': ['Event1', 'Event2', 'Event1', 'Event3', 'Event2'],
    ...         'EventTemplate': ['TemplateA', 'TemplateB', 'TemplateA', 'TemplateC', 'TemplateB']}
    >>> df = pd.DataFrame(data)
    >>> result = extract_unique_events(df)
    >>> print(result)
       EventId  Count EventTemplate  EventIdNumeric
    0   Event1      2     TemplateA               1
    1   Event2      2     TemplateB               2
    2   Event3      1     TemplateC               3

    """

    df['EventIdNumeric'] = df['EventId'].str.extract('(\d+)').astype(int)

    unique_events = df['EventId'].value_counts().reset_index()
    unique_events.columns = ['EventId', 'Count']

    unique_events['EventTemplate'] = unique_events['EventId'].map(df.drop_duplicates('EventId').set_index('EventId')['EventTemplate'])
    unique_events['EventIdNumeric'] = unique_events['EventId'].str.extract('(\d+)').astype(int)
    
    unique_events = unique_events.sort_values(by='EventIdNumeric')
    return unique_events


def generate_individual_timeseries_plot(df, event_id): 

    """
    Generates a histogram plot of the time distribution for a specific event.

    This function takes a DataFrame containing time-series data and plots a histogram
    to visualize the time distribution of a specific event.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing time-series data.
    event_id (str): The unique identifier of the event for which the time histogram is generated.

    Returns:
    matplotlib.figure.Figure: A Matplotlib Figure object representing the histogram plot.

    Example:
    >>> import pandas as pd
    >>> import matplotlib.pyplot as plt
    >>> data = {'EventId': ['Event1', 'Event2', 'Event1', 'Event3', 'Event2'],
    ...         'TimeFull': ['2023-09-14 10:00:00', '2023-09-14 11:15:00',
    ...                      '2023-09-14 10:30:00', '2023-09-14 12:45:00',
    ...                      '2023-09-14 11:30:00']}
    >>> df = pd.DataFrame(data)
    >>> event_id = 'Event2'
    >>> fig = generate_individual_timeseries_plot(df, event_id)
    >>> plt.show()

    """

    subset = df[df['EventId'] == event_id]
    
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(pd.to_datetime(subset['TimeFull']), bins=20, edgecolor='k')
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Time Histogram for Event {event_id}')
    ax.grid(True)

    return fig 



""" Streamlit Component """

def colE(): 
    df = st.session_state.demo_state['df']
    unique_events = extract_unique_events(df) 

    st.title("Event Analysis")

    st.caption("These are all the event types and frequency counts we were able to extract from your log!")
    st.table(unique_events[['EventId', 'EventTemplate', 'Count']].reset_index(drop=True))


    col_list = list(unique_events['EventId'])
    tab_list = st.tabs(col_list)

    for idx, tab in enumerate(tab_list): 
        event_id = col_list[idx]
        tab.write(f"**Histogram for Event {event_id}:**")

        fig = generate_individual_timeseries_plot(df, event_id)
        tab.pyplot(fig)