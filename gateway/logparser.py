import pandas as pd 
import re 


def log_csv_to_df(path, filtering_string=None): 
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

    # If we are filtering, only return subset of df 
    if filtering_string: 
        filter_string = filtering_string.replace("||", "|").replace("&&", "&")
        print(f"(logparser.py) Inputted filtering string: {filter_string}")
        
        filter_string = re.sub(r'\|\|', '|', filter_string)
        filter_string = re.sub(r'&&', '&', filter_string)

        mask = pd.Series(False, index=df.index)
        first_time = True 

        # Go through each boolean condition inputted 
        for condition in re.split(r'\||&', filter_string):
            condition = condition.strip()
            print(f" - Indiv condition: [{condition}]")

            in_pattern = r'(\S+)\s+in\s+(\S+)'
            eq_pattern = r'\s*(\S+)\s*==\s*(\S+)\s*'
            gr_pattern = r'\s*(\S+)\s*<\s*(\S+)\s*'
            lt_pattern = r'\s*(\S+)\s*>\s*(\S+)\s*'


            operator = [] 

            # Currently, only `in` and `==` are suppored 
            if re.match(in_pattern, condition):
                match = re.match(in_pattern, condition)
                operator = "in"
                print(f"   - Extracted operator: in")
            elif re.match(eq_pattern, condition):
                match = re.match(eq_pattern, condition)
                operator = "=="
                print(f"   - Extracted operator: ==")
            elif re.match(gr_pattern, condition):
                match = re.match(gr_pattern, condition)
                operator = "<"
                print(f"   - Extracted operator: <")
            elif re.match(lt_pattern, condition):
                match = re.match(lt_pattern, condition)
                operator = ">"
                print(f"   - Extracted operator: >")
            else:
                print(f"   - Invalid operator, breaking")
                break 
        
            print(f"   - Group 1: {match.group(1)}")
            print(f"   - Group 2: {match.group(2)}")


            # Defining the two possible condition formats
            if operator == "in": 
                cond_mask = f"df['{match.group(2)}'].str.contains('{str(match.group(1))}')"
            else: 
                cond_mask = f"df['{match.group(1)}'] {operator} {match.group(2)}"

            # Either and-ing or or-ing to df mask 
            if '&' in filter_string and not first_time:
                print("   - Anding condition:", cond_mask)
                mask &= eval(cond_mask)
                first_time = False
            else:
                print("   - Or-ing condition", cond_mask)
                mask |= eval(cond_mask)
                first_time = False 


        filtered_df = df[mask]
        print(f"(logparser.py) Filtered df length: {len(filtered_df)}")
        df = filtered_df

    return df 

