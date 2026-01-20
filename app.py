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
    """Create an animated stacked bar chart showing medal accumulation by Olympics."""
    
    # Group medals by year and medal type
    medal_counts = df.groupby(['Year', 'Medal']).size().unstack(fill_value=0)
    medal_counts = medal_counts.reindex(columns=['Gold', 'Silver', 'Bronze'], fill_value=0)
    
    # Create cumulative totals
    years = sorted(df['Year'].unique())
    
    frames = []
    for i, year in enumerate(years):
        cumulative = medal_counts.loc[:year].sum()
        frames.append({
            'Year': year,
            'Gold': cumulative.get('Gold', 0),
            'Silver': cumulative.get('Silver', 0),
            'Bronze': cumulative.get('Bronze', 0)
        })
    
    frame_df = pd.DataFrame(frames)
    
    # Create the animated figure
    fig = go.Figure()
    
    colors = {'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
    
    # Add traces for each medal type
    for medal in ['Bronze', 'Silver', 'Gold']:
        fig.add_trace(go.Bar(
            name=medal,
            x=[str(years[0])],
            y=[frame_df.iloc[0][medal]],
            marker_color=colors[medal],
            text=[int(frame_df.iloc[0][medal])],
            textposition='inside',
            textfont=dict(size=14, color='#1a1a1a', family='Source Sans Pro')
        ))
    
    # Create animation frames
    animation_frames = []
    for i, row in frame_df.iterrows():
        x_vals = [str(y) for y in years[:i+1]]
        
        frame_data = []
        for medal in ['Bronze', 'Silver', 'Gold']:
            y_vals = list(frame_df.iloc[:i+1][medal])
            frame_data.append(go.Bar(
                x=x_vals,
                y=y_vals,
                text=[int(v) if v > 0 else '' for v in y_vals],
                textposition='inside'
            ))
        
        animation_frames.append(go.Frame(data=frame_data, name=str(row['Year'])))
    
    fig.frames = animation_frames
    
    # Layout with play button
    fig.update_layout(
        barmode='stack',
        title=dict(
            text='Medal Count Growing Through Each Olympics',
            font=dict(size=22, color='#e8e8e8', family='Source Sans Pro'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text='Olympic Year', font=dict(size=16, color='#e8e8e8')),
            tickfont=dict(size=14, color='#c9d6df'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title=dict(text='Cumulative Medal Count', font=dict(size=16, color='#e8e8e8')),
            range=[0, 30],
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
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            y=1.15,
            x=0.5,
            xanchor='center',
            buttons=[
                dict(
                    label='▶ Play Journey',
                    method='animate',
                    args=[None, {
                        'frame': {'duration': 1500, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 800, 'easing': 'cubic-in-out'}
                    }]
                ),
                dict(
                    label='⏸ Pause',
                    method='animate',
                    args=[[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                )
            ]
        )],
        height=500
    )
    
    return fig


def create_event_type_histogram(df):
    """Create a histogram showing individual vs team medals."""
    
    type_counts = df['Event_Type'].value_counts()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=type_counts.index,
        y=type_counts.values,
        marker=dict(
            color=['#00b4d8', '#ffd700'],
            line=dict(color='rgba(255,255,255,0.3)', width=2)
        ),
        text=type_counts.values,
        textposition='outside',
        textfont=dict(size=18, color='#e8e8e8', family='Source Sans Pro')
    ))
    
    fig.update_layout(
        title=dict(
            text='Individual vs Team Relay Medals',
            font=dict(size=22, color='#e8e8e8', family='Source Sans Pro'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text='Event Type', font=dict(size=16, color='#e8e8e8')),
            tickfont=dict(size=14, color='#c9d6df')
        ),
        yaxis=dict(
            title=dict(text='Number of Medals', font=dict(size=16, color='#e8e8e8')),
            range=[0, max(type_counts.values) + 3],
            tickfont=dict(size=14, color='#c9d6df'),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False
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
        st.markdown("*Press Play to watch the medals stack up through each Olympic Games*")
        
        stacked_chart = create_cumulative_stacked_chart(data)
        st.plotly_chart(stacked_chart, use_container_width=True)
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # ============ INDIVIDUAL VS TEAM HISTOGRAM ============
        st.markdown("### Solo Glory vs Team Triumph")
        st.markdown("*How many medals came from individual events versus relay teams?*")
        
        histogram = create_event_type_histogram(data)
        st.plotly_chart(histogram, use_container_width=True)
        
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
