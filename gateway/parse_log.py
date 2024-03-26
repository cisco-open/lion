
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

import os
import pandas as pd
from drain3 import TemplateMiner
from dateutil import parser
import time
import csv
import re
import time
import concurrent.futures
from functools import partial
import multiprocessing

log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'


def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        print(time.time()-start_time)
    return wrapper



def get_log_format(filename):
    benchmark_settings = {
        "HDFS": {
            "log_format": "<Date> <Time> <Pid> <Level> <Component>: <Content>",
            "regex": [r"blk_-?\d+", r"(\d+\.){3}\d+(:\d+)?"],
            "st": 0.5,
            "depth": 4,
        },
        "Hadoop": {
            "log_format": "<Date> <Time> <Level> \[<Process>\] <Component>: <Content>",
            "regex": [r"(\d+\.){3}\d+"],
            "st": 0.5,
            "depth": 4,
        },
        "Spark": {
            "log_format": "<Date> <Time> <Level> <Component>: <Content>",
            "regex": [r"(\d+\.){3}\d+", r"\b[KGTM]?B\b", r"([\w-]+\.){2,}[\w-]+"],
            "st": 0.5,
            "depth": 4,
        },
        "Zookeeper": {
            "log_format": "<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>",
            "regex": [r"(/|)(\d+\.){3}\d+(:\d+)?"],
            "st": 0.5,
            "depth": 4,
        },
        "BGL": {
            "log_file": "BGL/BGL_2k.log",
            "log_format": "<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>",
            "regex": [r"core\.\d+"],
            "st": 0.5,
            "depth": 4,
        },
        "HPC": {
            "log_file": "HPC/HPC_2k.log",
            "log_format": "<LogId> <Node> <Component> <State> <Time> <Flag> <Content>",
            "regex": [r"=\d+"],
            "st": 0.5,
            "depth": 4,
        },
        "Thunderbird": {
            "log_file": "Thunderbird/Thunderbird_2k.log",
            "log_format": "<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>",
            "regex": [r"(\d+\.){3}\d+"],
            "st": 0.5,
            "depth": 4,
        },
        "Windows": {
            "log_file": "Windows/Windows_2k.log",
            "log_format": "<Date> <Time>, <Level>                  <Component>    <Content>",
            "regex": [r"0x.*?\s"],
            "st": 0.7,
            "depth": 5,
        },
        "Linux": {
            "log_file": "Linux/Linux_2k.log",
            "log_format": "<Month> <Date> <Time> <Level> <Component>(\[<PID>\])?: <Content>",
            "regex": [r"(\d+\.){3}\d+", r"\d{2}:\d{2}:\d{2}"],
            "st": 0.39,
            "depth": 6,
        },
    "Android": {
        "log_file": "Android/Android_2k.log",
        "log_format": "<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>",
        "regex": [
            r"(/[\w-]+)+",
            r"([\w-]+\.){2,}[\w-]+",
            r"\b(\-?\+?\d+)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b",
        ],
        "st": 0.2,
        "depth": 6,
    },
    "HealthApp": {
        "log_file": "HealthApp/HealthApp_2k.log",
        "log_format": "<Time>\|<Component>\|<Pid>\|<Content>",
        "regex": [],
        "st": 0.2,
        "depth": 4,
    },
    "Apache": {
        "log_file": "Apache/Apache_2k.log",
        "log_format": "\[<Time>\] \[<Level>\] <Content>",
        "regex": [r"(\d+\.){3}\d+"],
        "st": 0.5,
        "depth": 4,
    },
    "Proxifier": {
        "log_file": "Proxifier/Proxifier_2k.log",
        "log_format": "\[<Time>\] <Program> - <Content>",
        "regex": [
            r"<\d+\ssec",
            r"([\w-]+\.)+[\w-]+(:\d+)?",
            r"\d{2}:\d{2}(:\d{2})*",
            r"[KGTM]B",
        ],
        "st": 0.6,
        "depth": 3,
    },
    "OpenSSH": {
        "log_file": "OpenSSH/OpenSSH_2sk.log",
        "log_format": "<Date> <Day> <Time> <Component> sshd\[<Pid>\]: <Content>",
        "regex": [r"(\d+\.){3}\d+", r"([\w-]+\.){2,}[\w-]+"],
        "st": 0.6,
        "depth": 5,
    },
    "OpenStack": {
        "log_file": "OpenStack/OpenStack_2k.log",
        "log_format": "<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>",
        "regex": [r"((\d+\.){3}\d+,?)+", r"/.+?\s", r"\d+"],
        "st": 0.5,
        "depth": 5,
    },
    "Mac": {
        "log_file": "Mac/Mac_2k.log",
        "log_format": "<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>",
        "regex": [r"([\w-]+\.){2,}[\w-]+"],
        "st": 0.7,
        "depth": 6,
    },
    }
    for key in benchmark_settings:
        if re.search(rf'{key}(?=[_\W]|$)', filename):
            return benchmark_settings[key]["log_format"]

    print("Unable to find the logformat ! This can lead to errors please take care of this:")
    return None

