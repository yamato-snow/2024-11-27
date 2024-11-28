import flet as ft
from typing import Optional
import pandas as pd
import asyncio
import logging  # ログ出力のためのライブラリを追加

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DashboardApp:  # UserControlを削除
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "データ可視化ダッシュボード"
        self.page.padding = 20
        self.data_processor = DataProcessor()  # DataProcessorのインスタンスを作成
        self.main_content = ft.Ref[ft.Column]()  # ft.Columnへの参照を保持
        self.initialize_components()

    def initialize_components(self):
        """コンポーネントの初期化"""
        # ヘッダー
        self.header = ft.Container(
            content=ft.Text("データ可視化ダッシュボード", 
                          size=24, 
                          weight=ft.FontWeight.BOLD),
            margin=ft.margin.only(bottom=20),
            bgcolor=ft.colors.BLUE_GREY_100,  # モダンな背景色を追加
            padding=10,  # パディングを追加
            border_radius=10  # 角を丸くする
        )

        # データテーブル - 公式ドキュメントのDataTableコントロールを使用
        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("初期列"))],  # ダミーのDataColumnを追加
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.BorderSide(1, ft.colors.GREY_400),
            horizontal_lines=ft.BorderSide(1, ft.colors.GREY_400),
            column_spacing=20,
            heading_row_color=ft.colors.BLUE_GREY_50,  # ヘッダーに背景色を追加
            data_row_min_height=40,  # 行の最小高さを設定
            data_row_max_height=40,  # 行の最大高さを設定
        )

        # 統計情報表示エリア
        self.stats_view_container = ft.Container(  # ListViewをContainerでラップ
            bgcolor=ft.colors.WHITE,  # 背景色を追加
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            padding=10,
            margin=ft.margin.only(top=10),
            content=ft.ListView(  # ColumnからListViewに変更
                controls=[
                    ft.Text("基本統計情報", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("データがロードされていません")
                ],
                spacing=10,
                expand=True,
                auto_scroll=True  # 自動スクロールを有効化
            )
        )

        # ファイルドロップエリア
        self.upload_text = ft.Text("ここにCSVファイルをドロップ", size=16)
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
            margin=ft.margin.only(bottom=20),
            bgcolor=ft.colors.BLUE_GREY_50  # 背景色を追加
        )

        # グラフビューの追加
        self.graph_view = GraphView()

        # 読み込み中インジケータ
        self.loading_indicator = ft.ProgressRing(visible=False, color=ft.colors.BLUE)

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
            logging.error(f"データ処理エラー: {str(ex)}")  # エラーログを出力
            self.show_error("データ処理中にエラーが発生しました。")  # ユーザーに一般的なエラーメッセージを表��
        finally:
            self.loading_indicator.visible = False
            self.page.update()

    async def update_display(self, df: pd.DataFrame, stats: dict):
        """UI表示の非同期更新"""
        try:
            # データテーブルの更新
            self.update_data_display(df)
            
            # グラフの更新
            self.graph_view.update_data(df)
            
            self.page.update()
        except Exception as ex:
            logging.error(f"UI更新エラー: {str(ex)}")  # エラーログを出力
            self.show_error("UIの更新中にエラーが発生しました。")  # ユーザーに一般的なエラーメッセージを表示

    def build(self):
        """UIの構築"""
        return ft.Container(
            content=ft.ListView(  # Column を ListView でラップしてスクロール可能にする
                controls=[
                    ft.Column(
                        controls=[
                            self.header,
                            ft.Row(
                                [
                                    # 左側: ファイルアップロードエリア
                                    ft.Container(
                                        content=ft.Column([
                                            self.drop_container,
                                            self.loading_indicator,
                                            self.stats_view_container  # 修正: stats_viewをstats_view_containerに変更
                                        ], expand=True, spacing=10),
                                        expand=True,
                                        padding=10,
                                    ),
                                    
                                    # 右側: データ表示エリア
                                    ft.Container(
                                        content=ft.Column([
                                            self.graph_view.build(),  # GraphViewをビルドして追加
                                            self.data_table
                                        ], expand=True, spacing=10),
                                        expand=True,
                                        padding=10,
                                    )
                                ],
                                spacing=20,
                                expand=True
                            )
                        ],
                        spacing=20,
                        expand=True
                    )
                ],
                expand=True
            ),
            padding=20,  # Padding を Container に移動
            expand=True
        )

    def update_data_display(self, df: pd.DataFrame):
        """データ表示の更新"""
        # テーブルヘッダーの更新
        self.data_table.columns = [
            ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD))  # を太字に変更
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
        
        self.stats_view_container.content.controls.clear()
        self.stats_view_container.content.controls.extend(stats_text)
        self.page.update()

    def show_error(self, message: str):
        """エラーメッセージの表示"""
        snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.RED_400)
        self.page.snack_bar = snack_bar
        self.page.update()

