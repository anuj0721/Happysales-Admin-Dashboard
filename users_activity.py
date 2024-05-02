# Not useful right now

import streamlit as st
from dotenv import load_dotenv
from streamlit import write
from streamlit_authenticator import Authenticate 
from collections import defaultdict
from datetime import timedelta
import plotly.express as px

load_dotenv()

def weekly_active_users(mongo_client):

    mongo_db = mongo_client["happysales"]

    collection = mongo_db["user_prospect"]

    # Define the list of fields to check
    fields_to_check = [
        'used_prospect_insight', 'used_prospect_icebreaker',
        'used_organization_insight', 'used_organization_icebreaker',
        'used_email', 'used_key_challenges', 'used_disc'
    ]

    # Find documents with at least one field True
    cursor = collection.find({
        "$or": [
            {field: True} for field in fields_to_check
        ]
    })

    # Function to get the last day of the week (Sunday) for a given date
    def get_last_day_of_week(date):
        return date + timedelta(days=6 - date.weekday())

    # Initialize an empty dictionary to store documents by week
    weekly_user_counts  = defaultdict(set)

    # Process documents and count unique users per week
    for document in cursor:
    # Extract the created_at date
        created_at = document.get('created_at')
        if created_at:
            last_day_of_week = get_last_day_of_week(created_at.date()).strftime('%Y-%m-%d')
            # Add user_id to the set for unique users per week
            weekly_user_counts[last_day_of_week].add(document.get('user_id'))

    # Prepare data for the graph
    weeks = [week for week in weekly_user_counts.keys()]
    user_counts = [len(user_set) for user_set in weekly_user_counts.values()]  # Get set lengths

    # Check if any data was found
    if not weekly_user_counts:
        st.write("No documents found in the cursor.")
    else:
        # Create graph using plotly.express
        fig = px.line(x=weeks, y=user_counts, title="Weekly Active Unique Users")
        fig.update_xaxes(title_text="Last Day of Week")
        fig.update_yaxes(title_text="Number of Unique Users")
        st.plotly_chart(fig)


def monthly_active_users(mongo_client):
    mongo_db = mongo_client["happysales"]

    collection = mongo_db["user_prospect"]

    # Define the list of fields to check
    fields_to_check = [
        'used_prospect_insight', 'used_prospect_icebreaker',
        'used_organization_insight', 'used_organization_icebreaker',
        'used_email', 'used_key_challenges', 'used_disc'
    ]

    # Find documents with at least one field True
    cursor = collection.find({
        "$or": [
            {field: True} for field in fields_to_check
        ]
    })

    # Define a function to get the first day of the month
    def get_first_day_of_month(date):
        return date.replace(day=1)

    # Process documents and count unique users per month
    monthly_user_counts = defaultdict(set)
    
    for document in cursor:
        created_at = document.get("created_at")
        if created_at:
            first_day_of_month = get_first_day_of_month(created_at.date())
            # Format date as 'Month Year' for table header (e.g., 'January 2023')
            month_str = first_day_of_month.strftime('%B %Y')
            monthly_user_counts[month_str].add(document.get("user_id"))

    # Prepare data for the graph
    months = [month for month in monthly_user_counts.keys()]
    user_counts = [len(user_set) for user_set in monthly_user_counts.values()]  # Get set lengths

    # Check if any data was found
    if not monthly_user_counts:
        st.write("No documents found in the cursor.")
    else:
        # Create graph using plotly.express
        fig = px.line(x=months, y=user_counts, title="Monthly Active Unique Users")
        fig.update_xaxes(title_text="Month")
        fig.update_yaxes(title_text="Number of Unique Users")
        st.plotly_chart(fig)

def trend(mongo_client):
    
    st.header("Active Unique Users")
    # Set default state for toggle button (optional)
    default_graph = "Weekly Trend"  # Change this to "Graph 2" if you want Graph 2 to show by default

    show_graph_option = st.selectbox("Tracking Users Activity", ("Weekly Trend", "Monthly Trend"), index=([text for text, _ in enumerate([default_graph])] + [-1])[0])

    # Execute the selected function based on toggle button selection
    if show_graph_option == "Weekly Trend":
        weekly_active_users(mongo_client)
    else:
        monthly_active_users(mongo_client)