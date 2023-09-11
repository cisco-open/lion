"""

Log Analysis Demo - Stable, 9/10

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
