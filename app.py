import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page config
st.set_page_config(
    page_title="Michael Phelps: Path to Gold", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for blog-post styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+Pro:wght@400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 50%, #0d1b2a 100%);
    }
    
    h1 {
        font-family: 'Playfair Display', serif !important;
        color: #ffd700 !important;
        text-align: center;
        font-size: 3.5rem !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        margin-bottom: 0 !important;
    }
    
    h2, h3 {
        font-family: 'Source Sans Pro', sans-serif !important;
        color: #e8e8e8 !important;
    }
    
    p, .stMarkdown {
        font-family: 'Source Sans Pro', sans-serif !important;
        color: #c9d6df !important;
        font-size: 1.1rem;
        line-height: 1.7;
    }
    
    .hero-caption {
        text-align: center;
        font-style: italic;
        color: #8899a6 !important;
        margin-top: -10px;
        margin-bottom: 40px;
    }
    
    .stat-box {
        background: rgba(255,215,0,0.1);
        border-left: 4px solid #ffd700;
        padding: 15px 20px;
        margin: 20px 0;
        border-radius: 0 8px 8px 0;
    }
    
    .section-divider {
        border: 0;
        height: 1px;
        background: linear-gradient(to right, transparent, #ffd700, transparent);
        margin: 50px 0;
    }
</style>
""", unsafe_allow_html=True)


def load_and_prep_data():
    """Load and prepare the medal data."""
    df = pd.read_csv("mp_olympics_medals_data.csv")
    
    # Filter out non-medal performances
    df = df[df['Medal'].isin(['Gold', 'Silver', 'Bronze'])].copy()
    
    # Add event type classification
    df['Event_Type'] = df['Event'].apply(
        lambda x: 'Team (Relay)' if 'Relay' in x else 'Individual'
    )
    
    return df


def create_cumulative_stacked_chart(df):
    """Create a simple stacked bar chart showing medals per Olympics."""
    
    # Group medals by year and medal type
    medal_counts = df.groupby(['Year', 'Medal']).size().reset_index(name='Count')
    
    # Add 2000 Olympics with 0 medals (Phelps competed but didn't medal)
    row_2000 = pd.DataFrame({'Year': [2000], 'Medal': ['None'], 'Count': [0]})
    medal_counts = pd.concat([row_2000, medal_counts], ignore_index=True)
    
    # Create stacked bar chart
    fig = px.bar(
        medal_counts,
        x='Year',
        y='Count',
        color='Medal',
        color_discrete_map={'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32', 'None': '#4a5568'},
        category_orders={'Medal': ['None', 'Bronze', 'Silver', 'Gold']},
        text='Count'
    )
    
    fig.update_traces(textposition='inside', textfont=dict(size=14, color='#1a1a1a'))
    
    # Add annotation for 2000
    fig.add_annotation(
        x=2000, y=0.5,
        text="5th place",
        showarrow=False,
        font=dict(size=12, color='#8899a6'),
        yshift=15
    )
    
    fig.update_layout(
        xaxis=dict(
            title=dict(text='Olympic Year', font=dict(size=16, color='#e8e8e8')),
            tickfont=dict(size=14, color='#c9d6df'),
            tickmode='array',
            tickvals=[2000, 2004, 2008, 2012, 2016]
        ),
        yaxis=dict(
            title=dict(text='Medal Count', font=dict(size=16, color='#e8e8e8')),
            tickfont=dict(size=14, color='#c9d6df'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='#e8e8e8', size=14),
            title=None
        ),
        height=450,
        bargap=0.3
    )
    
    return fig


def time_to_seconds(time_str):
    """Convert time string (e.g., '1:52.03' or '50.58') to seconds."""
    time_str = str(time_str).strip()
    if ':' in time_str:
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        return float(time_str)


def create_butterfly_time_chart():
    """Create a line chart showing time improvement in butterfly events."""
    
    # Load full data (including 2000 non-medal performance)
    df = pd.read_csv("mp_olympics_medals_data.csv")
    
    # Filter for butterfly events
    butterfly_df = df[df['Event'].isin(['Men 100 Butterfly', 'Men 200 Butterfly'])].copy()
    
    # Convert time to seconds
    butterfly_df['Time_Seconds'] = butterfly_df['Time'].apply(time_to_seconds)
    
    fig = go.Figure()
    
    colors = {'Men 200 Butterfly': '#ffd700', 'Men 100 Butterfly': '#00b4d8'}
    symbols = {'Men 200 Butterfly': 'circle', 'Men 100 Butterfly': 'diamond'}
    
    for event in ['Men 200 Butterfly', 'Men 100 Butterfly']:
        event_data = butterfly_df[butterfly_df['Event'] == event].sort_values('Year')
        
        # Format label
        label = '200m Butterfly' if '200' in event else '100m Butterfly'
        
        fig.add_trace(go.Scatter(
            x=event_data['Year'],
            y=event_data['Time_Seconds'],
            mode='lines+markers+text',
            name=label,
            line=dict(color=colors[event], width=3),
            marker=dict(size=12, symbol=symbols[event], line=dict(width=2, color='white')),
            text=event_data['Time'],
            textposition='top center',
            textfont=dict(size=11, color='#e8e8e8'),
            hovertemplate='<b>%{text}</b><br>Year: %{x}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text='Butterfly Event Times Across Olympics',
            font=dict(size=22, color='#e8e8e8', family='Source Sans Pro'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text='Olympic Year', font=dict(size=16, color='#e8e8e8')),
            tickfont=dict(size=14, color='#c9d6df'),
            tickmode='array',
            tickvals=[2000, 2004, 2008, 2012, 2016],
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text='Time (seconds)', font=dict(size=16, color='#e8e8e8')),
            tickfont=dict(size=14, color='#c9d6df'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='#e8e8e8', size=14)
        ),
        height=450
    )
    
    return fig


def main():
    # ============ HERO SECTION ============
    st.title("Michael Phelps - Path to Gold")
    
    # Center the hero image
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("mp_photo_london_2012.pmg.png", use_container_width=True)
        st.markdown('<p class="hero-caption">London 2012 — The greatest Olympian of all time</p>', 
                    unsafe_allow_html=True)
    
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # ============ INTRO TEXT ============
    st.markdown("""
    <div class="stat-box">
        <strong>28 Olympic Medals</strong>
        <strong>>> 23 Gold + 3 Silver + 2 Bronze</strong><br>
        A record that may never be broken.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    From a 15-year-old in Sydney 2000 to the Olympian legendin, Michael Phelps' journey through five Olympic Games is amazing to study.
    """)
    
    # Comparison panorama - other great athletes
    st.image("great_athlets_image_gemini_generate.png", use_container_width=True)
    st.markdown('<p class="hero-caption">How Phelps compares to other legendary Olympic athletes</p>', 
                unsafe_allow_html=True)
    
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # ============ LOAD DATA ============
    try:
        data = load_and_prep_data()
        
        # ============ STACKED MEDAL CHART ============
        st.markdown("### The Medal Journey")
        st.markdown("*Medals won at each Olympic Games*")
        
        stacked_chart = create_cumulative_stacked_chart(data)
        st.plotly_chart(stacked_chart, use_container_width=True)
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # ============ BUTTERFLY TIME IMPROVEMENT ============
        st.markdown("### Chasing Faster Times")
        st.markdown("*Watch how Phelps' butterfly times evolved — lower is faster!*")
        
        butterfly_chart = create_butterfly_time_chart()
        st.plotly_chart(butterfly_chart, use_container_width=True)
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # ============ DATA PREVIEW ============
        st.markdown("### 📋 Full Medal Record")
        if st.button("📂 Show Medal Data", type="secondary"):
            st.dataframe(
                data[['Year', 'Event', 'Medal', 'Time', 'Note', 'Event_Type']],
                use_container_width=True,
                hide_index=True
            )
        
        # Footer
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align: center; color: #5c6b7a; font-size: 0.9rem;">
            Data source: <a href="https://www.worldaquatics.com/athletes/1001621/michael-phelps/medals" 
            style="color: #ffd700;">World Aquatics Official Records</a>
        </p>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error("⚠️ Could not find 'mp_olympics_medals_data.csv'. Please ensure it's in the same folder as this script.")


if __name__ == "__main__":
    main()
