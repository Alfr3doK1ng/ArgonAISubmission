from flask import Flask, request, jsonify
import pandas as pd
from pymilvus import MilvusClient
from openai import OpenAI
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)


os.environ["OPENAI_API_KEY"] = 'sk-'

openai_client = OpenAI()
MODEL_NAME = "text-embedding-3-small"
DIMENSION = 1536
collection_name_list = ['study_title', 'brief_summary', 'conditions']


df = pd.read_csv('ctg-studies.csv')
df = df.fillna('N/A')
# Preprocess columns
def transform_name(name):
    return name.lower().replace(" ", "_")

df.columns = [transform_name(name) for name in df.columns]

milvus_client = MilvusClient("ArgonCoding.db")

# API endpoint to trigger indexing
@app.route('/index', methods=['POST'])
def index_data():

    vector_dict = {}
    for collection_name in collection_name_list:
        vectors = []
        for i in range(0, len(df), len(df) // 10):
            docs = df[collection_name][i:i+len(df) // 10]
            vectors.extend(
                [vec.embedding
                for vec in openai_client.embeddings.create(input=docs, model=MODEL_NAME).data]
            )
        vector_dict[collection_name] = vectors

    for collection_name in collection_name_list:
        vectors = vector_dict[collection_name]
        docs = df[collection_name]
        data = [
            {"id": i, "vector": vectors[i], "text": docs[i]}
            for i in range(len(docs))
        ]
        # Connect to Milvus, all data is stored in a local file named "milvus_openai_demo.db"
        COLLECTION_NAME = collection_name
        
        # Create a collection to store the vectors and text
        if milvus_client.has_collection(collection_name=COLLECTION_NAME):
            milvus_client.drop_collection(collection_name=COLLECTION_NAME)
        milvus_client.create_collection(collection_name=COLLECTION_NAME, dimension=DIMENSION)
        milvus_client.insert(collection_name=COLLECTION_NAME, data=data)

    return jsonify({"message": "Indexing completed successfully"}), 200


def _generate_multiple_queries_with_openai(query):
    # Generate multiple queries using OpenAI's DaVinci model
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "system",
            "content": "You are an intelligent assistant that specializes in querying and refining search results from clinical trial databases. Your task is to help the user optimize their search queries for better accuracy and relevance. When given a query, analyze it, identify potential improvements, and return a rewritten version that enhances the search results, considering factors like keyword specificity, synonyms, and relevant fields. Simply return the rewritten query as a response."
            },
            {"role": "user", "content": query},
        ],
        max_tokens=50,
        n=5,  # Requesting 5 completions
        temperature=0.7
    )
    
    # Extracting all the generated queries
    queries = [choice.message.content for choice in response.choices]
    return queries

# Define search API endpoint
@app.route('/search_trials', methods=['GET'])
def search_trials():
    query = request.args.get('query')
    rewritten_queries = _generate_multiple_queries_with_openai(query)
    queries = rewritten_queries
    print(queries)

    immunotherapy_filter = request.args.get('immunotherapy', 'false').lower() == 'true'
    status_filter = request.args.get('status', 'all').lower()  # could be 'finished', 'ongoing', or 'planned'
    
    if immunotherapy_filter:
        queries.append("immunotherapy")

    completion_date_col = 'completion_date_new'
    start_date_col = 'start_date_new'

    # Convert date columns to datetime, handling mixed formats
    df[start_date_col] = pd.to_datetime(df["start_date"], errors='coerce', format='mixed')
    df[completion_date_col] = pd.to_datetime(df["completion_date"], errors='coerce', format='mixed')

    current_date = datetime.now()

    # Apply the filtering logic based on the status
    if status_filter == 'finished':
        df_filtered = df[(df[completion_date_col] < current_date)]
    elif status_filter == 'ongoing':
        df_filtered = df[(df[start_date_col] <= current_date) & (df[completion_date_col] > current_date)]
    elif status_filter == 'planned':
        df_filtered = df[(df[start_date_col] > current_date)]
    else:
        df_filtered = df
    s = set()
    # Generate query vectors
    query_vectors = [
        vec.embedding
        for vec in openai_client.embeddings.create(input=queries, model=MODEL_NAME).data
    ]

    results = []

    for collection_name in collection_name_list:

        res = milvus_client.search(
            collection_name=collection_name,  # target collection
            data=query_vectors,  # query vectors
            limit=10,  # number of returned entities
            output_fields=["text"],  # specifies fields to be returned
        )
        results.append(res)

        for q in queries:
            for result in res:
                for r in result:
                    s.add(r['id'])

    valid_indices = [i for i in s if i < len(df_filtered)]

    # Safeguard against out-of-bounds indices
    if not valid_indices:
        return jsonify({"message": "No matching trials found after processing."}), 200

    relevant_nodes = df_filtered.iloc[valid_indices]
    print(relevant_nodes)

    return jsonify(relevant_nodes.to_json()), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False)