class GraphView:  # UserControlを継承から削除
    def __init__(self):
        self.chart = ft.LineChart(
            data_series=[],
            border=ft.border.all(1, ft.colors.GREY_400),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.colors.GREY_200,
                width=1,
                dash_pattern=[3, 3]
            ),
            vertical_grid_lines=ft.ChartGridLines(
                color=ft.colors.GREY_300,
                width=1,
                dash_pattern=[3, 3]
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.GREY_300),
            expand=True,
            left_axis=ft.ChartAxis(
                labels_size=20,  # ラベルサイズを調整
                # labels_color=ft.colors.BLACK,  # ラベル色を黒に設定
                title=ft.Text("Y軸タイトル", size=18, weight=ft.FontWeight.BOLD),  # Y軸タイトルを追加
                title_size=20,
                # title_align=ft.Alignment.center,  # タイトルの位置調整
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=16,  # ラベルサイズを調整
                # labels_color=ft.colors.BLACK,  # ラベル色を黒に設定
                title=ft.Text("X軸タイトル", size=18, weight=ft.FontWeight.BOLD),  # X軸タイトルを追加
                title_size=20,
                # title_align=ft.Alignment.center,  # タイトルの位置調整
            ),
            interactive=True,
        )

    def build(self):  # buildメソッドはそのまま
        """グラフビューの構築"""
        return ft.Container(
            content=self.chart,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            expand=True
        )

    def update_data(self, df: pd.DataFrame):
        """グラフデータの更新"""
        if df.empty:
            return

        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return

        first_numeric_col = numeric_cols[0]
        self.chart.data_series = [
            ft.LineChartData(
                data_points=[
                    ft.LineChartDataPoint(x=x, y=float(y))
                    for x, y in enumerate(df[first_numeric_col])
                ],
                stroke_width=2,
                color=ft.colors.BLUE
            )
        ]
        self.chart.update()

class DataProcessor:
    """データ処理クラス"""
    async def load_csv(self, file_path: str) -> pd.DataFrame:
        """CSVファイルの非同期読み込み"""
        try:
            loop = asyncio.get_running_loop()
            df = await loop.run_in_executor(None, pd.read_csv, file_path)
            logging.info(f"CSVファイル '{file_path}' を読み込ました。")
            return df
        except Exception as e:
            logging.error(f"CSVファイル '{file_path}' の読み込み中にエラーが発生しました: {e}")
            raise

    async def process_data(self, df: pd.DataFrame) -> dict:
        """データ処理の非同期実行"""
        try:
            loop = asyncio.get_running_loop()
            stats = await loop.run_in_executor(None, self._calculate_stats, df)
            logging.info("データ処理が完了しました。")
            return stats
        except Exception as e:
            logging.error(f"データ処理中にエラーが発生しました: {e}")
            raise

    def _calculate_stats(self, df: pd.DataFrame) -> dict:
        """統計情報の計算"""
        stats = {}
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        stats['count'] = len(df)
        for col in numeric_cols:
            stats[col] = {
                'mean': df[col].mean(),
                'sum': df[col].sum()
            }
        return stats

async def main(page: ft.Page):
    """メイン関数"""
    app = DashboardApp(page)
    page.add(app.build())  # 'await' を削除

if __name__ == "__main__":
    ft.app(target=main)