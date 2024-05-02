import streamlit as st
import pandas as pd
from collections import defaultdict
import global_vars 

post_client = global_vars.post_client
mongo_client = global_vars.mongo_client

def workspaces_sorted_by_activity():
    
    cur = post_client.cursor()

    mongo_db = mongo_client["happysales"]

    collection = mongo_db["user_prospect"]

    st.write("# List of workspaces")

    # Pipeline to filter and group documents
    pipeline = [
        {
            "$match": {"used_email": True}  # Filter documents with "used_email" set to True
        },
        {
            "$group": {"_id": "$user_id", "documents": {"$push": "$$ROOT"}}
        }
    ]

    # Execute aggregation pipeline
    grouped_prospects = collection.aggregate(pipeline)

    user_group_sizes = defaultdict(lambda: 0)

    for doc in grouped_prospects:
        user_id = doc["_id"]
        documents = doc["documents"]
        user_group_sizes[user_id] = len(documents)  
    

    user_ids = list(user_group_sizes.keys())

    placeholder_clause = ','.join(['%s'] * len(user_ids))

    # Construct the query with parameterization
    query = f"""
    SELECT id, workspace_id
    FROM public.\"user\"
    WHERE id IN ({placeholder_clause});
    """

    cur = post_client.cursor()

    # # Execute query with user IDs as parameters
    cur.execute(query, user_ids)

    # Fetch results and store in a dictionary
    workspace_id_dict = defaultdict(lambda: 0)
    for row in cur:
        user_id, workspace_id = row
        workspace_id_dict[user_id] = workspace_id

    workspace_activity_count = defaultdict(lambda: 0)

    workspace_ids = set()

    for user_id, workspace_id in workspace_id_dict.items():

        workspace_activity_count[workspace_id] += user_group_sizes[user_id]
        workspace_ids.add(workspace_id)
    
    workspace_name_dict = defaultdict(str)  # Dictionary to store workspace_id and name
    workspace_creator_dict = defaultdict(str)

    # Construct the query to fetch workspace names
    query = """
    SELECT id, created_by, name
    FROM workspace
    WHERE id IN %s;
    """
    cur.execute(query, (tuple(workspace_ids),))

    # Fetch results and store workspace names in the dictionary
    for row in cur:
        workspace_id, creator_id, name = row
        workspace_creator_dict[workspace_id] = creator_id
        workspace_name_dict[workspace_id] = name


    creator_email_dict = defaultdict(str)  # Dictionary to store creator ID and email

    # Construct the query to fetch creator emails
    query = """
    SELECT id, email
    FROM public."user"
    WHERE id IN %s;
    """

    # Collect creator IDs from workspace_creator_dict
    creator_ids = set(workspace_creator_dict.values())

    # Execute query with creator IDs as a tuple (if any)
    if creator_ids:
        cur.execute(query, (tuple(creator_ids),))

    # Fetch results and store creator emails in the dictionary
    for row in cur:
        creator_id, email = row
        creator_email_dict[creator_id] = email

    workspace_data = []

    # Combine information into dictionaries
    for workspace_id, name in workspace_name_dict.items():
        creator_id = workspace_creator_dict.get(workspace_id)
        creator_email = creator_email_dict.get(creator_id)
        activity_count = workspace_activity_count.get(workspace_id, 0)  # Handle missing activity

        workspace_data.append([workspace_id, name, creator_email, activity_count])

    # Sort workspace_data based on activity_count in decreasing order
    sorted_workspace_data = sorted(workspace_data, key=lambda x: x[3], reverse=True)

    # Convert table_data to a pandas DataFrame
    df = pd.DataFrame(sorted_workspace_data, columns=["Workspace Id", "Workspace Name", "Creator Email", "Activity Count"])

    # Sort DataFrame by activity_count (descending)
    df = df.sort_values(by='Activity Count', ascending=False)

    # Display table header
    st.header("Sorted Workspace Data")
    st.write("**Note:** Creator email might be 'Not Found' if unavailable.")

    # Display table using pandas DataFrame with Streamlit
    st.dataframe(df)

if st.session_state["authentication_status"]:
    authenticator = st.session_state['authenticator']
    authenticator.logout()
    workspaces_sorted_by_activity()

else:
    st.write("this is a protected route, login to access this route")