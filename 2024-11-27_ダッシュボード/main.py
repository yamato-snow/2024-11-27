import flet as ft
import pandas as pd
from typing import Optional
from graph_view import GraphView  # GraphViewをインポート
import constants  # 定数をインポート

class ModernDataDashboard:
    def __init__(self, page: ft.Page):
        self.page = page
        self.df: Optional[pd.DataFrame] = None
        self.page.theme_mode = ft.ThemeMode.LIGHT  # ライトモード固定
        self.setup_page()
        self.init_components()
        self.graph_view = GraphView()  # GraphViewのインスタンスを作成
        self.create_layout()

    def setup_page(self):
        """ページの基本設定"""
        # 非推奨APIの修正
        self.page.window.title_bar_hidden = False
        self.page.window.title_bar_buttons_hidden = False
        self.page.theme = ft.Theme(
            color_scheme_seed=constants.THEME_COLOR_SCHEME,
        )
        self.page.window.width = constants.WINDOW_WIDTH
        self.page.window.height = constants.WINDOW_HEIGHT
        self.page.window.min_width = constants.MIN_WINDOW_WIDTH  # ウィンドウの最小幅を設定
        self.page.window.min_height = constants.MIN_WINDOW_HEIGHT  # ウィンドウの最小高さを設定
        self.page.padding = constants.PADDING_VALUE
        
        def theme_changed(e):
            self.page.theme_mode = (
                ft.ThemeMode.DARK 
                if self.page.theme_mode == ft.ThemeMode.LIGHT 
                else ft.ThemeMode.LIGHT
            )
            self.page.update()

        self.page.appbar = ft.AppBar(
            leading=ft.Icon(ft.icons.ANALYTICS),
            leading_width=40,
            title=ft.Text("データ可視化ダッシュボード"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(ft.icons.DARK_MODE, on_click=theme_changed),
                ft.IconButton(ft.icons.HELP_OUTLINE)
            ],
        )

    def init_components(self):
        """UIコンポーネントの初期化"""
        self.file_picker = ft.FilePicker(
            on_result=self.on_file_picked
        )
        self.page.overlay.append(self.file_picker)

        # ファイルアップロードエリア
        self.upload_area = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.UPLOAD_FILE, size=40, color=ft.colors.BLUE),
                ft.Text(
                    "CSVファイルをドラッグ＆ドロップ",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.ElevatedButton(
                    "ファイルを選択",
                    icon=ft.icons.FILE_UPLOAD,
                    on_click=lambda _: self.file_picker.pick_files(
                        allowed_extensions=["csv"]
                    )
                ),
            ], 
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
            padding=20,
            height=200,
        )

        # 統計情報エリア
        self.stats_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )

        # データプレビューエリア
        self.data_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            # auto_scroll=True
        )

    def create_layout(self):
        """レイアウトの構築"""
        # メインコンテンツエリアのレイアウトを修正
        self.main_content = ft.Container(
            content=ft.Column([
                # アップロードエリアとグラフを並びに配置
                ft.Row([
                    # アップロードエリア（左側）
                    ft.Container(
                        content=self.upload_area,
                        width=400,  # 必要に応じて幅を調整
                        padding=10,
                    ),

                    # グラフ表示エリア（右側）
                    ft.Container(
                        content=self.graph_view.build(),  # グラフビューを追加
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=10,
                        padding=20,
                        expand=True,
                        height=400,
                    ),
                ],
                spacing=20,
                ),

                # データと統計情報エリア
                ft.Row([
                    # 統計情報（左側）
                    ft.Container(
                        content=ft.Column([
                            ft.Text("基本統計情報", size=16, weight=ft.FontWeight.BOLD),
                            self.stats_view,
                        ]),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=10,
                        padding=20,
                        width=300,
                        height=400
                    ),
                    
                    # データプレビュー（右側）
                    ft.Container(
                        content=ft.Column([
                            ft.Text("データプレビュー", size=16, weight=ft.FontWeight.BOLD),
                            self.data_view,
                        ]),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=10,
                        padding=20,
                        expand=True,
                        height=400,
                    ),
                ],
                expand=True,
                spacing=20,
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
            ),
            padding=20,
            expand=True,
        )

    async def on_file_picked(self, e: ft.FilePickerResultEvent):
        """ファイル選択時の処理"""
        if e.files:
            file_path = e.files[0].path
            try:
                self.df = pd.read_csv(file_path)
                self.update_displays()
                self.graph_view.update_data(self.df)  # グラフを更新
                # スナックバーを表示
                snack = ft.SnackBar(content=ft.Text("データを正常に読み込みました"))
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()
            except Exception as ex:
                # エラースナックバーを表示
                snack = ft.SnackBar(content=ft.Text(f"エラーが発生しました: {str(ex)}"))
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

    def update_displays(self):
        """表示の更新"""
        if self.df is None:
            return

        # 統計情報の更新
        stats = []
        stats.append(ft.Text(f"行数: {len(self.df)}", size=16))
        stats.append(ft.Text(f"列数: {len(self.df.columns)}", size=16))
        
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            col_stats = self.df[col].describe()
            stats.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{col}の統計情報:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"平均: {col_stats['mean']:.2f}"),
                        ft.Text(f"合計: {self.df[col].sum():.2f}")
                    ]),
                    bgcolor=ft.colors.BLUE_50,
                    padding=10,
                    border_radius=10
                )
            )
        self.stats_view.controls = stats

        # データプレビューの更新
        data_rows = []
        # ヘッダー
        data_rows.append(
            ft.Container(
                content=ft.Text(
                    ", ".join(self.df.columns),
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor=ft.colors.BLUE_50,
                padding=10,
                border_radius=10
            )
        )
        # データ行
        for _, row in self.df.head(10).iterrows():
            data_rows.append(
                ft.Container(
                    content=ft.Text(", ".join(str(cell) for cell in row)),
                    padding=10,
                    border_radius=10
                )
            )
        self.data_view.controls = data_rows
        
        self.page.update()

def main(page: ft.Page):
    page.title = "データ可視化ダッシュボード"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    dashboard = ModernDataDashboard(page)
    page.add(dashboard.main_content)

if __name__ == "__main__":
    ft.app(target=main)