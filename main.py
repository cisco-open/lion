
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

Log Analysis Demo - Stable, 9/11

IMPORTANT: pip install protobuf==3.20.0
Will NOT work (streamlit and matrix profile are not compatible unless 3.20.X)

To run, simply execute `streamlit run main.py`  

"""

import streamlit as st

from frontend.colL import colL 
from frontend.colR import colR

from const import INITIAL_STATE 
import os 


st.set_page_config(page_title='Log Analysis', layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)


if 'demo_state' not in st.session_state: 
    st.session_state.demo_state = INITIAL_STATE 

try:
    print(f"(main.py) Cleaning all files in {st.session_state.demo_state['dump_folder']}.")
    file_list = os.listdir(st.session_state.demo_state["dump_folder"])

    for file_name in file_list:
        file_path = os.path.join(st.session_state.demo_state["dump_folder"], file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f" - Deleted file: {file_name}")

    print(f"(main.py) All files in log_dump dir have been deleted.")

except Exception as e:
    print(f"(main.py) An error occurred during file deletion: {str(e)}")


lhs, _, rhs = st.columns([0.3, 0.1, 0.6]) 

with lhs: colL()
with rhs: colR()
