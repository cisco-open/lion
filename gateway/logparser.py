
#  Copyright 2024 Cisco Systems, Inc. and its affiliates
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

- def get_df_mask_from_filtering_string(df, filtering_string)
- def log_csv_to_df(path, filtering_string=None)

"""

import pandas as pd 
import re 


def get_df_mask_from_filtering_string(df, filtering_string): 

    """
    Filter rows in a DataFrame based on boolean expressions involving column titles.

    This function takes a DataFrame and a filtering string containing boolean expressions
    involving the DataFrame's column titles and returns a Boolean mask that can be used
    to filter rows that satisfy the conditions specified in the filtering string.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    filtering_string (str): A string containing boolean expressions involving column titles.
        Examples: "172.192.18.23 in Content || Pid == 24287", "LineId > 120 && LineId < 160".

    Returns:
    pd.Series: A Boolean mask with the same index as the DataFrame, indicating which rows
        satisfy the conditions in the filtering string.

    Example:
    >>> import pandas as pd
    >>> data = {'LineId': [100, 150, 130, 140, 160],
    ...         'Pid': [24287, 24287, 12345, 56789, 12345],
    ...         'Content': ['A', 'B', 'C', 'D', 'E']}
    >>> df = pd.DataFrame(data)
    >>> filtering_string = "LineId > 120 && LineId < 160 || Pid == 24287"
    >>> mask = get_df_mask_from_filtering_string(df, filtering_string)
    >>> filtered_df = df[mask]
    >>> print(filtered_df)
       LineId    Pid Content
    0     100  24287       A
    1     150  24287       B
    2     130  12345       C

    """

    filter_string = filtering_string.replace("||", "|").replace("&&", "&")
    print(f"(logparser.py) Inputted filtering string: {filter_string}")
    
    filter_string = re.sub(r'\|\|', '|', filter_string)
    filter_string = re.sub(r'&&', '&', filter_string)

    mask = pd.Series(False, index=df.index)
    first_time = True 

    # Go through each boolean condition inputted 
    for condition in re.split(r'\||&', filter_string):
        condition = condition.strip()

        in_pattern = r'(\S+)\s+in\s+(\S+)'
        eq_pattern = r'\s*(\S+)\s*==\s*(\S+)\s*'
        gr_pattern = r'\s*(\S+)\s*<\s*(\S+)\s*'
        lt_pattern = r'\s*(\S+)\s*>\s*(\S+)\s*'

        operator = [] 

        # Currently, only `in` and `==` are suppored 
        if re.match(in_pattern, condition):
            match = re.match(in_pattern, condition)
            operator = "in"
        elif re.match(eq_pattern, condition):
            match = re.match(eq_pattern, condition)
            operator = "=="
        elif re.match(gr_pattern, condition):
            match = re.match(gr_pattern, condition)
            operator = "<"
        elif re.match(lt_pattern, condition):
            match = re.match(lt_pattern, condition)
            operator = ">"
        else:
            break 

        # Defining the two possible condition formats
        if operator == "in": 
            cond_mask = f"df['{match.group(2)}'].str.contains('{str(match.group(1))}')"
        else: 
            cond_mask = f"df['{match.group(1)}'] {operator} {match.group(2)}"

        # Either and-ing or or-ing to df mask 
        if '&' in filter_string and not first_time:
            mask &= eval(cond_mask)
            first_time = False
        else:
            mask |= eval(cond_mask)
            first_time = False 
    
    return mask 



def log_csv_to_df(path, filtering_string=None): 

    """
    Reads a CSV log file into a DataFrame and performs optional filtering.

    This function reads a CSV log file into a DataFrame and performs optional filtering
    based on a provided filtering string containing boolean expressions involving column titles.

    Parameters:
    path (str): The file path to the CSV log file.
    filtering_string (str, optional): A string containing boolean expressions involving
        column titles for filtering the DataFrame. Default is None.

    Returns:
    pd.DataFrame: A DataFrame containing the log data with optional filtering applied.

    Example:
    >>> import pandas as pd
    >>> data = {'Date': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    ...         'Day': [1, 2, 3, 4, 5],
    ...         'Time': ['10:00:00', '11:15:00', '10:30:00', '12:45:00', '11:30:00']}
    >>> df = pd.DataFrame(data)
    >>> path = 'sample_log.csv'
    >>> filtering_string = "Day > 2"
    >>> log_df = log_csv_to_df(path, filtering_string)
    >>> print(log_df)
        Date  Day      Time            TimeFull
    2    Mar    3  10:30:00  03-03-2016 10:30:00
    3    Apr    4  12:45:00  04-04-2016 12:45:00
    4    May    5  11:30:00  05-05-2016 11:30:00

    """

    df = pd.read_csv(path)

    YEAR = 2016 # TODO: openssh.csv doesn't have an associated year
    month_dict = {'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4', 'May': '5', 'Jun': '6', 'Jul': '7', 'Aug': '8', 'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

    # Convert time into full timestamp (unified format: %d-%m-%Y %H:%M:%S)
    time_full = [] 
    for idx, entry in enumerate(df['Date']): 
        date_full = f"{df['Day'][idx]}-{month_dict[entry]}-{YEAR}" 
        time_full.append(pd.to_datetime(date_full + ' ' + df['Time'][idx], format='%d-%m-%Y %H:%M:%S'))
    df['TimeFull'] = time_full 

    # Delete these columns, as no longer needed
    df.drop(['Date', 'Day', 'Time'], axis=1, inplace=True)

    if filtering_string: 
        mask = get_df_mask_from_filtering_string(df, filtering_string)
        df = df[mask]

        print(f"(logparser.py) Filtered df length: {len(df)}")

    return df 

