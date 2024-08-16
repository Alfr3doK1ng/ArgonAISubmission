import streamlit as st
import requests
import pandas as pd

# Backend URL configuration
backend_url = "http://127.0.0.1:5000" 

# Title of the application
st.title("Clinical Trial Search App")

# Sidebar for input
st.sidebar.header("Search Criteria")
query = st.sidebar.text_input("Enter query (e.g., NSCLC)")
status = st.sidebar.selectbox("Select trial status", ['All', 'Finished', 'Ongoing', 'Planned'])
immunotherapy_filter = st.sidebar.checkbox("Filter for Immunotherapy trials", value=False)

# Button to trigger search
if st.sidebar.button("Search"):
    # Prepare the query parameters
    params = {
        "query": query,
        "status": status.lower(),
        "immunotherapy": str(immunotherapy_filter).lower()
    }
    
    # Making a GET request to the backend API to search trials
    response = requests.get(f"{backend_url}/search_trials", params=params)
    
    if response.status_code == 200:
        trials = response.json()
        
        if trials:
            st.subheader("Search Results")
            
            # Parse the JSON response
            trials_df = pd.read_json(trials)
            
            # Display each result as a clickable, foldable entry
            for index, row in trials_df.iterrows():
                with st.expander(f"{row['study_title']} (NCT Number: {row['nct_number']})"):
                    st.markdown(f"**Study Title:** {row['study_title']}")
                    st.write(f"**Locations:** {row['locations']}")
                    st.write(f"**Study Documents:** {row['study_documents']}")
                    st.write(f"**Summary:** {row['brief_summary']}")
                    st.write(f"**Conditions:** {row['conditions']}")
                    st.write(f"**Status:** {row['study_status']}")
                    st.write(f"**Start Date:** {row['start_date']}")
                    st.write(f"**Primary Completion Date:** {row['primary_completion_date']}")
                    st.write(f"**Completion Date:** {row['completion_date']}")
                    st.write("---")
        else:
            st.write("No results found for your criteria.")
    else:
        st.write("Error: Unable to fetch data from the backend.")

# Section to trigger indexing
st.sidebar.subheader("Admin Operations")
if st.sidebar.button("Trigger Indexing"):
    # Making a POST request to the backend API to trigger indexing
    response = requests.post(f"{backend_url}/index")
    
    if response.status_code == 200:
        st.sidebar.write("Indexing completed successfully!")
    else:
        st.sidebar.write("Error: Indexing failed.")

# Instruction or status messages
st.write("Use the sidebar to search for clinical trials or to trigger indexing.")
