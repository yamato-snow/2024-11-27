# utils/data_processor.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class DataProcessor:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.current_stats: Dict = {}
        
    async def load_csv(self, file_path: str) -> bool:
        try:
            self.df = pd.read_csv(file_path)
            await self._calculate_statistics()
            return True
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            return False
            
    async def _calculate_statistics(self):
        """基本統計情報の計算"""
        if self.df is None:
            return
            
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns
        self.current_stats = {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "numeric_stats": {
                col: {
                    "mean": float(self.df[col].mean()),
                    "sum": float(self.df[col].sum()),
                    "min": float(self.df[col].min()),
                    "max": float(self.df[col].max())
                } for col in numeric_columns
            }
        }