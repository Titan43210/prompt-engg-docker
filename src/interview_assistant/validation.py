from guardrails import Guard
from guardrails.hub import SimilarToDocument
import json

# Define the path to your JSON file
dict_file_path = '../../data.json'

# Load the JSON data from the file
with open(dict_file_path, 'r') as f:
    qa_dict = json.load(f)

def validate_response(query, response):
    golden_response = qa_dict[query]
    guard = Guard().use(
        SimilarToDocument,
        document= golden_response,
        threshold=0.7,
        model="all-MiniLM-L6-v2",
        on_fail="exception",
    )
    try:
        score = guard.validate(response)
        return score
    except Exception as e:
        print(e)
