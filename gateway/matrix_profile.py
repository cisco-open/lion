import pandas as pd  
import numpy as np 
import matrixprofile as mp 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os 

plt.style.use('https://raw.githubusercontent.com/TDAmeritrade/stumpy/main/docs/stumpy.mplstyle')



class MatrixProfileAnalyzer(): 

    """ Initializes time_series and event_series based on inputted dataframe """

    def __init__(self, df): 
        self.df = df 

        assert 'TimeFull' in df.columns, "DataFrame doesn't have 'TimeFull' column"

        assert pd.to_datetime(df['TimeFull'], format='%d-%m-%Y %H:%M:%S', errors='coerce').notna().all(), \
            "Column 'TimeFull' is not in the format '%d-%m-%Y %H:%M:%S'"

        # Assert that 'EventId' and 'content' columns exist
        assert 'EventId' in df.columns, "DataFrame doesn't have 'EventId' column"
        assert 'Content' in df.columns, "DataFrame doesn't have 'content' column"

        print(f"(matrix_profile.py) Dataframe is in correct format. Ready to go!")

        self.time_series = self.df['TimeFull']
        self.eventid_series = self.df['EventId']

        self.event_series = [] 
        for event in self.eventid_series: 
            self.event_series.append(int(str(event)[1:]))

        self.time_series = [np.datetime64(ts) for ts in self.time_series] # TODO: may not need this line!


    """ Extracts and returns profile and discords (may fail if len(df) is too small) """

    def get_discords(self, k=3, windows=None, subset=None): 
        try: 
            if windows: profile = mp.compute(self.event_series, windows)
            else: profile = mp.compute(self.event_series)

            profile = mp.discover.discords(profile, k=k)
            discords = profile['discords']

            return profile, discords
        
        except: 
            print("(matrix_profile.py) Error occured (likely window too small)")
            return None, None 


    """ Extracts and returns profile and motifs (may fail if len(df) is too small) """

    def get_motifs(self, subset=None): 
        try: 
            profile = mp.compute(self.event_series)
            profile = mp.discover.motifs(profile)

            motifs = profile['motifs']
            return profile, motifs
    
        except: 
            print("(matrix_profile.py) Error occured (likely window too small)")
            return None, None 


    """ Returns subset of event_arr contingent on time_arr and range of time """

    def get_arr_subset(self, time_arr, event_arr, range): 
        start_time = range[0]; end_time = range[1]

        subset = [] 
        for idx, timestamp in enumerate(time_arr): 
            if start_time <= timestamp <= end_time:
                subset.append(event_arr[idx])

        return subset
        

    """ Retrieves slice of dataframe (either w/ target in middle, or at start) """

    def get_df_entries(self, target, window=5, after=False): 
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


    """ Generates and saves timeseries plot of df["EventId] vs df["TimeFull] """

    def plot_timeseries(self, dir): 
        plt.figure(figsize=(20, 4))  # Adjust the figure size as needed

        plt.plot(self.time_series, self.event_series, marker='o', linestyle='-', color='b', markersize=8)

        plt.xlabel('Timestamp')
        plt.ylabel('Event ID')
        plt.title('Timestamps vs. Event IDs')

        plt.xticks(rotation=45)
        plt.xlim(min(self.time_series), max(self.time_series))

        #print(f"Logs range from: {min(self.time_series)} to {max(self.time_series)}")

        plt.grid()
        plt.tight_layout()
        plt.savefig(os.path.join(dir, "timeseries.png"))


    """ Dumps profile figures into specified directory """

    def visualize_profile(self, profile, dir): 
        if not os.path.exists(dir): os.makedirs(dir)

        figures = mp.visualize(profile)
        for count, figure in enumerate(figures):
            figure.savefig(os.path.join(dir, '{}.png'.format(count)))
