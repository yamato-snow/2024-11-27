# components/charts.py
import flet as ft

class Charts(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        
    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("データ可視化", size=20, weight=ft.FontWeight.BOLD),
                ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(
                            text="折れ線グラフ",
                            content=self._build_line_chart()
                        ),
                        ft.Tab(
                            text="棒グラフ",
                            content=self._build_bar_chart()
                        )
                    ],
                )
            ]),
            padding=10,
            expand=True
        )
        
    def _build_line_chart(self):
        return ft.LineChart(
            expand=True,
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            interactive=True
        )
        
    def _build_bar_chart(self):
        return ft.BarChart(
            expand=True,
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            interactive=True
        )