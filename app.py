import streamlit as st
from setup import searchClient

MODES = ["Simple Query", "Facet Query",
         "Synonym", "Suggestion", "Autocomplete"]


if __name__ == "__main__":
    st.title("Azure Cognitive Search Demo")
    st.sidebar.selectbox("Choose a mode", MODES)
