import pandas as pd
import asyncio
import logging

class DataProcessor:
    """データ処理クラス"""
    async def load_csv(self, file_path: str) -> pd.DataFrame:
        """CSVファイルの非同期読み込み
        Args:
            file_path (str): 読み込むCSVファイルのパス
        Returns:
            pd.DataFrame: 読み込まれたデータフレーム
        """
        try:
            loop = asyncio.get_running_loop()  # 現在のイベントループを取得
            df = await loop.run_in_executor(None, pd.read_csv, file_path)  # 非同期でCSVを読み込む
            logging.info(f"CSVファイル '{file_path}' を読み込みました。")  # 読み込み成功のログを記録
            return df
        except Exception as e:
            logging.error(f"CSVファイル '{file_path}' の読み込み中にエラーが発生しました: {e}")  # エラーログを記録
            raise  # 例外を再送出

    async def process_data(self, df: pd.DataFrame) -> dict:
        """データ処理の非同期実行
        Args:
            df (pd.DataFrame): 処理するデータフレーム
        Returns:
            dict: 計算された統計情報
        """
        try:
            loop = asyncio.get_running_loop()  # 現在のイベントループを取得
            stats = await loop.run_in_executor(None, self._calculate_stats, df)  # 非同期で統計情報を計算
            logging.info("データ処理が完了しました。")  # 処理完了のログを記録
            return stats
        except Exception as e:
            logging.error(f"データ処理中にエラーが発生しました: {e}")  # エラーログを記録
            raise  # 例外を再送出

    def _calculate_stats(self, df: pd.DataFrame) -> dict:
        """統計情報の計算
        Args:
            df (pd.DataFrame): 計算対象のデータフレーム
        Returns:
            dict: 計算された統計情報
        """
        stats = {}
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns  # 数値カラムを取得
        stats['count'] = len(df)  # データ件数を設定
        for col in numeric_cols:
            stats[col] = {
                'mean': df[col].mean(),  # 平均を計算
                'sum': df[col].sum()  # 合計を計算
            }
        return stats 