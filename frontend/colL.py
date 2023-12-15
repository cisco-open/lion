
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

- def colL() {STREAMLIT}

"""

import streamlit as st
import os 

from gateway.logparser import log_csv_to_df
from gateway.matrix_profile import MatrixProfileAnalyzer


def colL(): 
    st.title("Log with LION 🦁🥳")


    """ Section 1: File Upload """

    # TODO: support file types beyond csv (currently only rigorously tested w/ openssh.csv)
    st.session_state.demo_state['selected_file'] = st.file_uploader("Upload a Log File (Current support: .txt, .csv, .log)", type=["txt", "csv", "log"])

    if st.session_state.demo_state['selected_file']:
        os.makedirs(st.session_state.demo_state['dump_folder'], exist_ok=True)

        save_path = os.path.join(st.session_state.demo_state['dump_folder'], st.session_state.demo_state['selected_file'].name)
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(st.session_state.demo_state['selected_file'].read())

        st.session_state.demo_state['selected_file_path'] = save_path
        print(f"(colL.py) Successfully stored log to: {save_path}")

    st.divider() 


    """ Section 2: Button, Selector, More Info """

    min_col1, min_col2 = st.columns([0.4, 0.6])

    with min_col1: 
        st.session_state.demo_state['start_analysis'] = st.button("Analyze Log File")
        st.caption ("Want to learn more? Check out:")

    
    with min_col2: 
        st.session_state.demo_state['comps_to_see'] = st.multiselect(
            'Inspection Selector - Which comps to see?',
            ['Graphs', 'Motifs', 'Discords'], [])
    
    with st.expander("What is a Matrix Profile? Who is a Motif?? And why is a Discord???"): 
        st.markdown("""Matrix Profile is a unique tool to analyze time-series data. It is useful to efficiently determine motifs and discords. 
                    Motifs are essentially repeated patterns, while discords are deviations, or anomalies! 😧""")
    
        st.caption("_For more info, check out: https://matrixprofile.docs.matrixprofile.org/Quickstart.html_")
        

    """ Section 3: Start Button Pressed """

    if st.session_state.demo_state['start_analysis']: 
        st.session_state.demo_state['analysis_finished'] = False 

        if not st.session_state.demo_state['selected_file'] or not st.session_state.demo_state['selected_file_path']: 
            st.warning('No log file has been selected. Please upload, and try again!', icon="⚠️")
        
        else: 
            # First, we convert the log file into a dataframe 
            with st.spinner("Putting log into DF..."):
                st.session_state.demo_state['df'] = log_csv_to_df(st.session_state.demo_state['selected_file_path'], filtering_string=st.session_state.demo_state['filtering_string'])

            # Next, we initialize our Matrix Profile analyzer
            with st.spinner("Running Matrix Profile..."):
                st.session_state.demo_state['mpa'] = MatrixProfileAnalyzer(st.session_state.demo_state['df'])


            # If we're not filtering (showing subset of log), then: 
            if st.session_state.demo_state['filtering_string'] == "": 

                with st.spinner("Analyzing discords..."):
                    st.session_state.demo_state['profileDiscords'], st.session_state.demo_state['discords'] = st.session_state.demo_state['mpa'].get_discords()
                    for discord in st.session_state.demo_state['discords']: 
                        col = discord[1] # The index corresponding to this discord 
                        entry = st.session_state.demo_state['mpa'].get_df_entries(col, window=3)

                        st.session_state.demo_state['discordDict'][col] = {"log_df": entry} 


                with st.spinner("Analyzing motifs..."):
                    st.session_state.demo_state['profileMotifs'], st.session_state.demo_state['motifs'] = st.session_state.demo_state['mpa'].get_motifs()
                    for motif in st.session_state.demo_state['motifs']: 
                        motif = motif['motifs']

                        # TODO: assuming only 2 motif entries... so far unable to find any 2+ cases 
                        st_row, st_col = motif[0][0], motif[0][1]
                        en_row, en_col = motif[1][0], motif[1][1]

                        window_size = st.session_state.demo_state['profileMotifs']['windows'][st_row]

                        entry = st.session_state.demo_state['mpa'].get_df_entries(st_col, window=window_size, after=True)
                        st.session_state.demo_state['motifDict'][st_col] = {"log_df": entry, "locs" : [st_col, en_col], "window_size": window_size}  

            
            print(f"(colL.py) Analysis finished.")

            st.session_state.demo_state['analysis_finished'] = True 
            st.success('Analysis Completed Successfully.', icon="✅")

    st.divider()


    """ Section 4. Filtering w/ Specific Variables """

    st.subheader("Filter using Specific Variables 🔍")

    st.caption("Upon inspection of discords and motifs, feel free to view a filtered version of the log file.")
    st.session_state.demo_state['filtering_string'] = st.text_input(label="Enter any variables, keywords, addresses, and more (boolean operators supported!)", placeholder="Ex. 173.234.31.186 in Content || Pid==24,200")
    st.caption("Simply press 'Analyze Log File' or empty the text input to remove filtering")