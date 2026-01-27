import os
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"
from dotenv import load_dotenv
load_dotenv()
import hopsworks

project = hopsworks.login(
    api_key_value=os.getenv("HOPSWORKS_API_KEY"),
    project=os.getenv("HOPSWORKS_PROJECT_NAME")
)
fs = project.get_feature_store()
fg = fs.get_feature_group("karachi_air_quality", version=4)
df = fg.read()

print(f"Total rows: {len(df)}")
print(f"Latest timestamp: {df['timestamp'].max()}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