def detect_timestamp_format(log_line):
    # This function tries to detect the timestamp format from the log line
    # For simplicity, we assume the timestamp is at the beginning of the log line
    # You can extend this function to handle more timestamp formats
    try:
        timestamp_str = log_line.split()[0]
        timestamp = parser.parse(timestamp_str)
        return timestamp
    except:
        return None

def generate_logformat_regex(logformat):
        """ Function to generate regular expression to split log messages
        """
        headers = []
        splitters = re.split(r'(<[^<>]+>)', logformat)
        regex = ''
        for k in range(len(splitters)):
            if k % 2 == 0:
                splitter = re.sub(' +', '\\\s+', splitters[k])
                regex += splitter
            else:
                header = splitters[k].strip('<').strip('>')
                regex += '(?P<%s>.*?)' % header
                headers.append(header)
        regex = re.compile('^' + regex + '$')
        return headers, regex

def get_parameter_list(template, input_string):
    # Replace placeholders with a unique string
    template_regex = re.sub(r"<.{1,5}>", "PLACEHOLDER", template)

    # Escape special characters
    template_regex = re.sub(r'([^A-Za-z0-9])', r'\\\1', template_regex)

    # Replace the unique string with the capturing group
    template_regex = "^" + template_regex.replace("PLACEHOLDER", "(.*?)") + "$"

        # Extract parameters
        #input_string = row["Content"]

    match_objects = list(re.finditer(template_regex, input_string))

        # Extract preceding words for each match and combine
    preceding_combined_corrected = []
    for match_obj in match_objects:
        for group_num in range(1, len(match_obj.groups()) + 1):
            pos = match_obj.span(group_num)
            preceding_match = re.search(r"([^\s]+)[\s,'-','_']*$", input_string[:pos[0]])
            preceding_chars = preceding_match.group(1) if preceding_match else ""
            matched_value = match_obj.group(group_num)
            preceding_combined_corrected.append(preceding_chars + matched_value)
      
    return preceding_combined_corrected

def get_parameter_list_generic(template, input_string):
    # Convert placeholders into a unique string
    template_regex = re.sub(r"<.{1,5}>", "PLACEHOLDER", template)
    
    # Escape special characters and replace the unique string with a capturing group
    template_regex = re.escape(template_regex).replace("PLACEHOLDER", "(.*?)")
    
    # Make the pattern flexible for spaces, underscores, and hyphens
    template_regex = template_regex.replace("\\ ", "[\\s_-]+")
    template_regex = "^" + template_regex + "$"
    
    # Extract parameters
    match_objects = list(re.finditer(template_regex, input_string))
    
    # Lists to hold the results
    parameters_without_preceding = []
    parameters_with_preceding = []
    
    for match_obj in match_objects:
        for group_num in range(1, len(match_obj.groups()) + 1):
            pos = match_obj.span(group_num)
            preceding_match = re.search(r"([^\s]+)\s*$", input_string[:pos[0]])
            preceding_chars = preceding_match.group(1) if preceding_match else ""
            matched_value = match_obj.group(group_num)
            
            parameters_without_preceding.append(matched_value)
            parameters_with_preceding.append(preceding_chars + matched_value)
      
    return parameters_without_preceding, parameters_with_preceding
    


