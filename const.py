
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
