# Needs to be discussed with Aby


import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from streamlit import write
from streamlit_authenticator import Authenticate 
from collections import defaultdict
from datetime import timedelta
import plotly.express as px

def features_usage(mongo_client):
    mongo_db = mongo_client["happysales"]

    collection = mongo_db["user_prospect"]

    # Initialize counters
    prospect_insight, prospect_icebreaker, email, disc, key_challenges, pitch, organization_insight = 0, 0, 0, 0, 0, 0, 0

    # Iterate through documents
    for document in collection.find():
    # Check for used fields and increment counters
        if document["used_prospect_insight"] == True:
            prospect_insight += 1
        if document["used_prospect_icebreaker"] == True:
            prospect_icebreaker += 1
        if document["used_email"] == True:
            email += (len(document.get("emails", [])) / 3)
        if document["used_disc"] == True:
            disc += 1
        if document["used_key_challenges"] == True:
            key_challenges += 1
            pitch += 1
        if document["used_organization_insight"] == True:
            organization_insight += 1

    # Print the counts
    st.write("Prospect Insight Usage:", prospect_insight)
    st.write("Prospect Icebreaker Usage:", prospect_icebreaker)
    st.write("Email Usage:", email)
    st.write("DISC Usage:", disc)
    st.write("Key Challanges Usage:", key_challenges)
    st.write("Prospect Pitch Usage:", pitch)
    st.write("Organization Insight Usage:", organization_insight)

    # Prepare data for pie chart
    labels = ['Prospect Insight', 'Prospect Icebreaker', 'Email', 'DISC', 'Key Challenges', 'Prospect Pitch', 'Organization Insight']
    sizes = [prospect_insight, prospect_icebreaker, email, disc, key_challenges, pitch, organization_insight]

    # Create pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Display the chart using Streamlit
    st.pyplot(fig)