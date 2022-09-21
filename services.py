from re import search
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchIndex,
    ScoringProfile,
    SearchFieldDataType,
    SimpleField,
    SearchableField
)

# Set the service endpoint and API key from the environment
serviceName = "cseric"
adminKey = "JsdazQBtme5kOfjsHSrkKSh2l5pgAejtPRqwGfR2P9AzSeCsWbP7"
indexName = "hotels-sample-index"

# Create an SDK client
endpoint = "https://{}.search.windows.net/".format(serviceName)
adminClient = SearchIndexClient(endpoint=endpoint,
                                index_name=indexName,
                                credential=AzureKeyCredential(adminKey))

searchClient = SearchClient(endpoint=endpoint,
                            index_name=indexName,
                            credential=AzureKeyCredential(adminKey))


def get_document(id):
    return searchClient.get_document(key=id)
