"""

This file defines the streamlit initial session state. 
This dictionary is stored in `st.session_state.demo_state`

"""

INITIAL_STATE =  {
    "api_key" : "<YOUR-API-KEY-HERE", 
    "dump_folder" : "file_dump/",

    "selected_file" : None, 
    "selected_file_path" : None, 
    
    "start_analysis" : False, 
    "comps_to_see" : [], 

    "df" : None, 
    "mpa" : None, 

    "profileDiscords" : None, 
    "discords" : [], 
    "discordDict" : {}, 

    "profileMotifs" : None, 
    "motifs" : [], 
    "motifDict" : {}, 

    'analysis_finished' : False, 
}