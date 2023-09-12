import re 
import streamlit as st 

from gateway.openai_summ import generate_log_summary

from frontend.colE import colE
from frontend.colV import colV


def colR(): 
    # Only display the RHS if analysis is finished running 
    if st.session_state.demo_state['analysis_finished']: 


        # Case 1: Display filtering components 

        if st.session_state.demo_state['filtering_string'] != "": 
            st.subheader(f"Filtered Log (entries reduced to: {len(st.session_state.demo_state['df'])})")
            st.dataframe(st.session_state.demo_state['df'],  hide_index=True, column_order=("LineId", "TimeFull", "Pid", "Component", "EventId", "Content"), column_config={"EventTemplate": None})

            gpt_analysis = st.button("Submit for GPT Analysis", key=-1)

            if gpt_analysis: 
                with st.spinner("Querying LLM w/ specified data..."): 
                    log_data_str = st.session_state.demo_state['df'].to_string(index=False)
                    res = generate_log_summary(st.session_state.demo_state['api_key'], log_data_str)

                    st.subheader(res) 

            st.session_state.demo_state['motifs'] = [] 
            st.session_state.demo_state['discords'] = [] 


        # Case 2: No motifs/discords have been selected in viewer

        elif len(st.session_state.demo_state['comps_to_see']) == 0: 
            colE()

        # Case 3: Showing graph analysis pane 

        elif 'Graphs' in st.session_state.demo_state['comps_to_see']: 
            colV()

        # Case 4: Displaying motifs/discord viewer 

        elif len(st.session_state.demo_state['motifs']) != 0 and len(st.session_state.demo_state['discords']) != 0: 
            
            # Compute the tab titles (and length) depending on mutiselect in LHS column 

            list_of_events = [] 

            if "Motifs" in st.session_state.demo_state['comps_to_see']: 
                list_of_events.extend([f"Motif {i+1}" for i, d in enumerate(st.session_state.demo_state['motifs'])])

            if "Discords" in st.session_state.demo_state['comps_to_see']: 
                list_of_events.extend([f"Discord {i+1}" for i, d in enumerate(st.session_state.demo_state['discords'])])


            # Display each tab individually (for loop) 

            whitespace = 12
            for idx, tab in enumerate(st.tabs([s.center(whitespace,"\u2001") for s in list_of_events])): 

                tab.header(f"{list_of_events[idx]}")
                print(f"(colR.py) Idx: {idx} - This is tab: {list_of_events[idx]}")

                # Case 1: This is a Motif tab 

                if "Motif" in list_of_events[idx]: 
                    pattern = r"Motif (\d+)"
                    entry_num = int(re.search(pattern, list_of_events[idx]).group(1)) - 1 
                    motif = st.session_state.demo_state['motifs'][entry_num]

                    _, col =  motif["motifs"][0]
                    res = st.session_state.demo_state['motifDict'][col]

                    motif_idx_arr = [] 
                    for m in motif["motifs"]: 
                        row, col = m
                        row_time = st.session_state.demo_state['df'].iloc[int(col)]["TimeFull"]
                        motif_idx_arr.append({"id" : str(int(col) + 1), "start" : row_time.strftime('%Y-%m-%d %H:%M:%S')})
                    
                    motif_idx_title = [m["id"] for m in motif_idx_arr]
                    tab.markdown(f"Occurs at indices: {', '.join(motif_idx_title)}")

                    tab.dataframe(res["log_df"],  hide_index=True, column_order=("LineId", "TimeFull", "Pid", "Component", "EventId", "Content"), column_config={"EventTemplate": None})

                    gpt_analysis = tab.button("Submit for GPT Analysis", key=idx)

                    if gpt_analysis: 
                        with st.spinner("Querying LLM w/ specified data..."): 
                            log_data_str = res["log_df"].to_string(index=False)
                            res = generate_log_summary(st.session_state.demo_state['api_key'], log_data_str)

                            tab.subheader(res) 


                # Case 2: This is a Discord tab 

                if "Discord" in list_of_events[idx]: 
                    pattern = r"Discord (\d+)"
                    entry_num = int(re.search(pattern, list_of_events[idx]).group(1)) - 1

                    col = st.session_state.demo_state['discords'][entry_num][1] # Getting col of this discord
                    entry = st.session_state.demo_state['discordDict'][col]

                    tab.markdown(f"Anomaly found on line: {col+1}")


                    extracted_variables = set() 

                    for i, row in entry["log_df"].iterrows(): 
                        template = row["EventTemplate"]
                        content = row["Content"]

                        template_words = template.split(" ")
                        content_words = content.split(" ") 

                        for j, word in enumerate(template_words):
                                if "<*>" in word: 
                                    extracted_variables.add(content_words[j])


                    if "" in extracted_variables: extracted_variables.remove("")
                    markdown_list = ", ".join([f"{item}" for item in extracted_variables])

                    tab.markdown(f"Variables Extracted: {markdown_list}")

                    # TODO: CAN ADD A SLIDER HERE THAT WILL SLIDE/SHOW MORE OR LESS CONTEXT DEPENDING ON WINDOW_SIZE

                    def highlight_row(row):
                        return ['background-color: yellow' if row['LineId'] == col + 1 else '' for _ in row]

                    styled_df = entry["log_df"].style.apply(highlight_row, axis=1)
                    
                    tab.dataframe(styled_df, hide_index=True, column_order=("LineId", "TimeFull", "Pid", "Component", "EventId", "Content"), column_config={"EventTemplate": None})

                    tab.caption("Currently, some of the discords may overlap. This is a feature we are working to resolve!")

                    gpt_analysis = tab.button("Submit for GPT Analysis", key=idx)

                    if gpt_analysis: 
                        with st.spinner("Querying LLM w/ specified data..."): 
                            log_data_str = entry["log_df"].to_string(index=False)
                            res = generate_log_summary(st.session_state.demo_state['api_key'], log_data_str)

                            tab.subheader(res) 



