# components/stats.py
import flet as ft

class Stats(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        
    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("基本統計情報", size=20, weight=ft.FontWeight.BOLD),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("データサマリー"),
                            self._build_stats_grid()
                        ]),
                        padding=10
                    )
                )
            ]),
            padding=10
        )
        
    def _build_stats_grid(self):
        return ft.Column([
            ft.Row([
                ft.Text("総行数:"),
                ft.Text("0", ref=self._row_count_ref)
            ]),
            ft.Row([
                ft.Text("数値カラム数:"),
                ft.Text("0", ref=self._num_cols_ref)
            ])
        ])
        
    async def update_stats(self, stats_data: dict):
        """統計情報の更新"""
        if not stats_data:
            return
            
        self._row_count_ref.current.value = str(stats_data.get("row_count", 0))
        self._num_cols_ref.current.value = str(len(stats_data.get("numeric_stats", {})))
        await self.update_async()