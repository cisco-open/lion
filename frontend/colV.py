"""

This file contains: 

- def colV() {STREAMLIT}

"""

import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt


def get_histogram_given_col_title(df, title):

    """
    Generates a histogram plot for a specified column in the DataFrame.

    This function takes a DataFrame and the title of a column and generates a histogram plot
    for that specific column using Seaborn and Matplotlib.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    title (str): The title of the column for which the histogram is generated.

    Returns:
    matplotlib.figure.Figure: A Matplotlib Figure object representing the histogram plot.

    Example:
    >>> import pandas as pd
    >>> import streamlit as st
    >>> data = {'EventId': ['Event1', 'Event2', 'Event1', 'Event3', 'Event2'],
    ...         'Pid': [1, 2, 1, 3, 2]}
    >>> df = pd.DataFrame(data)
    >>> col_title = 'Pid'
    >>> fig = get_histogram_given_col_title(df, col_title)
    >>> st.pyplot(fig)

    """

    plt.figure(figsize=(10, 6))
    sns.histplot(df[title], bins=20, kde=True)
    return plt.gcf()  # Get the current Figure


def colV(): 
    st.title("Graph Analysis")
    df = st.session_state.demo_state['df']

    st.subheader(f'Histogram for Pid')
    fig = get_histogram_given_col_title(df, 'Pid')
    st.pyplot(fig)


    # Custom sorting function to extract the numeric part and convert it to an integer
    def custom_sort_key(event):
        return int(''.join(filter(str.isdigit, event)))

    # Sort the DataFrame based on the 'EventId' column using the custom key
    df['EventId'] = sorted(df['EventId'], key=custom_sort_key)

    st.subheader(f'Histogram for EventId')
    fig = get_histogram_given_col_title(df, 'EventId')
    st.pyplot(fig)


    if st.checkbox('Show DataFrame'):
        st.dataframe(df)
