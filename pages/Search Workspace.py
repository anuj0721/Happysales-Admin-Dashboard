import streamlit as st
import pandas as pd
from collections import defaultdict
import global_vars 

st.set_page_config(page_title="Workspaces")

post_client = global_vars.post_client
mongo_client = global_vars.mongo_client

def extract_workspace_id():
    criteria = st.selectbox("Select Criteria:", ["Workspace Name", "Email Address", "Website"])
    input_value = st.text_input(f"Enter {criteria}:")

    if st.button("Search"):
        if input_value:
            workspace_data = fetch_workspace_data(criteria, input_value)
            if workspace_data:
                st.write("Workspace Data")
                df = pd.DataFrame(workspace_data, columns=["Workspace ID", "Workspace Name", "Creator Email", "Subscription Plan", "Subscription Status", "Workspace Creation Date", "Plan Ends On"])
                st.dataframe(df)
                workspace_ids = [row[0] for row in workspace_data]
                workspace_users_activity(workspace_ids[0])

            else:
                st.write("No workspace found with the provided criteria.")
        else:
            st.write("Please enter a value.")


def fetch_workspace_data(criteria, input_value):
    """
    Fetch workspace data based on the selected criteria from the database.
    """
    cursor = post_client.cursor()
    if criteria == "Workspace Name":
        query = """
            SELECT w.id AS workspace_id, w.name AS workspace_name, u.email AS creator_email, 
                    s.name AS subscription_plan_name, 
                    CASE WHEN us.is_active THEN 'Active' ELSE 'Inactive' END AS plan_status, 
                    to_char(w.created_at, 'YYYY-MM-DD HH24:MI:SS') AS workspace_creation_date, 
                    to_char(us.end_date, 'YYYY-MM-DD') AS subscription_end_date
            FROM workspace w 
            JOIN public.user u ON w.created_by = u.id 
            LEFT JOIN user_subscription us ON w.id = us.workspace_id
            LEFT JOIN subscription_plan s ON us.subscription_plan_id = s.id
            WHERE w.name = %s;
        """

    elif criteria == "Email Address":
        query = """
            SELECT w.id AS workspace_id, w.name AS workspace_name, u.email AS creator_email, 
                    s.name AS subscription_plan_name, 
                    CASE WHEN us.is_active THEN 'Active' ELSE 'Inactive' END AS plan_status, 
                    to_char(w.created_at, 'YYYY-MM-DD HH24:MI:SS') AS workspace_creation_date, 
                    to_char(us.end_date, 'YYYY-MM-DD') AS subscription_end_date
            FROM workspace w 
            JOIN public.user u ON w.created_by = u.id 
            LEFT JOIN user_subscription us ON w.id = us.workspace_id
            LEFT JOIN subscription_plan s ON us.subscription_plan_id = s.id
            WHERE u.email = %s;
        """

    elif criteria == "Website":
        query = """
            SELECT w.id AS workspace_id, w.name AS workspace_name, u.email AS creator_email, 
                    s.name AS subscription_plan_name, 
                    CASE WHEN us.is_active THEN 'Active' ELSE 'Inactive' END AS plan_status, 
                    to_char(w.created_at, 'YYYY-MM-DD HH24:MI:SS') AS workspace_creation_date, 
                    to_char(us.end_date, 'YYYY-MM-DD') AS subscription_end_date
            FROM workspace w 
            JOIN public.user u ON w.created_by = u.id 
            LEFT JOIN user_subscription us ON w.id = us.workspace_id
            LEFT JOIN subscription_plan s ON us.subscription_plan_id = s.id
            WHERE w.website = %s;
        """
    cursor.execute(query, (input_value,))
    data = cursor.fetchall()
    cursor.close()
    return data

