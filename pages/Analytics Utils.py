import streamlit as st
import pandas as pd
from collections import defaultdict
import global_vars 
# from ..app import authenticator

post_client = global_vars.post_client
mongo_client = global_vars.mongo_client

def avg_usr_per_ws():

    cur = post_client.cursor()
    cur.execute("SELECT COUNT(*) FROM workspace")
    count_workspaces = cur.fetchone()
    
    number_of_workspaces = count_workspaces[0]
    # st.write(number_of_workspaces)

    cur.execute("SELECT COUNT(*) FROM public.\"user\";")
    count_users= cur.fetchone()
    
    number_of_users = count_users[0]
    # st.write(number_of_users)
    
    st.write("Average number of users per workspace: {:.4f}".format(number_of_users / number_of_workspaces))


def avg_pros_per_ws():
    mongo_db = mongo_client["happysales"]

    collection = mongo_db["prospect"]
    
    number_of_prospects = collection.count_documents({})

    cur = post_client.cursor()
    cur.execute("SELECT COUNT(*) FROM workspace")
    count_workspaces = cur.fetchone()
    
    number_of_workspaces = count_workspaces[0]

    st.write("Average number of prospects per workspace = {:.4f}".format(number_of_prospects / number_of_workspaces))


def avg_pros_per_usr():

    mongo_db = mongo_client["happysales"]

    collection = mongo_db["prospect"]
    
    number_of_prospects = collection.count_documents({})

    cur = post_client.cursor()
    cur.execute("SELECT COUNT(*) FROM public.\"user\";")
    count_users= cur.fetchone()

    number_of_users = count_users[0]

    st.write("Average number of prospects per user = {:.4f}".format(number_of_prospects / number_of_users))

def users_category():

    pass

def avg_roleplay_per_user():
    
    mongo_db = mongo_client["happysales"]

    collection = mongo_db["practice_pitch"]

    number_of_roleplays = collection.count_documents({})

    cur = post_client.cursor()
    cur.execute("SELECT COUNT(*) FROM public.\"user\";")
    count_users= cur.fetchone()

    number_of_users = count_users[0]

    st.write("Average number of roleplays per user = {:.4f}".format(number_of_roleplays / number_of_users))


if 'authentication_status' in st.session_state and st.session_state["authentication_status"]:
    authenticator = st.session_state['authenticator']
    authenticator.logout()
    avg_usr_per_ws()
    avg_pros_per_ws()
    avg_pros_per_usr()
    avg_roleplay_per_user()
else:
    st.write("this is a protected route, login to access this route")