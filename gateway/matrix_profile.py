"""

This file contains: 

- class MatrixProfileAnalyzer() 

  - def __init__(self, df)
  - def get_discords(self, k=4, windows=None, subset=None)
  - def get_motifs(self, k=4, subset=None)
  - def get_arr_subset(self, time_arr, event_arr, range)
  - def get_df_entries(self, target, window=5, after=False)
  - def plot_timeseries(self, dir)
  - def visualize_profile(self, profile, dir)

"""


import pandas as pd  
import numpy as np 
import matrixprofile as mp 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os 

plt.style.use('https://raw.githubusercontent.com/TDAmeritrade/stumpy/main/docs/stumpy.mplstyle')



class MatrixProfileAnalyzer: 

    """
    Initializes a MatrixProfileAnalyzer object with a DataFrame.

    This class represents a MatrixProfileAnalyzer, which is initialized with a DataFrame
    containing time-series and event data. It performs data validation and extracts
    relevant columns for further analysis.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the following columns:
        - 'TimeFull': Timestamps in the format '%d-%m-%Y %H:%M:%S'.
        - 'EventId': Unique event identifiers.
        - 'Content': Event content.

    Raises:
    AssertionError: If the DataFrame lacks required columns or if 'TimeFull' column format is incorrect.

    Example:
    >>> import pandas as pd
    >>> data = {'TimeFull': ['03-03-2016 10:30:00', '04-04-2016 12:45:00', '05-05-2016 11:30:00'],
    ...         'EventId': ['Event1', 'Event2', 'Event3'],
    ...         'Content': ['A', 'B', 'C']}
    >>> df = pd.DataFrame(data)
    >>> analyzer = MatrixProfileAnalyzer(df)
    
    """

    def __init__(self, df): 
        self.df = df 

        assert 'TimeFull' in df.columns, "DataFrame doesn't have 'TimeFull' column"
        assert pd.to_datetime(df['TimeFull'], format='%d-%m-%Y %H:%M:%S', errors='coerce').notna().all(), \
            "Column 'TimeFull' is not in the format '%d-%m-%Y %H:%M:%S'"
        assert 'EventId' in df.columns, "DataFrame doesn't have 'EventId' column"
        assert 'Content' in df.columns, "DataFrame doesn't have 'content' column"

        print(f"(matrix_profile.py) Dataframe is in correct format. Ready to go!")

        self.time_series = self.df['TimeFull']
        self.eventid_series = self.df['EventId']

        self.event_series = [] 
        for event in self.eventid_series: 
            self.event_series.append(int(str(event)[1:]))

        self.time_series = [np.datetime64(ts) for ts in self.time_series] # TODO: may not need this line!


    def get_discords(self, k=4, windows=None, subset=None): 

        """
        Extracts and returns MatrixProfile profile and discords.

        This method computes the MatrixProfile profile and identifies discords in the event series.
        Discords are subsequences that significantly differ from the rest and may indicate anomalies.

        Parameters:
        k (int, optional): The number of discords to identify. Default is 4.
        windows (list, optional): A list of window sizes for MatrixProfile computation. Default is None.
        subset (slice, optional): A slice indicating a subset of the event series to analyze. Default is None.

        Returns:
        dict or None: A dictionary containing the MatrixProfile profile and a list of discords if successful.
            Returns None if an error occurs (e.g., when the window size is too small).

        Example:
        >>> analyzer = MatrixProfileAnalyzer(df)
        >>> profile, discords = analyzer.get_discords(k=3, windows=[5, 10, 15])
        >>> if profile is not None:
        ...     print(f"MatrixProfile Profile: {profile['matrix_profile']}")
        ...     print(f"Discords: {discords}")

        """

        try: 
            exclusion_zone = int(len(self.event_series)/10)

            if windows: profile = mp.compute(self.event_series, windows)
            else: profile = mp.compute(self.event_series)

            profile = mp.discover.discords(profile, k=k, exclusion_zone=exclusion_zone)
            discords = profile['discords']
            return profile, discords
        
        except: 
            print("(matrix_profile.py) Error occured (likely window too small)")
            return None, None 


    def get_motifs(self, k=4, subset=None): 

        """
        Extracts and returns MatrixProfile profile and motifs.

        This method computes the MatrixProfile profile and identifies motifs in the event series.
        Motifs are subsequences that appear as repeating patterns within the data.

        Parameters:
        k (int, optional): The number of motifs to identify. Default is 4.
        subset (slice, optional): A slice indicating a subset of the event series to analyze. Default is None.

        Returns:
        dict or None: A dictionary containing the MatrixProfile profile and a list of motifs if successful.
            Returns None if an error occurs (e.g., when the window size is too small).

        Example:
        >>> analyzer = MatrixProfileAnalyzer(df)
        >>> profile, motifs = analyzer.get_motifs(k=3)
        >>> if profile is not None:
        ...     print(f"MatrixProfile Profile: {profile['matrix_profile']}")
        ...     print(f"Motifs: {motifs}")

        """
        try: 
            profile = mp.compute(self.event_series)
            profile = mp.discover.motifs(profile, k=k)

            motifs = profile['motifs']
            return profile, motifs
    
        except: 
            print("(matrix_profile.py) Error occured (likely window too small)")
            return None, None 


    def get_arr_subset(self, time_arr, event_arr, range): 

        """
        Returns a subset of event_arr contingent on time_arr and a time range.

        This method extracts a subset of event_arr based on the corresponding time_arr and a specified
        time range defined by start_time and end_time.

        Parameters:
        time_arr (list or pd.Series): A list or Series containing timestamps.
        event_arr (list or pd.Series): A list or Series containing event data.
        time_range (tuple): A tuple specifying the time range as (start_time, end_time).

        Returns:
        list: A subset of event_arr within the specified time range.

        Example:
        >>> analyzer = MatrixProfileAnalyzer(df)
        >>> time_series = ['03-03-2016 10:00:00', '03-03-2016 11:00:00', '04-04-2016 10:30:00', '05-05-2016 11:30:00']
        >>> event_series = ['Event1', 'Event2', 'Event3', 'Event4']
        >>> time_range = ('03-03-2016 10:00:00', '04-04-2016 11:00:00')
        >>> subset = analyzer.get_arr_subset(time_series, event_series, time_range)
        >>> print(subset)
        ['Event1', 'Event2']

        In this example, the method is used to extract a subset of 'event_series' within the specified
        time range, resulting in ['Event1', 'Event2'].

        """

        start_time = range[0]; end_time = range[1]

        subset = [] 
        for idx, timestamp in enumerate(time_arr): 
            if start_time <= timestamp <= end_time:
                subset.append(event_arr[idx])

        return subset
        

    def get_df_entries(self, target, window=5, after=False):

        """
        Retrieves a slice of the DataFrame centered around or starting at a specified target index.

        This method extracts a slice of the DataFrame with entries centered around the specified
        target index or starting at the target index if 'after' is set to True.

        Parameters:
        target (int): The target index around which the slice is extracted.
        window (int, optional): The size of the window around the target index. Default is 5.
        after (bool, optional): If True, the slice starts at the target index; if False, it is centered
            around the target index. Default is False.

        Returns:
        pd.DataFrame: A slice of the DataFrame containing entries within the specified window.

        Example:
        >>> analyzer = MatrixProfileAnalyzer(df)
        >>> target_index = 3
        >>> window_size = 2
        >>> after_target = False
        >>> window_entries = analyzer.get_df_entries(target_index, window_size, after_target)
        >>> print(window_entries)
           TimeFull  EventId Content
        1  03-03-2016 11:00:00  Event2       B
        2  04-04-2016 10:30:00  Event3       C
        3  05-05-2016 11:30:00  Event4       D

        In this example, the method extracts a DataFrame slice centered around index 3
        with a window size of 2, resulting in entries from index 1 to 3.

        """

        print(f"(matrix_profile.py) Extracting entry at index {target}")

        if not after: 
            start_idx = max(0, target - window)
            end_idx = min(len(self.df) - 1, target + window)
        else: 
            start_idx = target 
            end_idx = min(len(self.df) - 1, target + window)
        
        # Slice the DataFrame to get the entries within the window
        window_entries = self.df.iloc[start_idx:end_idx + 1]  # Adding 1 to include the end index
        
        return window_entries


    def plot_timeseries(self, dir): 

        """
        Generates and saves a timeseries plot of df["EventId] vs df["TimeFull].

        This method creates a timeseries plot of event IDs against timestamps and saves
        it as an image in the specified directory.

        Parameters:
        dir (str): The directory where the timeseries plot image will be saved.

        Returns:
        None

        Example:
        >>> analyzer = MatrixProfileAnalyzer(df)
        >>> output_directory = 'plots'
        >>> analyzer.plot_timeseries(output_directory)

        In this example, the method generates a timeseries plot of event IDs against timestamps
        and saves it as an image in the 'plots' directory.

        """

        plt.figure(figsize=(20, 4))  # Adjust the figure size as needed

        plt.plot(self.time_series, self.event_series, marker='o', linestyle='-', color='b', markersize=8)

        plt.xlabel('Timestamp')
        plt.ylabel('Event ID')
        plt.title('Timestamps vs. Event IDs')

        plt.xticks(rotation=45)
        plt.xlim(min(self.time_series), max(self.time_series))

        plt.grid()
        plt.tight_layout()
        plt.savefig(os.path.join(dir, "timeseries.png"))


    def visualize_profile(self, profile, dir): 

        """
        Dumps MatrixProfile figures into the specified directory.

        This method generates and saves visualizations of the MatrixProfile into the specified
        directory. Each figure represents a different aspect of the MatrixProfile analysis.

        Parameters:
        profile (dict): A dictionary containing the MatrixProfile and related information.
        dir (str): The directory where the profile figures will be saved.

        Returns:
        None

        Example:
        >>> analyzer = MatrixProfileAnalyzer(df)
        >>> profile, _ = analyzer.get_discords(k=3)
        >>> output_directory = 'profile_visualizations'
        >>> analyzer.visualize_profile(profile, output_directory)

        In this example, the method generates visualizations of the MatrixProfile analysis results
        and saves them in the 'profile_visualizations' directory.

        """

        if not os.path.exists(dir): os.makedirs(dir)

        figures = mp.visualize(profile)
        for count, figure in enumerate(figures):
            figure.savefig(os.path.join(dir, '{}.png'.format(count)))
