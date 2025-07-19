import hopsworks
import os
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import joblib
import shutil

def train_model():
    project = hopsworks.login(api_key_value=os.environ['HOPSWORKS_API_TOKEN'])
    feature_store = project.get_feature_store()
    fg = feature_store.get_feature_group("aqi_data", version=1)
    df = fg.read()
    print(f"DataFrame shape: {df.shape}")
    df['aqi_future'] = df['aqi'].shift(-3)

    df = df.dropna(subset=['aqi_future'])

    feature_columns = [
        'co', 'h', 'no2', 'o3', 'p', 'pm10', 'pm25', 'so2', 't', 'aqi'
    ]

    X = df[feature_columns]
    y = df['aqi_future']


    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

    model = XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"prediction length: {len(y_pred)}")
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"predictions: {y_pred}")
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")

    os.makedirs("model_output", exist_ok=True)
    joblib.dump(model, "model_output/aqi_model.pkl")

    mr = project.get_model_registry()

    mr_model = mr.python.create_model(
        name="aqi_predictor",
        metrics={"mae": mae, "rmse": rmse},
        description="Modelo XGBoost para predecir AQI a futuro"
    )

    mr_model.save("model_output")

    shutil.rmtree("model_output")

if __name__ == "__main__":
    train_model()