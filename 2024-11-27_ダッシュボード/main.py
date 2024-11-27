import flet as ft
import pandas as pd
import io
import base64

class DataDashboard:
    def __init__(self, page: ft.Page):
        self.page = page
        self.df = None
        self.setup_page()
        self.init_components()
        self.layout_components()

    def setup_page(self):
        """ページの基本設定"""
        self.page.title = "データ可視化ダッシュボード"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.padding = 20
        self.page.spacing = 20

    def init_components(self):
        """コンポーネントの初期化"""
        # ファイルドロップエリア
        self.drop_area = ft.DragTarget(
            content=ft.Container(
                content=ft.Text("CSVファイルをドロップしてください", 
                              size=20, 
                              text_align=ft.TextAlign.CENTER),
                width=400,
                height=200,
                border=ft.border.all(2, ft.colors.GREY_400),
                border_radius=10,
                alignment=ft.alignment.center,
            ),
            on_accept=self.handle_file_drop,
        )

        # データテーブル
        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("ダミー"))],  # ダミーの DataColumn を追加
            expand=True,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
        )

        # 統計情報表示
        self.stats_text = ft.Text("", size=16)

        # グラフ表示エリア
        self.chart = ft.LineChart(
            expand=True,
            height=300,
            left_axis=ft.ChartAxis(labels_size=40),
            bottom_axis=ft.ChartAxis(labels_size=40),
        )

    def layout_components(self):
        """レイアウトの構成"""
        self.page.add(
            ft.Row([
                ft.Column([
                    self.drop_area,
                    self.stats_text
                ], expand=1),
                ft.VerticalDivider(width=1),
                ft.Column([
                    ft.Text("グラフ表示", size=20, weight=ft.FontWeight.BOLD),
                    self.chart
                ], expand=2)
            ], expand=True),
            ft.Divider(height=1),
            ft.Text("データテーブル", size=20, weight=ft.FontWeight.BOLD),
            self.data_table
        )

    async def handle_file_drop(self, e):
        """ファイルドロップ処理"""
        try:
            # ファイルの読み込み
            file_content = await self.page.get_upload_url(e.data)
            df = pd.read_csv(file_content)
            self.df = df

            # データテーブルの更新
            self.update_data_table()

            # 統計情報の更新
            self.update_stats()

            # グラフの更新
            self.update_chart()

            self.page.update()

        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"エラー: {str(ex)}"))
            )

    def update_data_table(self):
        """データテーブルの更新"""
        if self.df is None:
            return

        # カラムの設定
        self.data_table.columns = [
            ft.DataColumn(ft.Text(col)) for col in self.df.columns
        ]

        # データ行の設定
        self.data_table.rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]
            ) for row in self.df.values[:100]  # 表示行数を制限
        ]

    def update_stats(self):
        """統計情報の更新"""
        if self.df is None:
            return

        stats = f"""
        データ件数: {len(self.df)}
        数値列の統計:
        {self.df.describe().to_string()}
        """
        self.stats_text.value = stats

    def update_chart(self):
        """グラフの更新"""
        if self.df is None:
            return

        # 数値列の最初の列をグラフ化
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            data = self.df[numeric_cols[0]].head(20)  # データ数を制限
            
            self.chart.data_series = [
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(x, y) 
                        for x, y in enumerate(data)
                    ],
                    stroke_width=2,
                    color=ft.colors.BLUE,
                )
            ]

def main(page: ft.Page):
    app = DataDashboard(page)

ft.app(target=main)