def parse_log_chunk(chunk, pattern, headers, first_unix_time, template_miner):
    # Initialize the template miner
    # template_miner = TemplateMiner()

    timestamps, pids, processes, log_texts, event_templates, original_logs, unix_times, parameters, parameters_wo, normalized_timestamps = [], [], [], [], [], [], [], [], [], []

    for line in chunk:
        try:
            match = pattern.search(line.strip()) if pattern is not None else None
            message = [match.group(header) for header in headers]
            
            content = message[-1]
            result = template_miner.add_log_message(content)
            print(result)
            log_texts.append(result["template_mined"])
            event_templates.append(result["cluster_id"])
            original_logs.append(line)
            
            current_timestamp = detect_timestamp_format(line)
            if current_timestamp:
                current_unix_time = time.mktime(current_timestamp.timetuple())
                unix_times.append(current_unix_time)
                normalized_timestamps.append(current_unix_time - first_unix_time)
            else:
                unix_times.append(None)
                normalized_timestamps.append(None)
            
            parameters_wo_categories,params_with_categories = get_parameter_list_generic(result["template_mined"], content)
            parameters.append(params_with_categories)
            parameters_wo.append(parameters_wo_categories)
            timestamps.append(current_timestamp)
        except Exception as e:
            pass

    return timestamps, log_texts, event_templates, original_logs, unix_times, normalized_timestamps, parameters, parameters_wo

def parse_log_file(log_file_path, pattern=None, headers=None, chunk_size=10000):
    # Initialize the template miner
    template_miner = TemplateMiner()

    # Read the log file
    with open(log_file_path, 'r') as file:
        log_lines = file.readlines()

    first_timestamp = detect_timestamp_format(log_lines[0])
    if first_timestamp is None:
        print("Error: Couldn't detect timestamp format from the first log line.")
        return None

    first_unix_time = time.mktime(first_timestamp.timetuple())

    # Split log lines into chunks
    chunks = [log_lines[i:i+chunk_size] for i in range(0, len(log_lines), chunk_size)]

    # Define a partial function for parsing a log chunk
    parse_chunk_partial = partial(parse_log_chunk, pattern=pattern, headers=headers, first_unix_time=first_unix_time,template_miner=template_miner)

    # Process chunks in parallel
    with multiprocessing.Pool() as pool:
        results = pool.map(parse_chunk_partial, chunks)

    # Combine results from all chunks
    timestamps, log_texts, event_templates, original_logs, unix_times, normalized_timestamps, parameters, parameters_wo = zip(*results)

    # Flatten lists
    timestamps = [item for sublist in timestamps for item in sublist]
    log_texts = [item for sublist in log_texts for item in sublist]
    event_templates = [item for sublist in event_templates for item in sublist]
    original_logs = [item for sublist in original_logs for item in sublist]
    unix_times = [item for sublist in unix_times for item in sublist]
    normalized_timestamps = [item for sublist in normalized_timestamps for item in sublist]
    parameters = [item for sublist in parameters for item in sublist]
    parameters_wo = [item for sublist in parameters_wo for item in sublist]

    # Convert lists to DataFrame
    try:
        df = pd.DataFrame({
            'Timestamp': timestamps,
            'Content': log_texts,
            'EventID': event_templates,
            'Original Log': original_logs,
            'Unix Time': unix_times,
            'Normalized Timestamp': normalized_timestamps,
            'Parameters': parameters,
            'Parameters_without_categories': parameters_wo,
        })
        print(f'{len(df)}')
        print(df)
    except:
        df = None
        print("Error occurred during DataFrame creation.")

    return df

def detect_delimiter(filename, sample_size=1024):
    with open(filename, 'r') as f:
        sample = f.read(sample_size)
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample)
            return dialect.delimiter
        except csv.Error:
            # Couldn't determine delimiter
            return None
        
def is_csv_content(filename, delimiter=None):
    if not delimiter:
        delimiter = detect_delimiter(filename)
        if not delimiter:
            delimiter = ','
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter=delimiter)
            for _ in reader:  # Just iterate over a few rows to check
                break
        return True
    except csv.Error:
        return False

@time_it
def parse_log_file_from_file(logName='SSH.log', delimiter=',',outdir='.',indir='.'):
    
    logfileName = os.path.expanduser(indir) + logName
    if logfileName.lower().endswith('.csv'):
        df = pd.read_csv(logfileName)
    else:
        log_format = get_log_format(logName)
        headers, pattern = generate_logformat_regex(log_format)
        df = parse_log_file(logfileName, pattern=pattern, headers=headers)
        #print(df.head())
    
    df.to_csv(os.path.join(outdir,logName + '_templates.csv'), index=True)

# Example usage
#log_file_path = "path_to_your_log_file.log"

if __name__ == '__main__':

   # indir = r'C:\Users\addeepak\Desktop\LogAnalysis\input_logs\\'
   # outdir = r'C:\Users\addeepak\Desktop\LogAnalysis\profile_figs\\'
   indir = './input_logs/'
   outdir = '.'

   parse_log_file_from_file(logName='OpenSSH_2sk.log', delimiter=';',outdir='.',indir=indir)