def workspace_users_activity(target_workspace_id):

    st.write("Track the activity of each user within the workspace.")

    cur = post_client.cursor()

    mongo_db = mongo_client["happysales"]

    user_prospect_collection = mongo_db["user_prospect"]

    practice_pitch_collection = mongo_db["practice_pitch"]

    # Get creator ID from workspace relation
    # workspace_query = """
    #     SELECT created_by, created_at
    #     FROM workspace
    #     WHERE id = %s;
    # """
    # cur.execute(workspace_query, (target_workspace_id,))
    # workspace_result = cur.fetchone()

    # creator_id, created_date = workspace_result

    # # 2. Get email from user relation using creator ID
    # user_query = """
    #     SELECT email
    #     FROM public.\"user\"
    #     WHERE id = %s;
    # """
    # cur.execute(user_query, (creator_id,))
    # user_result = cur.fetchone()

    # creator_email = user_result[0]

    # st.write(creator_id, created_date, creator_email)

    # Define the query to fetch user data
    user_query = """
    SELECT id
    FROM public.\"user\"
    WHERE workspace_id = %s;
    """

    # Dictionary to store prospect count for each user ID
    user_prospect_counts_email = {}
    user_prospect_counts_disc = {}
    user_prospect_counts_icebreaker = {}
    user_prospect_counts_pitch = {}
    user_prospect_counts_scripts = {}

    # Execute the query with the target workspace ID
    cur.execute(user_query, (target_workspace_id,))

    workspace_user_ids = set()

    # Fetch rows and process for each user
    for row in cur:
        user_id = row[0]
        workspace_user_ids.add(user_id)
        # Create a query specific to this user ID
        prospect_query_email = {
            "user_id": user_id,
            "used_email": True
        }

        prospect_query_disc = {
            "user_id": user_id,
            "used_disc": True
        }

        prospect_query_icebreakers = {
            "user_id": user_id, 
            "used_prospect_icebreaker": True
        }

        prospect_query_pitch = {
            "user_id": user_id, 
            "talking_points": {"$ne": []}
        }

        prospect_query_call_scripts = {
            "user_id": user_id
        }

        # Set to store prospect IDs for this user (within the loop)
        prospect_ids_email = set()
        prospect_ids_disc = set()
        prospect_ids_icebreaker = set()
        prospect_ids_pitch = set()
        prospect_ids_scripts = set()

        # Find matching documents for this user
        for document in user_prospect_collection.find(prospect_query_email):
            prospect_ids_email.add(document["prospect_id"])

        for document in user_prospect_collection.find(prospect_query_disc):
            prospect_ids_disc.add(document["prospect_id"])

        for document in user_prospect_collection.find(prospect_query_icebreakers):
            prospect_ids_icebreaker.add(document["prospect_id"])

        for document in user_prospect_collection.find(prospect_query_pitch):
            prospect_ids_pitch.add(document["prospect_id"])

        for document in practice_pitch_collection.find(prospect_query_pitch):
            prospect_ids_scripts.add(document["prospect_id"])

        # Store the count for this user
        user_prospect_counts_email[user_id] = len(prospect_ids_email)
        user_prospect_counts_disc[user_id] = len(prospect_ids_disc)
        user_prospect_counts_icebreaker[user_id] = len(prospect_ids_icebreaker)
        user_prospect_counts_pitch[user_id] = len(prospect_ids_pitch)
        user_prospect_counts_scripts[user_id] = len(prospect_ids_scripts)

        # for user_id, prospect_count in user_prospect_counts_email.items():
        #     print(f"User ID: {user_id}, Prospect Count: {prospect_count}")

        # for user_id, prospect_count in user_prospect_counts_disc.items():
        #     print(f"User ID: {user_id}, Prospect Count: {prospect_count}")

        # for user_id, prospect_count in user_prospect_counts_icebreaker.items():
        #     print(f"User ID: {user_id}, Prospect Count: {prospect_count}")

        # for user_id, prospect_count in user_prospect_counts_pitch.items():
        #     print(f"User ID: {user_id}, Prospect Count: {prospect_count}")

        # for user_id, prospect_count in user_prospect_counts_scripts.items():
        #     print(f"User ID: {user_id}, Prospect Count: {prospect_count}")

    workspace_user_ids = list(workspace_user_ids)

    # Define the query to fetch emails using IN operator
    email_query = """
    SELECT id, email
    FROM public.\"user\"
    WHERE id IN %s;
    """

    # Convert user IDs set to a tuple for the query
    user_id_tuple = tuple(workspace_user_ids)

    user_emails = {}

    if user_id_tuple:
        # Execute the query with user_id_tuple
        cur.execute(email_query, (user_id_tuple,))

        # Fetch rows and add email addresses to the dictionary
        for row in cur:
            user_emails[row[0]] = row[1]
    else:
        print("No users found in the workspace.")

    # Create an empty dictionary to store email addresses

    table_rows = []

    # Iterate over user IDs
    for user_id in workspace_user_ids:
        # Fetch email from user_emails dictionary
        user_email = user_emails.get(user_id, "Email Not Found")
        # Get prospect counts for the user
        prospect_count_email = user_prospect_counts_email.get(user_id, 0)
        prospect_count_disc = user_prospect_counts_disc.get(user_id, 0)
        prospect_count_icebreaker = user_prospect_counts_icebreaker.get(user_id, 0)
        prospect_count_pitch = user_prospect_counts_pitch.get(user_id, 0)
        prospect_count_scripts = user_prospect_counts_scripts.get(user_id, 0)

        # Append row to the table
        # print(user_id, user_email, prospect_count_email, prospect_count_disc)
        table_rows.append([
            user_id,
            user_email,
            prospect_count_email,
            prospect_count_disc,
            prospect_count_icebreaker,
            prospect_count_pitch,
            prospect_count_scripts
        ])

    # Create a DataFrame from the table rows
    table_df = pd.DataFrame(table_rows, columns=["User Id", "User Email", "# Email generated", "# DISC generated", "# Icebreaker Generated", "# Pitch Generated", "# Call Scripts Generated"])

    st.dataframe(table_df)

if st.session_state["authentication_status"]:
    extract_workspace_id()

else:
    st.write("this is a protected route, login to access this route")