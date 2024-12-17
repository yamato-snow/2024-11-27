import flet as ft
import pandas as pd
import constants  # 定数をインポート

class GraphView:
    """グラフビュークラス"""

    def __init__(self):
        """グラフビューの初期化"""
        self.chart = ft.LineChart(
            data_series=[],  # 初期のデータシリーズは空
            border=ft.border.all(1, constants.CHART_BORDER_COLOR),  # 境界線を設定
            horizontal_grid_lines=ft.ChartGridLines(
                color=constants.GRID_LINE_COLOR_HORIZONTAL,
                width=1,
                dash_pattern=[3, 3]  # 破線パターンを設定
            ),
            vertical_grid_lines=ft.ChartGridLines(
                color=constants.GRID_LINE_COLOR_VERTICAL,
                width=1,
                dash_pattern=[3, 3]  # 破線パターンを設定
            ),
            tooltip_bgcolor=constants.CHART_TOOLTIP_BG_COLOR,  # ツールチップの背景色を設定
            expand=True,  # グラフを拡張
            left_axis=ft.ChartAxis(
                labels_size=50,  # Y軸のラベルサイズを調整
                title=ft.Text(constants.CHART_LEFT_AXIS_TITLE, size=18, weight=ft.FontWeight.BOLD),  # Y軸タイトルを設定
                title_size=30,  # タイトルのサイズを設定
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=50,  # X軸のラベルサイズを調整
                title=ft.Text(constants.CHART_BOTTOM_AXIS_TITLE, size=18, weight=ft.FontWeight.BOLD),  # X軸タイトルを設定
                title_size=30,  # タイトルのサイズを設定
            ),
            max_y=constants.CHART_MAX_Y,  # Y軸の最大値を設定
            min_y=constants.CHART_MIN_Y,  # Y軸の最小値を設定
            interactive=True,  # インタラクティブモードを有効化
        )

    def build(self):
        """グラフビューの構築
        Returns:
            ft.Container: グラフを含むコンテナ
        """
        return ft.Container(
            content=self.chart,  # グラフをコンテンツとして設定
            padding=ft.padding.only(20, 50, 30, 10),  # パディングを設定
            border=ft.border.all(1, constants.CHART_BORDER_COLOR),  #境界線を設定
            border_radius=10,  # 角を丸くする
            expand=True  # コンテナを拡張
        )

    def update_data(self, df: pd.DataFrame):
        """グラフデータの更新
        Args:
            df (pd.DataFrame): 更新するデータフレーム
        """
        if df.empty:
            return  # データフレームが空の場合は終了

        numeric_cols = df.select_dtypes(include=['number']).columns  # 数値カラムを取得
        if len(numeric_cols) == 0:
            return  # 数値カラムがない場合は終了

        first_numeric_col = numeric_cols[0]  # 最初の数値カラムを選択
        self.chart.data_series = [
            ft.LineChartData(
                data_points=[
                    ft.LineChartDataPoint(x=x, y=float(y))  # 各データポイントを設定
                    for x, y in enumerate(df[first_numeric_col])
                ],
                stroke_width=2,  # 線の太さを設定
                color=ft.colors.BLUE,  # 線の色を設定
                prevent_curve_over_shooting=True,  # カーブのオーバーシューティングを防止
                point=True,  # データポイントを表示
            )
        ]
        self.chart.update()  # グラフを更新