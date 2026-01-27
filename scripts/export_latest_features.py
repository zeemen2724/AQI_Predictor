import os
import hopsworks
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"

def main():
    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT_NAME"),
    )

    fs = project.get_feature_store()

    fg = fs.get_feature_group(
        name="karachi_air_quality",
        version=3
    )

    df = fg.read()
    df = df.sort_values("timestamp")

    os.makedirs("artifacts", exist_ok=True)
    df.to_parquet("artifacts/latest_features.parquet", index=False)

    print("✅ Latest features exported")

if __name__ == "__main__":
    main()
import os
import hopsworks
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"

def main():
    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT_NAME"),
    )

    fs = project.get_feature_store()

    fg = fs.get_feature_group(
        name="karachi_air_quality",
        version=4
    )

    df = fg.read()
    df = df.sort_values("timestamp")

    os.makedirs("artifacts", exist_ok=True)
    df.to_parquet("artifacts/latest_features.parquet", index=False)

    print("✅ Latest features exported")

if __name__ == "__main__":
    main()
