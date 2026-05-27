import pandas as pd
from typing import List, Dict, Any


def transcript_to_dataframe(transcript: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(transcript)
