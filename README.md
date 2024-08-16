# How to run

## Install Milvus locally (Vector DB)

Run these two scripts to start running docker for Milvus service:

### Download the installation script
$ curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

### Start the Docker container
$ bash standalone_embed.sh start

## Run the code

Fill in your openai api key

`source venv/bin/activate`

`python backend.py`

`streamlit run frontend.py`

Then click on <img width="204" alt="Screenshot 2024-08-16 at 3 30 21 AM" src="https://github.com/user-attachments/assets/1ef653ba-b499-4e80-85d3-3670b012e204">

Wait for a while. (~3 minutes)

<img width="384" alt="Screenshot 2024-08-16 at 3 30 56 AM" src="https://github.com/user-attachments/assets/e4f0ffd7-5b30-4390-a9a8-a3049e8dfa06">

Fill in arguments.

Click search.

Clinical results will show on the right.

If you want to serach Immunotherapy, check the box, and click search again.

# Discussion

Bonus points:
- How do we allow her to search for NSCLC trials -AND- immunotherapy related drugs?
  * By rewriting the query, we can allow for better search results of NSCLC trials. For Immunothearapy, we add a keyword of that to the query to be sent to the vector DB.
  * But we can also implement logic that runs two queries and take intersection of the results. (Need to try, but no time to implement.)
- How would you deploy your software?
  * Deploy the software using Docker. Dockerize everything and use Docker compose to orchestrate. Then deploy everything onto AWS EC2.
- What are the alternatives to loading the dataset into memory, and why would you want to
use those alternatives?
  * Now Vector DB is self hosted. Could possibly migrate it to cloud, which will reduce memory needed.
- How do we evaluate completeness of results?
  * Can use LLM as a judge to compare if everything is included in the search results. It's expensive but the eval performance will be guaranteed.

