import pandas as pd
import time
import logging

logger = logging.getLogger(__name__)


def push_features(fg, df: pd.DataFrame, max_retries=3):
    """
    Push already-built features to Hopsworks Feature Group with retry logic.
    
    Args:
        fg: Hopsworks feature group object
        df: DataFrame with features to push
        max_retries: Maximum number of retry attempts (default: 3)
    """
    if df is None or len(df) == 0:
        logger.warning("⚠️ No data to insert")
        return
    
    print(f"📤 Attempting to insert {len(df)} rows into feature group...")
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}")
            
            # Try synchronous insert for better reliability
            fg.insert(
                df, 
                write_options={
                    "wait_for_job": True,  # Wait for materialization to complete
                    "start_offline_materialization": True
                }
            )
            
            print(f"✅ Successfully pushed {len(df)} row(s) to Feature Store")
            return
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            print(f"❌ Attempt {attempt + 1} failed: {error_type}")
            print(f"   Error: {error_msg}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 5s, 10s, 15s
                wait_time = (attempt + 1) * 5
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"💥 All {max_retries} attempts failed")
                
                # Last resort: try async insert
                print("🔧 Trying asynchronous insertion as fallback...")
                try:
                    fg.insert(df, write_options={"wait_for_job": False})
                    print("⚠️ Async insertion triggered")
                    print("   Please check Hopsworks UI to verify job status")
                    print("   Job name: Check for materialization job in your project")
                    return
                except Exception as e2:
                    print(f"💥 Fallback method also failed: {str(e2)}")
                    raise Exception(
                        f"Failed to insert data after {max_retries} attempts.\n"
                        f"Last error: {error_msg}\n"
                        f"This might be a Hopsworks service issue. Please check:\n"
                        f"1. Hopsworks dashboard status\n"
                        f"2. Your project quotas/limits\n"
                        f"3. Network connectivity"
                    )


def push_features_in_batches(fg, df: pd.DataFrame, batch_size=10, max_retries=3):
    """
    Push features in smaller batches to avoid timeouts.
    Use this if regular push_features continues to fail.
    
    Args:
        fg: Hopsworks feature group object
        df: DataFrame with features to push
        batch_size: Number of rows per batch (default: 10)
        max_retries: Maximum retries per batch (default: 3)
    """
    if df is None or len(df) == 0:
        logger.warning("⚠️ No data to insert")
        return
    
    total_rows = len(df)
    total_batches = (total_rows + batch_size - 1) // batch_size
    
    print(f"📦 Splitting {total_rows} rows into {total_batches} batches of ~{batch_size} rows")
    
    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"\n📤 Inserting batch {batch_num}/{total_batches} ({len(batch)} rows)...")
        
        for attempt in range(max_retries):
            try:
                fg.insert(
                    batch, 
                    write_options={
                        "wait_for_job": True,
                        "start_offline_materialization": True
                    }
                )
                print(f"✅ Batch {batch_num} inserted successfully")
                time.sleep(2)  # Small delay between batches
                break
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"⚠️ Batch {batch_num} attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Batch {batch_num} failed after {max_retries} attempts: {str(e)}")
                    raise
    
    print(f"\n✅ All {total_batches} batches inserted successfully!")