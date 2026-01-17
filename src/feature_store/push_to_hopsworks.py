# import hopsworks
# import pandas as pd
# import os
# from dotenv import load_dotenv

# load_dotenv()


# def get_last_ingested_timestamp(fs):
#     try:
#         fg = fs.get_feature_group(
#             name="karachi_air_quality",
#             version=2
#         )

#         df_last = fg.read(
#             select=["timestamp"],
#             limit=1,
#             sort_by="timestamp",
#             ascending=False
#         )

#         return df_last["timestamp"].iloc[0]

#     except Exception:
#         return None


# def push_features(fg, df):
#     fg.insert(df)


    

#     fg = fs.get_or_create_feature_group(
#         name="karachi_air_quality",
#         version=2,
#         primary_key=["event_id"],
#         event_time="timestamp",
#         online_enabled=True,
#         description="Karachi AQI features with pollutants and time-based features"
#     )

#     fg.insert(df)

#     print(f"✅ Successfully pushed {len(df)} rows to Feature Store")


import pandas as pd

def push_features(fg, df: pd.DataFrame):
    """
    Push already-built features to Hopsworks Feature Group.
    Assumes fg is already created and logged in.
    """
    fg.insert(df)
    print(f"✅ Successfully pushed {len(df)} row(s) to Feature Store")
