import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Setup Data (Storytelling Prep)
def load_and_prep_data():
    # Load data from csv
    df = pd.read_csv('data/mp_olympics_medals.csv')
    
    # Ensure date is a datetime object to sort chronologically
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Extract Year
    df['Year'] = df['Date'].dt.year
    
    # Create a cumulative count of medals over time
    df['Medal_Count'] = range(1, len(df) + 1)
    
    return df

# 2. Create the Storytelling Visual
def create_phelps_viz(df):
    # Animate by 'Date' to show the journey
    fig = px.scatter(
        df, 
        x="Date", 
        y="Medal_Count",
        animation_frame="Year", 
        color="Medal",
        hover_name="Event",
        size_max=20,
        title="The Path to 28: Michael Phelps' Medal Progression",
        labels={"Medal_Count": "Total Medals Earned", "Date": "Olympic Timeline"},
        template="plotly_dark",
        color_discrete_map={
            "Gold": "#FFD700", 
            "Silver": "#C0C0C0", 
            "Bronze": "#CD7F32"
        }
    )

    # Improve the "Story" by fixing the axes
    fig.update_layout(
        xaxis_range=[df['Date'].min(), df['Date'].max()],
        yaxis_range=[0, 30],
        showlegend=True
    )
    
    return fig

# 3. Streamlit Interface
def main():
    st.set_page_config(page_title="Phelps Olympic Journey", layout="wide")
    
    st.title("Michael Phelps: The Golden Narrative")
    st.markdown("""
    This interactive dashboard tells the story of the greatest Olympic run in history. 
    Use the **Play** button below the chart to watch the medals accumulate from 2004 to 2016.
    """)

    try:
        data = load_and_prep_data()
        
        # Sidebar metrics for storytelling
        st.sidebar.header("Career Snapshot")
        st.sidebar.metric("Total Medals", "28")
        st.sidebar.metric("Gold Medals", "23")
        st.sidebar.write("---")
        st.sidebar.info("[World Aquatics – Official Records](https://www.worldaquatics.com/athletes/1001621/michael-phelps/medals)")

        # Display Visualization
        viz = create_phelps_viz(data)
        st.plotly_chart(viz, use_container_width=True)
        
        # Data Table Toggle
        if st.checkbox("Show Raw Medal Data"):
            st.dataframe(data)

    except FileNotFoundError:
        st.error("Please make sure 'mp_olympics_medals.csv' is in the same folder as this script!")

if __name__ == "__main__":
    main()