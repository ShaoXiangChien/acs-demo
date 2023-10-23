# Azure Cognitive Search (ACS) Demo

## Overview

This repository demonstrates the capabilities of Azure Cognitive Search (ACS) using Streamlit. It showcases various features such as simple queries, facet queries, synonym mapping, suggestions, autocomplete, and AI enrichment.

## Features

- **Simple Query**: Search for hotels based on specific criteria such as rating, state, and order.
- **Facet Query**: Filter search results based on cities and categories.
- **Synonym**: Search for hotels using synonyms.
- **Suggestion**: Get suggested search terms based on the input.
- **Autocomplete**: Get autocomplete suggestions as you type.
- **AI Enrichment**: Enrich search results with AI, including images and detailed content.

## Getting Started

1. **Setup**:
   - Clone the repository to your local machine.
   - Install the required Python packages using the `requirements.txt` file.
   - Set up your Azure Cognitive Search service.

2. **Run the App**:
   - Execute the `app.py` script to start the Streamlit app.
   - Use the sidebar to select different search modes and input search criteria.

3. **Search Modes**:
   - **Simple Query**: Input search text and filter results based on rating and state.
   - **Facet Query**: Select cities and categories to filter results.
   - **Synonym**: Choose between different search indices and input search text.
   - **Suggestion**: Input search text to get suggested terms.
   - **Autocomplete**: Input search text and select completion mode to get autocomplete suggestions.
   - **AI Enrichment**: Input search text to get enriched results, including images and detailed content.

## Dependencies

- **Streamlit**: For creating the web app interface.
- **Pandas**: For data manipulation.
- **JSON**: For reading the `image_url.json` file.
- **Streamlit Elements**: For additional Streamlit components.
- **PIL**: For image processing.

## Contributing

Contributions are welcome! Feel free to create pull requests or raise issues. Your feedback and contributions are highly appreciated.
