# components/file_drop.py
import flet as ft

class FileDropZone(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("CSVファイルをドロップ", size=20),
                    ft.Container(
                        border=ft.border.all(2, ft.colors.GREY_400),
                        border_radius=8,
                        padding=20,
                        content=ft.DragTarget(
                            content=ft.Container(
                                width=300,
                                height=150,
                                alignment=ft.alignment.center,
                                content=ft.Text(
                                    "ここにファイルをドロップ",
                                    text_align=ft.TextAlign.CENTER,
                                )
                            ),
                            on_accept=self._handle_file_drop
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def _handle_file_drop(self, e):
        # ファイル処理ロジックの実装
        pass