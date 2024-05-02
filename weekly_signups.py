# completed, Please don't mess with this file.

import streamlit as st
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timedelta
import plotly.graph_objects as go

load_dotenv()

def signups_by_week(postgresql_connection):

    post_client = postgresql_connection

    # # Define query to fetch created_at values (replace 'created_at' with actual column name)
    query = "SELECT created_at FROM public.\"user\";"

    cursor = post_client.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Extract created_at values into a list
    created_at_list = []
    for row in results:
        # Check if created_at is already a datetime object
        if not isinstance(row[0], datetime):
            # If not, convert it using strptime (assuming format is known)
            created_at_list.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))  # Adjust format string if needed
        else:
            # If it's already datetime, append directly
            created_at_list.append(row[0])

    # Sort the list in-place using sorted()
    created_at_list.sort()

    # Create a list to store dates only
    dates_list = []
    for created_at in created_at_list:
        # Extract date part using .date()
        date_only = created_at.date()
        dates_list.append(date_only)

    # # Define a function to get the last day of the week
    def get_last_day_of_week(date):
        weekday = date.weekday()  # 0 (Monday) to 6 (Sunday)
        return date + timedelta(days=6 - weekday)  # Move to Sunday of the same week

    # # # Count dates in each week
    weekly_signup_counts = defaultdict(int)
    for date in dates_list:
        last_day_of_week = get_last_day_of_week(date)               # data type of last_day_of_week = <class 'datetime.date'>
        weekly_signup_counts[last_day_of_week] += 1

    # Prepare data for plotting (x-axis: last weekend dates (Sundays), y-axis: signup count)
    weekend_dates = [last_day_of_week.strftime('%Y-%m-%d') for last_day_of_week in weekly_signup_counts.keys()]
    signup_counts = list(weekly_signup_counts.values())

    # Create the line plot with hover annotations
    fig = go.Figure()

    # Plot the data with markers
    line = fig.add_trace(go.Scatter(
        x=weekend_dates,
        y=signup_counts,
        mode='lines+markers',  # Combine line and markers
        marker=dict(size=5),  # Adjust marker size
        line=dict(width=2),  # Adjust line width
        name="Signups"
    ))

    st.header("Weekly Signup Trend")

    # Create hover template for annotations
    hover_template = ("Week Ending: %{x}<br>"
                    "Signups: %{y}")

    # Add labels and title
    fig.update_layout(
        xaxis_title="Week Ending On (Sunday)",
        yaxis_title="Number of Signups",
        title="Signups per Week (Grouped by Weekend)",
        legend_title_text="Legend",  # Customize legend title
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)