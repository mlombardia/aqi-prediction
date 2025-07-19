import streamlit as st
import hopsworks
import joblib
import os

st.set_page_config(page_title="Predicción AQI", layout="centered")

st.title("🌫️ Predicción de Calidad del Aire (AQI)")
st.subheader("Predicción para las próximas 3 horas")

# --- Conectarse a Hopsworks ---
project = hopsworks.login(api_key_value="Wklr8oC6waerfZ3D.DhSAXrdLrJbhi83E6M7QpuiDCee5XsEMroKPzEc68z3zgQibHWp7o8wYsaKoNoad")
fs = project.get_feature_store()
mr = project.get_model_registry()

# --- Leer el último feature registrado ---
fg = fs.get_feature_group("aqi_data", version=1)
df = fg.read()

# --- Usar el último registro como input ---
latest = df.sort_values("timestamp", ascending=False).iloc[0:1]

# --- Preparar features (mismos usados en el modelo) ---
feature_columns = [
    'co', 'h', 'no2', 'o3', 'p', 'pm10', 'pm25', 'so2', 't', 'aqi'
]
X_pred = latest[feature_columns]

# --- Cargar el modelo desde el Model Registry ---
model = mr.get_model("aqi_predictor", version=1)
model_dir = model.download()
model_path = os.path.join(model_dir, "aqi_model.pkl")
loaded_model = joblib.load(model_path)

# --- Hacer la predicción ---
prediction = loaded_model.predict(X_pred)[0]

# --- Mostrar resultado ---
st.metric("Predicción de AQI (+3h)", f"{prediction:.2f}")

# --- Info extra opcional ---
with st.expander("🔎 Ver últimas mediciones"):
    st.dataframe(latest[['timestamp'] + feature_columns])