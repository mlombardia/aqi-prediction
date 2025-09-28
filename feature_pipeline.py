import requests
import hopsworks
import pandas as pd
import os

def get_air_quality_data(response):
    if response.get("status") == "ok":
        aqi = float(response['data']['aqi'])
        city = response['data']['city']['name']
        return {"aqi": aqi, "city": city}
    else:
        return {"error": "Data not available"}

def get_air_quality_data_features(response):
    data = {}
    for key in response['data']['iaqi'].keys():
        if key != 'w' or key != 'wg':
            data[key] = float(response['data']['iaqi'][key]['v'])
    return data

def get_timestamp(response):
    return pd.to_datetime(response['data']['time']['iso'])

url = f"https://api.waqi.info/feed/barcelona/?token={os.environ['AQICN_TOKEN']}"

response = requests.get(url).json()

aqi = get_air_quality_data(response)
iaqi = get_air_quality_data_features(response)
row = {**aqi, **iaqi, "timestamp": get_timestamp(response)}

df = pd.DataFrame([row])

project = hopsworks.login(api_key_value=os.environ['HOPSWORKS_API_TOKEN'])
feature_store = project.get_feature_store()
feature_group = feature_store.get_or_create_feature_group(
    name="aqi_data",
    version=1,
    primary_key=["timestamp"],
    description="Air quality data from WAQI API"
)

feature_group.insert(df, write_options={"wait_for_job": False})

"""
df["timestamp"] = pd.to_datetime(df["timestamp"])

feature_store = project.get_feature_store()
feature_group = feature_store.get_or_create_feature_group(
    name="aqi_data",
    version=1,
    primary_key=["timestamp"],
    description="Air quality data from WAQI API"
)

feature_group.insert(df, write_options={"wait_for_job": False})
"""
