import streamlit as st
import pandas as pd

from services import *

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
COMPLETE_MODE = ['oneTerm', 'twoTerms', 'oneTermWithContext']
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
        search_text = st.text_input("search text")
        if search_text != "":
            results = searchClient.suggest(
                search_text=search_text,
                suggester_name="sg"
            )

            res_docs = []
            st.subheader("Suggested Text")
            for res in results:
                hotel = get_document(res['HotelId'])
                res_docs.append(hotel)
                st.write("Text: {} for Hotel: {}".format(
                    repr(res["text"]), hotel["HotelName"]))

            res_df = pd.DataFrame(res_docs)
            res_df['Address'] = res_df.Address.apply(
                lambda x: f"{x['StreetAddress']}, {x['City']}, {x['StateProvince']}, {x['Country']}")

            st.subheader("Suggested Search Results")
            st.dataframe(res_df[FIELDS])

    elif mode == "Autocomplete":
        st.header(mode)
        search_text = st.text_input("search text")
        complete_mode = st.selectbox("Completion Mode", COMPLETE_MODE)
        if search_text != "":
            results = searchClient.autocomplete(
                search_text=search_text,
                suggester_name="sg",
                mode=complete_mode
            )
            with st.form("autocomplete"):
                completions = [res['query_plus_text' if complete_mode ==
                                   "oneTermWithContext" else "text"] for res in results]
                query = st.selectbox("Search with", completions)

                submitted = st.form_submit_button("Search")

            if submitted:
                results = searchClient.search(
                    search_text=query,
                    include_total_count=True,
                )

                st.write(
                    f"Total Documents Matching Query: {results.get_count()}")
                result_df = pd.DataFrame([res for res in results])
                result_df['Address'] = result_df.Address.apply(
                    lambda x: f"{x['StreetAddress']}, {x['City']}, {x['StateProvince']}, {x['Country']}")
                st.dataframe(result_df[FIELDS])
