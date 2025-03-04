import streamlit as st
import pint
from datetime import datetime
import json
import os
import plotly.graph_objects as go
import pandas as pd

# Initialize unit registry
ureg = pint.UnitRegistry()

# Define conversion categories with emojis and units
CATEGORIES = {
    "📏 Length": ["meters", "kilometers", "miles", "feet", "inches", "centimeters", "yards", "nautical_miles"],
    "⚖️ Weight": ["kilograms", "grams", "pounds", "ounces", "tons", "milligrams"],
    "🌡️ Temperature": ["celsius", "fahrenheit", "kelvin", "rankine"],
    "⏰ Time": ["seconds", "minutes", "hours", "days", "weeks", "months", "years"],
    "🧊 Volume": ["liters", "milliliters", "gallons", "cubic_meters", "cups", "tablespoons", "teaspoons"],
    "🚀 Speed": ["meters_per_second", "kilometers_per_hour", "miles_per_hour", "knots"],
    "💾 Data": ["bytes", "kilobytes", "megabytes", "gigabytes", "terabytes", "petabytes"],
    "📡 Frequency": ["hertz", "kilohertz", "megahertz", "gigahertz", "terahertz"],
    "🔋 Energy": ["joules", "kilojoules", "calories", "kilocalories", "watt_hours", "electron_volts"],
    "⚡ Power": ["watts", "kilowatts", "megawatts", "horsepower", "btu_per_hour"],
    "📐 Area": ["square_meters", "square_kilometers", "acres", "hectares", "square_feet", "square_yards", "square_miles"],
    "🔩 Pressure": ["pascals", "bar", "atmospheres", "psi", "torr", "millibars"],
    "🎛️ Electrical": ["volts", "amperes", "ohms", "farads", "henries", "siemens"],
    "🌀 Torque": ["newton_meters", "pound_feet", "kilogram_force_meters"],
    "📉 Density": ["kilograms_per_cubic_meter", "grams_per_cubic_centimeter", "pounds_per_cubic_foot"],
    "💨 Airflow": ["cubic_meters_per_second", "cubic_feet_per_minute", "liters_per_minute"],
    "💰 Currency": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY"]
}

# Define conversion formulas
CONVERSION_FORMULAS = {
    "temperature": {
        "celsius_to_fahrenheit": "°F = (°C × 9/5) + 32",
        "fahrenheit_to_celsius": "°C = (°F - 32) × 5/9",
        "celsius_to_kelvin": "K = °C + 273.15",
        "kelvin_to_celsius": "°C = K - 273.15"
    }
}

def format_unit(unit: str) -> str:
    """Format unit name for display"""
    return unit.replace("_", " ").title()

def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """Convert value between units"""
    try:
        # Input validation
        if not isinstance(value, (int, float)):
            st.error("Please enter a valid number")
            return None
            
        # Special handling for temperature
        if from_unit in ["celsius", "fahrenheit", "kelvin", "rankine"]:
            if from_unit == "celsius":
                kelvin = value + 273.15
            elif from_unit == "fahrenheit":
                kelvin = (value + 459.67) * 5/9
            elif from_unit == "rankine":
                kelvin = value * 5/9
            else:
                kelvin = value
            
            if to_unit == "celsius":
                return kelvin - 273.15
            elif to_unit == "fahrenheit":
                return kelvin * 9/5 - 459.67
            elif to_unit == "rankine":
                return kelvin * 9/5
            else:
                return kelvin
        
        # All other conversions
        try:
            quantity = value * ureg(from_unit)
            result = quantity.to(to_unit)
            return float(result.magnitude)
        except Exception as e:
            st.error(f"Invalid unit combination: {from_unit} to {to_unit}")
            return None
            
    except Exception as e:
        st.error(f"Conversion Error: {str(e)}")
        return None

def save_conversion_history(value: float, from_unit: str, to_unit: str, result: float):
    """Save conversion to history"""
    if 'conversion_history' not in st.session_state:
        st.session_state.conversion_history = []
    
    history_item = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'value': value,
        'from_unit': from_unit,
        'to_unit': to_unit,
        'result': result
    }
    
    st.session_state.conversion_history.insert(0, history_item)
    if len(st.session_state.conversion_history) > 10:  # Keep only last 10 conversions
        st.session_state.conversion_history.pop()

