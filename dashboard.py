import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from PIL import Image 

@st.cache_data
def load_data():
    # Load your dataset here
    data = pd.read_csv("data/kpi00.csv")
    return data

# Load data
data = load_data()

# Normalize data for SEI calculation
scaler = MinMaxScaler()
df_normalized = data[["Renewable_Energy_%", "Emissions_per_Unit", "Waste_Diversion_%"]].copy()
df_normalized[["Renewable_Energy_%", "Waste_Diversion_%"]] = scaler.fit_transform(
    df_normalized[["Renewable_Energy_%", "Waste_Diversion_%"]]
)

# Invert Emissions per Unit for efficiency (higher values indicate better sustainability)
df_normalized["Emissions_per_Unit"] = 1 - scaler.fit_transform(
    df_normalized[["Emissions_per_Unit"]]
)

# Define weights for each metric
weights = {
    "Renewable_Energy_%": 0.4,
    "Emissions_per_Unit": 0.3,  # Inverted
    "Waste_Diversion_%": 0.3,
}

# Calculate Sustainability Efficiency Index
data["SEI"] = (
    df_normalized["Renewable_Energy_%"] * weights["Renewable_Energy_%"]
    + df_normalized["Emissions_per_Unit"] * weights["Emissions_per_Unit"]
    + df_normalized["Waste_Diversion_%"] * weights["Waste_Diversion_%"]
)

# Streamlit App
st.title("Interactive Sustainability Dashboard")

#
# KPI Section
st.header("Key Performance Indicators (KPIs)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_sei = data['SEI'].mean()
    st.metric(label="Avg SEI", value=f"{avg_sei:.2f}")
with col2:
    avg_renewable = data['Renewable_Energy_%'].mean()
    st.metric(label="Avg Renewable Energy (%)", value=f"{avg_renewable:.2f}")
with col3:
    avg_emissions = data['Emissions_per_Unit'].mean()
    st.metric(label="Avg Emissions Intensity", value=f"{avg_emissions:.2f} kg CO2/unit")
with col4:
    avg_waste = data['Waste_Diversion_%'].mean()
    st.metric(label="Avg Waste Diversion (%)", value=f"{avg_waste:.2f}")


# Weight Adjustment Sliders
st.sidebar.header("Adjust SEI Component Weights")
renewable_weight = st.sidebar.slider("Renewable Energy Weight", 0.0, 1.0, weights["Renewable_Energy_%"], 0.1)
emissions_weight = st.sidebar.slider("Emissions Intensity Weight", 0.0, 1.0,weights["Emissions_per_Unit"] , 0.1)
waste_weight = st.sidebar.slider("Waste Diversion Weight", 0.0, 1.0, weights["Waste_Diversion_%"], 0.1)

# Ensure weights sum to 1
total_weight = weights["Renewable_Energy_%"] + weights["Emissions_per_Unit"]+ weights["Waste_Diversion_%"]
if total_weight != 1.0:
    renewable_weight /= total_weight
    emissions_weight /= total_weight
    waste_weight /= total_weight


# Recalculate SEI
data['SEI'] = (df_normalized["Renewable_Energy_%"] * weights["Renewable_Energy_%"]
    + df_normalized["Emissions_per_Unit"] * weights["Emissions_per_Unit"]
    + df_normalized["Waste_Diversion_%"] * weights["Waste_Diversion_%"]
)



# Trend Analysis
st.header("Trend Analysis")

# SEI Trend
st.subheader("Sustainability Efficiency Index Trend")
st.line_chart(data.set_index('Month')['SEI'])


# Component Trends
st.subheader("Component Trends")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(data['Month'], data['Renewable_Energy_%'], label='Renewable Energy Usage (%)', marker='o')
ax.plot(data['Month'], data['Waste_Diversion_%'], label='Waste Diversion Rate (%)', marker='o')
ax.set_title("Trends in SEI Components")
ax.set_xlabel("Month")
ax.set_ylabel("Value")
ax.legend()
st.pyplot(fig)

# Plot Emissions per Unit
st.image(Image.open("data/emission_per_unit.png"))

