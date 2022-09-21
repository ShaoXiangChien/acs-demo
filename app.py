import streamlit as st
import pandas as pd

from setup import searchClient

MODES = ["Simple Query", "Facet Query",
         "Synonym", "Suggestion", "Autocomplete"]
FIELDS = [
    'HotelName',
    'Rating',
    'Category',
    'Tags',
    'Description',
    'Address',
    'Location',
    'Description_fr',
    'ParkingIncluded',
    'LastRenovationDate'
]
OPERATOR_DT = {">=": "ge", "=": "eq", "<=": "le"}

if __name__ == "__main__":
    st.title("Azure Cognitive Search Demo")
    mode = st.sidebar.selectbox("Choose a mode", MODES)
    if mode == "Simple Query":
        st.header(mode)
        with st.form("Search Query"):
            cols = st.columns(2)
            search_text = cols[0].text_input("Search Text")
            select_fields = cols[1].multiselect("Interested Info", FIELDS, [
                                                'HotelName', 'Rating', 'Description'])

            st.write("Filter")
            cols = st.columns(3)

            filter_field = cols[0].selectbox(
                "field", ['Rating', 'Address/StateProvince'])
            operator = cols[1].selectbox("operator", [">=", "=", "<="])
            target = cols[2].text_input("target value", "4")

            st.write("Order")
            cols = st.columns(2)
            order_field = cols[0].selectbox("field", FIELDS, 9)
            order_mode = cols[1].selectbox("mode", ['desc', 'asc'])
            submitted = st.form_submit_button("Search")

        if submitted:
            select_str = ",".join(select_fields)
            filter_str = f"{filter_field} {OPERATOR_DT[operator]} {target}" if target != "" else ""
            order_str = f"{order_field} {order_mode}"

            results = searchClient.search(
                search_text=search_text,
                select=select_str,
                filter=filter_str,
                order_by=order_str,
                include_total_count=True,
                top=5)
            st.write(
                f"Total Documents Matching Query: {results.get_count()}")
            result_df = pd.DataFrame([res for res in results])
            if 'Address' in result_df.columns:
                result_df['Address'] = result_df.Address.apply(
                    lambda x: f"{x['StreetAddress']}, {x['City']}, {x['StateProvince']}, {x['Country']}")
            st.dataframe(result_df[select_fields])

    elif mode == "Facet Query":
        st.header(mode)
        st.subheader("Facet Parameters")
        cols = st.columns(3)
        field = cols[0].selectbox("field", FIELDS, 2)
        param = cols[1].selectbox(
            "param", ['count', 'sort', 'interval', 'value'], 0)
        value = cols[2].selectbox("value", ['count', '-count', 'value', '-value']
                                  ) if param == "sort" else cols[2].text_input("value", "3")

        results = searchClient.search(
            search_text="*",
            facets=[f'{field},{param}:{value}'],
            top=5)
        result_df = pd.DataFrame([res for res in results])
        if 'Address' in result_df.columns:
            result_df['Address'] = result_df.Address.apply(
                lambda x: f"{x['StreetAddress']}, {x['City']}, {x['StateProvince']}, {x['Country']}")

        facets = results.get_facets()

        st.subheader("Search Results")
        st.dataframe(result_df[FIELDS])

        st.subheader("Facets")
        for facet in facets[field]:
            st.write(facet)

    elif mode == "Synonym":
        st.header(mode)

    elif mode == "Suggestion":
        st.header(mode)
    elif mode == "Autocomplete":
        st.header(mode)