def toggle_favorite(from_unit: str, to_unit: str):
    """Toggle favorite conversion"""
    if 'favorites' not in st.session_state:
        st.session_state.favorites = set()
    
    conversion_pair = f"{from_unit}->{to_unit}"
    if conversion_pair in st.session_state.favorites:
        st.session_state.favorites.remove(conversion_pair)
    else:
        st.session_state.favorites.add(conversion_pair)

def create_conversion_visualization(value: float, from_unit: str, to_unit: str, result: float):
    """Create a visualization of the conversion"""
    try:
        fig = go.Figure()
        
        # Add bars for original and converted values
        fig.add_trace(go.Bar(
            name='Original',
            x=[format_unit(from_unit)],
            y=[value],
            marker_color='#2E7D32'
        ))
        
        fig.add_trace(go.Bar(
            name='Converted',
            x=[format_unit(to_unit)],
            y=[result],
            marker_color='#81C784'
        ))
        
        fig.update_layout(
            title='Conversion Visualization',
            barmode='group',
            height=300,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white' if st.session_state.get('theme', 'dark') == 'dark' else 'black')
        )
        
        return fig
    except Exception as e:
        st.error(f"Visualization Error: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Unique Unit Converter",
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state for theme
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    
    # Theme toggle in sidebar
    with st.sidebar:
        st.markdown("### Theme Settings")
        if st.checkbox('🌙 Dark Mode', value=st.session_state.theme == 'dark'):
            st.session_state.theme = 'dark'
        else:
            st.session_state.theme = 'light'
    
    # Custom CSS based on theme
    st.markdown(f"""
        <style>
        /* Main theme colors */
        :root {{
            --primary-color: #2E7D32;
            --secondary-color: #1B5E20;
            --accent-color: #81C784;
            --text-color: {'white' if st.session_state.theme == 'dark' else 'black'};
            --bg-color: {'#000000' if st.session_state.theme == 'dark' else '#FFFFFF'};
            --card-bg: {'#1A1A1A' if st.session_state.theme == 'dark' else '#F0F0F0'};
            --text-weight: {'bold' if st.session_state.theme == 'dark' else 'normal'};
        }}
        
        /* Global styles */
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: var(--text-weight);
        }}
        
        /* Streamlit specific styles */
        .stApp {{
            background-color: var(--bg-color);
            color: var(--text-color);
        }}
        
        .stMarkdown {{
            color: var(--text-color);
            font-weight: var(--text-weight);
        }}
        
        .stSelectbox label, .stNumberInput label {{
            color: var(--text-color);
            font-weight: var(--text-weight);
        }}
        
        /* Header styling */
        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            color: var(--text-color);
            font-size: 2.5rem;
            text-align: center;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            font-weight: var(--text-weight);
        }}
        
        /* Card styling */
        .stCard {{
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .stCard h3 {{
            color: var(--text-color);
            font-weight: var(--text-weight);
        }}
        
        .stCard li {{
            color: var(--text-color);
            font-weight: var(--text-weight);
        }}
        
        /* Input styling */
        .stNumberInput input {{
            background-color: var(--card-bg);
            color: var(--text-color);
            border: 2px solid var(--accent-color);
            border-radius: 8px;
            padding: 0.5rem;
            font-weight: var(--text-weight);
        }}
        
        /* Selectbox styling */
        .stSelectbox select {{
            background-color: var(--card-bg);
            color: var(--text-color);
            border: 2px solid var(--accent-color);
            border-radius: 8px;
            font-weight: var(--text-weight);
        }}
        
        /* Button styling */
        .stButton>button {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: var(--text-color);
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: bold;
            transition: all 0.3s ease;
            width: 100%;
        }}
        
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        
        /* Result display */
        .result-container {{
            background: linear-gradient(135deg, var(--card-bg), var(--bg-color));
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 1rem;
            text-align: center;
        }}
        
        .result-text {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent-color);
        }}
        
        /* Footer styling */
        .footer {{
            text-align: center;
            padding: 1rem;
            margin-top: 2rem;
            color: var(--accent-color);
            font-weight: var(--text-weight);
        }}
        
        /* Additional dark mode specific styles */
        {f'''
        .stMarkdown {{
            color: var(--text-color);
            font-weight: var(--text-weight);
        }}
        
        .stSelectbox label {{
            color: var(--text-color);
            font-weight: var(--text-weight);
        }}
        
        .stNumberInput label {{
            color: var(--text-color);
            font-weight: var(--text-weight);
        }}
        ''' if st.session_state.theme == 'dark' else ''}
        
        /* Search input styling */
        .stTextInput input {{
            background-color: var(--card-bg);
            color: var(--text-color);
            border: 2px solid var(--accent-color);
            border-radius: 8px;
            padding: 0.5rem;
            font-weight: var(--text-weight);
        }}
        
        .stTextInput label {{
            color: var(--text-color);
            font-weight: var(--text-weight);
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="header">
            <h1>🔄 Ultimate Unit Converter</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Search box for units
        search_query = st.text_input("🔍 Search Units", "").lower()
        
        # Filter categories based on search
        filtered_categories = {
            k: v for k, v in CATEGORIES.items()
            if search_query in k.lower() or any(search_query in unit.lower() for unit in v)
        }
        
        if not filtered_categories:
            st.warning("No units found matching your search.")
        else:
            # Main conversion interface
            category = st.selectbox("Select Category", options=list(filtered_categories.keys()))
            units = filtered_categories[category]
            
            # Create two columns for unit selection
            unit_col1, unit_col2 = st.columns(2)
            
            with unit_col1:
                from_unit = st.selectbox("From Unit", options=units, format_func=format_unit)
            with unit_col2:
                to_unit = st.selectbox("To Unit", options=units, format_func=format_unit)
            
            # Input validation for number input
            try:
                input_value = st.number_input("Enter Value", value=0.0, format="%f", min_value=None, max_value=None)
            except ValueError:
                st.error("Please enter a valid number")
                input_value = 0.0
            
            # Favorite toggle
            conversion_pair = f"{from_unit}->{to_unit}"
            is_favorite = conversion_pair in st.session_state.get('favorites', set())
            if st.button("⭐ " + ("Remove from Favorites" if is_favorite else "Add to Favorites")):
                toggle_favorite(from_unit, to_unit)
                st.rerun()
            
            if st.button("Convert", key="convert_button"):
                result = convert_units(input_value, from_unit, to_unit)
                if result is not None:
                    # Save to history
                    save_conversion_history(input_value, from_unit, to_unit, result)
                    
                    # Display result
                    st.markdown(f"""
                        <div class="result-container">
                            <div class="result-text">
                                {input_value} {format_unit(from_unit)} = {result:.6g} {format_unit(to_unit)}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show conversion formula if available
                    if category == "🌡️ Temperature":
                        formula_key = f"{from_unit}_to_{to_unit}"
                        if formula_key in CONVERSION_FORMULAS["temperature"]:
                            st.info(f"Formula: {CONVERSION_FORMULAS['temperature'][formula_key]}")
                    
                    # Show visualization with error handling
                    fig = create_conversion_visualization(input_value, from_unit, to_unit, result)
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sidebar information
        st.markdown("""
            <div class="stCard">
                <h3>📊 Quick Tips</h3>
                <ul>
                    <li>Select your category first</li>
                    <li>Choose source and target units</li>
                    <li>Enter the value to convert</li>
                    <li>Click Convert to see results</li>
                    <li>Use the search box to find units quickly</li>
                    <li>Toggle dark/light mode for comfort</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        # Favorites section
        if 'favorites' in st.session_state and st.session_state.favorites:
            st.markdown("""
                <div class="stCard">
                    <h3>⭐ Favorites</h3>
                    <ul>
            """, unsafe_allow_html=True)
            
            for fav in st.session_state.favorites:
                from_unit, to_unit = fav.split('->')
                st.markdown(f"<li>{format_unit(from_unit)} → {format_unit(to_unit)}</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)
        
        # Conversion history
        if 'conversion_history' in st.session_state and st.session_state.conversion_history:
            st.markdown("""
                <div class="stCard">
                    <h3>📜 Recent Conversions</h3>
                    <ul>
            """, unsafe_allow_html=True)
            
            for conv in st.session_state.conversion_history:
                st.markdown(f"""
                    <li>
                        {conv['value']} {format_unit(conv['from_unit'])} → {conv['result']:.2g} {format_unit(conv['to_unit'])}
                        <br>
                        <small>{conv['timestamp']}</small>
                    </li>
                """, unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="stCard">
                <h3>Last Updated</h3>
                <p>{}</p>
            </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div class="footer">
            <p>Made with Saima ❤️ using Streamlit | Your Unique Conversion Companion</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()







