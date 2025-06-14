import hopsworks
import pandas as pd
import os

project = hopsworks.login(api_key_value=os.environ['HOPSWORKS_API_KEY'])
feature_store = project.get_feature_store()
fg = feature_store.get_feature_group("air_quality", version=1)
df = fg.read()

print(df.head())