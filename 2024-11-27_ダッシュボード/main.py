import flet as ft
from typing import Optional
import pandas as pd
import asyncio

class DashboardApp(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.page.title = "データ可視化ダッシュボード"
        self.page.padding = 20
        self.initialize_components()

    def initialize_components(self):
        """コンポーネントの初期化"""
        # ヘッダー
        self.header = ft.Container(
            content=ft.Text("データ可視化ダッシュボード", 
                          size=24, 
                          weight=ft.FontWeight.BOLD),
            margin=ft.margin.only(bottom=20)
        )

        # データテーブル - 公式ドキュメントのDataTableコントロールを使用
        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("初期列"))],  # ダミーのDataColumnを追加
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.BorderSide(1, ft.colors.GREY_400),
            horizontal_lines=ft.BorderSide(1, ft.colors.GREY_400),
            column_spacing=20
        )

        # 統計情報表示エリア
        self.stats_view = ft.Column(
            controls=[
                ft.Text("基本統計情報", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("データがロードされていません")
            ],
            spacing=10
        )

        # ファイルドロップエリア
        self.upload_text = ft.Text("ここにCSVファイルをドロップ")
        self.file_picker = ft.FilePicker(
            on_result=self.handle_file_picked
        )
        self.page.overlay.append(self.file_picker)
        
        self.drop_container = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.icons.UPLOAD_FILE, 
                           size=40, 
                           color=ft.colors.BLUE),
                    self.upload_text,
                    ft.ElevatedButton(
                        "ファイルを選択",
                        on_click=lambda _: self.file_picker.pick_files(
                            allowed_extensions=["csv"]
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            width=400,
            height=200,
            border=ft.border.all(2, ft.colors.BLUE_200),
            border_radius=10,
            alignment=ft.alignment.center,
            margin=ft.margin.only(bottom=20)
        )

        # グラフビューの追加
        self.graph_view = GraphView()

        # グラフビューの追加
        self.graph_view = GraphView()

    async def handle_file_picked(self, e: ft.FilePickerResultEvent):
        """ファイル選択時の非同期処理"""
        if not e.files or not e.files[0].path:
            return
            
        try:
            # 読み込み中表示
            self.loading_indicator.visible = True
            self.page.update()
            
            # データの非同期読み込みと処理
            file_path = e.files[0].path
            df = await self.data_processor.load_csv(file_path)
            stats = await self.data_processor.process_data(df)
            
            # UI更新
            await self.update_display(df, stats)
            
        except Exception as ex:
            self.show_error(f"データ処理エラー: {str(ex)}")
        finally:
            self.loading_indicator.visible = False
            self.page.update()

    async def update_display(self, df: pd.DataFrame, stats: dict):
        """UI表示の非同期更新"""
        # データテーブルの更新
        self.update_data_table(df)
        
        # 統計情報の更新
        self.update_statistics(stats)
        
        # グラフの更新
        self.graph_view.update_data(df)
        
        await self.page.update_async()

    def build(self):
        """UIの構築"""
        return ft.Column([
            self.header,
            ft.Row(
                [
                    # 左側: ファイルアップロードエリア
                    ft.Column([
                        self.drop_container,
                        self.loading_indicator,
                        self.stats_view
                    ], expand=1),
                    
                    # 右側: データ表示エリア
                    ft.Column([
                        self.graph_view,
                        self.data_table
                    ], expand=2)
                ],
                spacing=20,
                expand=True
            )
        ])

    def handle_file_picked(self, e: ft.FilePickerResultEvent):
        """ファイル選択時の処理"""
        if e.files:
            file_path = e.files[0].path
            try:
                df = pd.read_csv(file_path)
                self.update_data_display(df)
            except Exception as ex:
                self.show_error(f"ファイルの読み込みエラー: {str(ex)}")

    def update_data_display(self, df: pd.DataFrame):
        """データ表示の更新"""
        # テーブルヘッダーの更新
        self.data_table.columns = [
            ft.DataColumn(ft.Text(col)) 
            for col in df.columns
        ]

        # 先頭5行のデータを表示
        self.data_table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(df.iloc[i][col])))
                for col in df.columns
            ])
            for i in range(min(5, len(df)))
        ]

        # 統計情報の更新
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        stats_text = [
            ft.Text("基本統計情報", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"データ件数: {len(df)}行"),
        ]
        
        if len(numeric_cols) > 0:
            for col in numeric_cols:
                stats_text.append(ft.Text(
                    f"{col}の統計:\n"
                    f"  平均: {df[col].mean():.2f}\n"
                    f"  合計: {df[col].sum():.2f}"
                ))
        
        self.stats_view.controls = stats_text
        self.page.update()

    def show_error(self, message: str):
        """エラーメッセージの表示"""
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.RED_400)
        )

class GraphView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.chart = ft.LineChart(
            data_series=[],
            border=ft.border.all(1, ft.colors.GREY_400),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=1,
                color=ft.colors.GREY_300,
                width=1
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            expand=True
        )

    def update_data(self, df: pd.DataFrame):
        """データフレームからグラフデータを更新"""
        # 数値列のみを対象
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) == 0:
            return
        
        # 最初の数値列を使用
        column = numeric_cols[0]
        data_points = [
            ft.LineChartDataPoint(i, float(value))
            for i, value in enumerate(df[column])
        ]
        
        self.chart.data_series = [
            ft.LineChartData(
                data_points=data_points,
                stroke_width=2,
                color=ft.colors.BLUE,
                curved=True,
            )
        ]
        
        # 軸ラベルの設定
        self.chart.left_axis = ft.ChartAxis(
            title=ft.Text(column),
            labels_size=40
        )
        
        self.chart.bottom_axis = ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=i,
                    label=ft.Container(
                        ft.Text(str(i), size=10),
                        margin=ft.margin.only(top=10),
                    ),
                )
                for i in range(0, len(df), max(1, len(df) // 5))
            ],
            labels_size=40
        )
        
        self.update()

    def build(self):
        return ft.Container(
            content=self.chart,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            padding=10,
            expand=True
        )

class DataProcessor:
    @staticmethod
    async def load_csv(file_path: str) -> pd.DataFrame:
        """CSVファイルの非同期読み込み"""
        # ファイル読み込みを非同期で実行
        return await asyncio.to_thread(pd.read_csv, file_path)

    @staticmethod
    async def process_data(df: pd.DataFrame) -> dict:
        """データの基本統計量を非同期で計算"""
        stats = {}
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        # 統計計算を非同期で実行
        def calculate_stats():
            stats["row_count"] = len(df)
            stats["numeric_stats"] = {}
            for col in numeric_cols:
                stats["numeric_stats"][col] = {
                    "mean": df[col].mean(),
                    "sum": df[col].sum(),
                    "min": df[col].min(),
                    "max": df[col].max()
                }
            return stats
            
        return await asyncio.to_thread(calculate_stats)

async def main(page: ft.Page):
    app = DashboardApp(page)
    await page.add_async(app)

if __name__ == "__main__":
    ft.app(target=main)