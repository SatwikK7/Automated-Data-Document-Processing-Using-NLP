import streamlit as st
from typing import Callable, List

class UIComponents:
    @staticmethod
    def file_upload_section(callback: Callable) -> None:
        st.header("Upload Documents")
        uploaded_file = st.file_uploader("Upload a file", type=["xml", "json", "pdf"])
        if uploaded_file:
            callback(uploaded_file)

    @staticmethod
    def query_section(filename: str, callback: Callable) -> None:
        st.subheader(f"Query {filename}")
        query = st.text_input(f"Enter your query for {filename}")
        if query and st.button(f"Submit Query for {filename}"):
            callback(query)