# Not useful right now

import streamlit as st
import pandas as pd
from streamlit import write
from collections import defaultdict
import plotly.express as px
import plotly.graph_objects as go

def organization_industry(mongo_client):

    mongo_db = mongo_client["happysales"]

    collection = mongo_db["organization"]

    cursor = collection.find({})

    organization_details = []

    organization_industry_counts = defaultdict(int)

    for organization in cursor:
        name = organization['name']
        organization_industry = organization['industry']
        organization_details.append([name, organization_industry])

        organization_industry_counts[organization_industry] += 1  # Increment count

    # Convert table_data to a pandas DataFrame
    df = pd.DataFrame(organization_details, columns=["Organization Name", "Organization Industry"])

    # Display table header
    st.header("Organizations using Happysales")

    # Display table using pandas DataFrame with Streamlit
    st.dataframe(df)

    
    # Prepare data for the pie chart
    organization_industry_types = list(organization_industry_counts.keys())  # Extract organization types
    organization_industry_counts = list(organization_industry_counts.values())  # Extract counts

    if organization_industry_types:  # Check if there are any organization types before creating the chart
        pie_chart = go.Figure(data=[go.Pie(labels=organization_industry_types, values=organization_industry_counts)])
        pie_chart.update_layout(
            title="Organization Industry Type Distribution",
            xaxis_title="Organization Industry Type",
            yaxis_title="Count",
        )
        st.plotly_chart(pie_chart)
    else:
        st.write("No organization data found to display the pie chart.")

def organization_size_range(mongo_client):

    mongo_db = mongo_client["happysales"]

    collection = mongo_db["organization"]

    cursor = collection.find({})

    size_range_counts = defaultdict(int)

    for organization in cursor:
        size = organization.get("company_size_on_linkedin")  # Use get() with default

        if size is not None and isinstance(size, int):  # Ensure size exists and is an integer
            if 1 <= size <= 10:
                size_range_counts["1-10"] += 1
            elif 11 <= size <= 50:
                size_range_counts["11-50"] += 1
            elif 51 <= size <= 200:
                size_range_counts["51-200"] += 1
            elif 201 <= size <= 500:
                size_range_counts["201-500"] += 1
            elif 501 <= size <= 1000:
                size_range_counts["501-1000"] += 1
            elif 1001 <= size <= 5000:
                size_range_counts["1001-5000"] += 1
            elif 5001 <= size <= 10000:
                size_range_counts["5001-10000"] += 1
            else:
                size_range_counts["10000+"] += 1  # Category for sizes above 10000

    # Prepare data for the pie chart (check if there are any counts before creating the chart)
    if size_range_counts:
        size_labels = list(size_range_counts.keys())
        size_values = list(size_range_counts.values())
        pie_chart = go.Figure(data=[go.Pie(labels=size_labels, values=size_values)])
        pie_chart.update_layout(
            title="Organization Size Distribution",
            xaxis_title="Size Range",
            yaxis_title="Count",
        )
        st.plotly_chart(pie_chart)
    else:
        st.write("No organization data found to display the pie chart.")
        
