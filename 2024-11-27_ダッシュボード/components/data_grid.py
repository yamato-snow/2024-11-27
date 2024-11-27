# components/data_grid.py
import flet as ft
from typing import List, Optional

class DataGrid(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.data_table: Optional[ft.DataTable] = None
        
    def build(self):
        self.data_table = ft.DataTable(
            expand=True,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
            column_spacing=50,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("データビュー", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.data_table,
                    padding=10,
                    expand=True
                )
            ]),
            expand=True
        )
        
    async def update_data(self, df):
        """データフレームの内容でテーブルを更新"""
        if df is None:
            return
            
        # ヘッダーの設定
        self.data_table.columns = [
            ft.DataColumn(
                ft.Text(col),
                on_sort=lambda e: self._handle_sort(e, col)
            ) for col in df.columns
        ]
        
        # データ行の設定
        self.data_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(value)))
                    for value in row
                ]
            ) for row in df.values
        ]
        
        await self.update_async()
        
    def _handle_sort(self, e, column_name):
        """ソート処理の実装"""
        pass