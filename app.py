import streamlit as st
import pandas as pd
import json
from streamlit_elements import elements, mui, html
from services import *

MODES = ["Simple Query", "Facet Query",
         "Synonym", "Suggestion", "Autocomplete", "AI Enrichment"]
FIELDS = ['HotelName', 'City', 'Category', 'ParkingIncluded',
          'Rating', 'Description', 'Tags', 'Address', 'StateProvince', 'LastRenovationDate']
OPERATOR_DT = {">=": "ge", "=": "eq", "<=": "le"}
COMPLETE_MODE = ['oneTerm', 'twoTerms', 'oneTermWithContext']
with open("./image_url.json") as fh:
    image_url_dt = json.load(fh)


def hotel_component(Name, Rating, Description, City, Tags, search_text):
    colored_text = f'<span style="font-family:sans-serif; color:red; font-weight: 700;">{search_text}</span>'
    Name = Name.lower().replace(search_text, colored_text)
    Description = Description.lower().replace(search_text, colored_text)
    City = City.lower().replace(search_text, colored_text)
    for i in range(len(Tags)):
        Tags[i] = Tags[i].replace(search_text, colored_text)
    with st.container():
        st.subheader(Name)
        st.markdown(f"Rating - {Rating}", unsafe_allow_html=True)
        st.markdown(f"City - {City}", unsafe_allow_html=True)
        st.markdown("Tags - " + ", ".join(Tags), unsafe_allow_html=True)
        st.markdown(Description, unsafe_allow_html=True)


@st.cache(allow_output_mutation=True)
def facet_result_gen():
    results = searchClient.search(
        search_text="*",
        facets=["City", 'Category']
    )
    return results.get_facets(), [res for res in results]


if __name__ == "__main__":
    st.title("Azure Cognitive Search Demo")
    mode = st.sidebar.selectbox("Choose a mode", MODES)
    searchClient = create_search_client("hotels-sample-index")
    if mode == "Simple Query":
        st.header(mode)
        with st.form("Search Query"):

            search_text = st.text_input("Search Text")

            st.write("Filter")
            cols = st.columns(3)

            filter_field = cols[0].selectbox(
                "field", ['Rating', 'StateProvince'])
            operator = cols[1].selectbox("operator", [">=", "=", "<="])
            target = cols[2].text_input("target value", "4")

            st.write("Order")
            cols = st.columns(2)
            order_field = cols[0].selectbox("field", FIELDS, 4)
            order_mode = cols[1].selectbox("mode", ['desc', 'asc'])
            submitted = st.form_submit_button("Search")

        if submitted:
            filter_str = f"{filter_field} {OPERATOR_DT[operator]} {target}" if target != "" else ""
            order_str = f"{order_field} {order_mode}"

            results = searchClient.search(
                search_text=search_text,
                filter=filter_str,
                order_by=order_str,
                include_total_count=True,
                top=5)
            st.write(
                f"Total Documents Matching Query: {results.get_count()}")
            result_df = pd.DataFrame([res for res in results])
            result_df['Address'] = result_df.apply(
                lambda x: f"{x['StreetAddress']}, {x['City']}, {x['StateProvince']}, {x['Country']}", axis=1)
            # st.dataframe(result_df[FIELDS])
            for idx, tmp in result_df.iterrows():
                hotel_component(tmp['HotelName'], tmp['Rating'],
                                tmp['Description'], tmp['City'], tmp['Tags'], search_text)

    elif mode == "Facet Query":
        st.header(mode)
        facets, results = facet_result_gen()

        city_facet = [
            f"{fc['value']} ({fc['count']})" for fc in facets['City']]
        category_facet = [
            f"{fc['value']} ({fc['count']})" for fc in facets['Category']]

        city_tags = st.multiselect("Cities", city_facet, city_facet[:1])
        category_tags = st.multiselect(
            "Category", category_facet, category_facet[:1])

        city_tags = [s[:s.index(
            "(") - 1] for s in (city_tags if len(city_tags) != 0 else city_facet)]
        category_tags = [s[:s.index(
            "(") - 1] for s in (category_tags if len(category_tags) != 0 else category_facet)]

        df = pd.DataFrame(results)
        df['Address'] = df.apply(
            lambda x: f"{x['StreetAddress']}, {x['City']}, {x['StateProvince']}", axis=1)
        ft = df.apply(lambda x: x['City'] in city_tags
                      and x['Category'] in category_tags, axis=1)
        df = df[ft]
        st.dataframe(df[FIELDS])

    elif mode == "Synonym":
        st.header(mode)
        with st.form("synonym"):
            index_mode = st.selectbox(
                "Search Index", ["hotels-sample-index", "hotels-sample-index-synonym"])
            search_client = create_search_client(index_mode)
            search_text = st.text_input("Search Text")

            submitted = st.form_submit_button("Search")

        if submitted:
            results = search_client.search(search_text=search_text, top=5)
            documents = [res for res in results]

            if len(documents) > 0:
                df = pd.DataFrame(documents)
                if index_mode == "hotels-sample-index-synonym":
                    df['StateProvince'] = df.Address.apply(
                        lambda x: x['StateProvince'])
                    df['StreetAddress'] = df.Address.apply(
                        lambda x: x['StreetAddress'])
                    df['City'] = df.Address.apply(lambda x: x['City'])

                df['Address'] = df.apply(
                    lambda x: f"{x['StreetAddress']}, {x['City']}, {x['StateProvince']}", axis=1)
                st.dataframe(df[FIELDS])
            else:
                st.write("No matching results")

    elif mode == "Suggestion":
        st.header(mode)
        search_text = st.text_input("search text")
        if search_text != "":
            results = searchClient.suggest(
                search_text=search_text,
                suggester_name="sg"
            )
            st.subheader("Suggested Text")
            for res in results:
                st.write(res['text'])
                hotel = searchClient.get_document(res['HotelId'])
                df = pd.DataFrame([hotel])
                df.index = df.HotelId
                st.dataframe(df)

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
                result_df['Address'] = result_df.apply(
                    lambda x: f"{x['StreetAddress']}, {x['City']}, {x['StateProvince']}, {x['Country']}", axis=1)
                st.dataframe(result_df[FIELDS])

    elif mode == "AI Enrichment":
        search_client = create_search_client("cogsrch-py-index")
        search_text = st.text_input("Search Text", "")
        if search_text != "":
            results = search_client.search(search_text=search_text)
            documents = [res for res in results]
            for idx, doc in enumerate(documents):
                st.header(f"Result {idx}")
                if doc['metadata_storage_name'][-3:] in ['jpg', 'png']:
                    if image_url_dt.get(doc['metadata_storage_name']):
                        st.subheader("Image")
                        st.image(image_url_dt.get(
                            doc['metadata_storage_name']))

                st.subheader("Content")
                st.write(doc['content'][:100] if len(
                    doc['content']) > 100 else doc['content'])

                st.subheader("Text")
                text = "\n".join(doc['text'])
                st.write(text[:100] if len(text) > 100 else text)
