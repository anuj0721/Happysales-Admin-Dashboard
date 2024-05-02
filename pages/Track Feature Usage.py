import streamlit as st
import global_vars
import plotly.graph_objects as go

post_client = global_vars.post_client
mongo_client = global_vars.mongo_client

def features_usage():
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
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3)])

    # Update layout for better presentation
    fig.update_layout(
        title_text="Feature Utilization Distribution",
        title_font_size=24,
        title_x=0.5,
        annotations=[dict(text='', x=0.5, y=0.5, font_size=20, showarrow=False)],
    )

    # Display the chart using Streamlit
    st.plotly_chart(fig)

if st.session_state["authentication_status"]:
    features_usage()

else:
    st.write("this is a protected route, login to access this route")