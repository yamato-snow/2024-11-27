import flet as ft
from typing import Optional
import pandas as pd
import asyncio
import logging  # ログ出力のためのライブラリを追加
from data_processor import DataProcessor  # 追加
from graph_view import GraphView  # 追加

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DashboardApp:
    """ダッシュボードアプリケーションクラス"""
    def __init__(self, page: ft.Page):
        """ダッシュボードアプリケーションの初期化"""
        self.page = page
        self.page.title = "データ可視化ダッシュボード"  # ページのタイトルを設定
        self.page.padding = 20  # ページのパディングを設定
        self.data_processor = DataProcessor()  # データ処理クラスのインスタンスを作成
        self.main_content = ft.Ref[ft.Column]()  # ft.Columnへの参照を保持
        self.graph_view = GraphView()  # グラフビュークラスのインスタンスを作成
        self.initialize_components()  # UIコンポーネントを初期化

    def create_container(self, content, expand=True, padding=10, width=None, **kwargs):
        """共通のContainerを作成するヘルパーメソッド
        Args:
            content: コンテナ内に配置するコンテンツ
            expand: コンテナを拡張するかどうか
            padding: コンテナのパディング
            width: コンテナの幅
            **kwargs: その他のキーワード引数
        Returns:
            ft.Container: 設定されたプロパティを持つコンテナ
        """
        return ft.Container(
            content=content,
            expand=expand,
            padding=padding,
            width=width,
            **kwargs
        )

    def initialize_components(self):
        """コンポーネントの初期化"""
        # ヘッダー
        self.header = ft.Container(
            content=ft.Text("データ可視化ダッシュボード", 
                          size=24, 
                          weight=ft.FontWeight.BOLD),
            margin=ft.margin.only(bottom=20),  # 下マージンを設定
            bgcolor=ft.colors.BLUE_GREY_100,  # モダンな背景色を追加
            padding=10,  # パディングを追加
            border_radius=10  # 角を丸くする
        )

        # データテーブル - 公式ドキュメントのDataTableコントロールを使用
        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("データを読み込んでください"))],  # カラムが空の場合エラーするため、初期値としてテキストを設定
            rows=[],  # 初期行は空
            border=ft.border.all(1, ft.colors.GREY_400),  # テーブルの境界線を設定
            border_radius=10,  # 角を丸くする
            vertical_lines=ft.BorderSide(1, ft.colors.GREY_400),  # 縦線のスタイルを設定
            horizontal_lines=ft.BorderSide(1, ft.colors.GREY_400),  # 横線のスタイルを設定
            column_spacing=20,  # カラム間のスペースを設定
            heading_row_color=ft.colors.BLUE_GREY_50,  # ヘッダーの背景色を設定
            data_row_min_height=40,  # 行の最小高さを設定
            data_row_max_height=40,  # 行の最大高さを設定
        )

        # 統計情報表示エリア
        self.stats_view_container = self.create_container(
            content=ft.ListView(
                controls=[
                    ft.Text("基本統計情報", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("データがロードされていません")
                ],
                spacing=10,  # 各アイテム間のスペースを設定
                expand=True,
                auto_scroll=True  # 自動スクロールを有効化
            ),
            bgcolor=ft.colors.WHITE,  # 背景色を白に設定
            border=ft.border.all(1, ft.colors.GREY_300),  # 境界線を設定
            border_radius=10,  # 角を丸くする
            padding=10,  # パディングを設定
            margin=ft.margin.only(top=10)  # 上マージンを設定
        )

        # ファイルアップロードエリア
        self.upload_text = ft.Text("ここにCSVファイルをアップロード", size=16)  # アップロード指示テキスト
        self.file_picker = ft.FilePicker(
            on_result=self.handle_file_picked  # ファイル選択後のコールバック関数を設定
        )
        self.page.overlay.append(self.file_picker)  # ページにファイルピッカーを追加
        
        self.drop_container = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.icons.UPLOAD_FILE, 
                           size=40, 
                           color=ft.colors.BLUE),  # アップロードアイコン
                    self.upload_text,  # アップロード指示テキスト
                    ft.ElevatedButton(
                        "ファイルを選択",
                        on_click=lambda _: self.file_picker.pick_files(
                            allowed_extensions=["csv"]  # CSVファイルのみ選択可能に設定
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # 水平方向の中央揃え
                alignment=ft.MainAxisAlignment.CENTER,  # メイン軸の中央揃え
                spacing=10  # 各アイテム間のスペースを設定
            ),
            width=400,  # コンテナの幅を設定
            height=200,  # コンテナの高さを設定
            border=ft.border.all(2, ft.colors.BLUE_200),  # 境界線を設定
            border_radius=10,  # 角を丸くする
            alignment=ft.alignment.center,  # コンテンツの中央揃え
            margin=ft.margin.only(bottom=20),  # 下マージンを設定
            bgcolor=ft.colors.BLUE_GREY_50,  # 背景色を追加
        )

        # 読み込み中インジケータ
        self.loading_indicator = ft.ProgressRing(visible=False, color=ft.colors.BLUE)  # 読み込み中のインジケータを設定

    async def handle_file_picked(self, e: ft.FilePickerResultEvent):
        """ファイル選択時の非同期処理
        Args:
            e (ft.FilePickerResultEvent): ファイルピッカーの結果イベント
        """
        if not e.files or not e.files[0].path:
            return  # ファイルが選択されていない場合は終了
            
        try:
            # 読み込み中表示
            self.loading_indicator.visible = True
            self.page.update()
            
            # データの非同期読み込みと処理
            file_path = e.files[0].path
            df = await self.data_processor.load_csv(file_path)  # CSVファイルを非同期で読み込む
            stats = await self.data_processor.process_data(df)  # データを非同期で処理して統計情報を取得
            
            # UI更新
            await self.update_display(df, stats)
            
        except Exception as ex:
            logging.error(f"データ処理エラー: {str(ex)}")  # エラーログを出力
            self.show_error("データ処理中にエラーが発生しました。")  # ユーザーにエラーメッセージを表示
        finally:
            self.loading_indicator.visible = False  # 読み込み中表示を非表示にする
            self.page.update()

    async def update_display(self, df: pd.DataFrame, stats: dict):
        """UI表示の非同期更新
        Args:
            df (pd.DataFrame): 読み込まれたデータフレーム
            stats (dict): 計算された統計情報
        """
        try:
            # データテーブルの更新
            self.update_data_display(df)
            
            # グラフの更新
            self.graph_view.update_data(df)
            
            self.page.update()  # ページを更新
        except Exception as ex:
            logging.error(f"UI更新エラー: {str(ex)}")  # エラーログを出力
            self.show_error("UIの更新中にエラーが発生しました。")  # ユーザーにエラーメッセージを表示

    def build(self):
        """UIの構築
        Returns:
            ft.Container: 構築されたUIコンテナ
        """
        return self.create_container(
            content=ft.Column(
                controls=[
                    self.header,  # ヘッダーを追加
                    ft.Row(
                        [
                            self.create_container(
                                content=ft.Column(
                                    controls=[
                                        self.drop_container,  # ファイルアップロードエリアを追加
                                        self.loading_indicator,  # 読み込み中インジケータを追加
                                    ],
                                    expand=True,
                                    alignment=ft.MainAxisAlignment.CENTER,  # 中央揃え
                                    spacing=10  # スペースを設定
                                ),
                                expand=True,
                                padding=10,
                                alignment=ft.alignment.center,
                            ),
                            self.create_container(
                                content=ft.ListView(
                                    controls=[
                                        self.graph_view.build(),  # グラフビューを追加
                                    ],
                                    expand=True,
                                    spacing=10,
                                    item_extent=50  # アイテムの高さを設定
                                ),
                                expand=True,
                                padding=10,
                                width=300,  # 幅を設定
                            )
                        ],
                        spacing=20,  # スペースを設定
                        expand=True
                    ),
                    ft.Row(
                        [
                            self.create_container(
                                content=self.stats_view_container  # 統計情報表示エリアを追加
                            ),
                            self.create_container(
                                content=ft.ListView(
                                    controls=[
                                        self.data_table  # データテーブルを追加
                                    ],
                                    expand=True,
                                    spacing=10,
                                ),
                                expand=True,
                                padding=10,
                                width=300,  # 幅を設定
                            )
                        ],
                        spacing=20,  # スペースを設定
                        expand=True
                    )
                ],
                spacing=20,  # 各行間のスペースを設定
                expand=True
            ),
            padding=20,  # 全体のパディングを設定
            expand=True
        )

    def update_data_display(self, df: pd.DataFrame):
        """データ表示の更新
        Args:
            df (pd.DataFrame): 更新するデータフレーム
        """
        # テーブルヘッダーの更新
        self.data_table.columns = [
            ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD))  # カラム名を太字に設定
            for col in df.columns
        ]

        # 全行のデータを表示
        self.data_table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(df.iloc[i][col])))  # 各セルにデータを設定
                for col in df.columns
            ])
            for i in range(len(df))
        ]

        # 統計情報の更新
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns  # 数値カラムを取得
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
        
        self.stats_view_container.content.controls.clear()  # 既存のコントロールをクリア
        self.stats_view_container.content.controls.extend(stats_text)  # 新しい統計情報を追加
        self.page.update()  # ページを更新

    def show_error(self, message: str):
        """エラーメッセージの表示
        Args:
            message (str): 表示するエラーメッセージ
        """
        snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.RED_400)  # スナックバーを作成
        self.page.snack_bar = snack_bar  # スナックバーをページに設定
        self.page.update()  # ページを更新

async def main(page: ft.Page):
    """メイン関数
    Args:
        page (ft.Page): Fletのページオブジェクト
    """
    app = DashboardApp(page)  # ダッシュボードアプリケーションのインスタンスを作成
    page.add(app.build())  # アプリケーションのUIをページに追加

if __name__ == "__main__":
    ft.app(target=main)  # アプリケーションを実行