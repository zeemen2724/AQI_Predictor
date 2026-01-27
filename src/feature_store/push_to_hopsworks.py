import pandas as pd

def push_features(fg, df: pd.DataFrame):
    """
    Push already-built features to Hopsworks Feature Group.
    Assumes fg is already created and logged in.
    """
    # Don't wait for materialization job to avoid timeouts
    fg.insert(df, write_options={"wait_for_job": False})
    
    print(f"Successfully pushed {len(df)} row(s) to Feature Store")
