import flet as ft
from typing import Optional
import pandas as pd

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

    def build(self):
        """UIの構築"""
        return ft.Column([
            self.header,
            ft.Row(
                [
                    # 左側: ファイルアップロードエリア
                    ft.Column([
                        self.drop_container,
                        self.stats_view
                    ], expand=1),
                    
                    # 右側: データ表示エリア
                    ft.Column([
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

def main(page: ft.Page):
    app = DashboardApp(page)
    page.add(app)

if __name__ == "__main__":
    ft.app(target=main)