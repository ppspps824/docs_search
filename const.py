HIDE_ST_STYLE = """
                <style>
div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
				        .appview-container .main .block-container{
                            padding-top: 1rem;
                            padding-right: 3rem;
                            padding-left: 3rem;
                            padding-bottom: 1rem;
                        }  
                        .appview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                        .reportview-container {
                            padding-top: 0rem;
                            padding-right: 3rem;
                            padding-left: 3rem;
                            padding-bottom: 0rem;
                        }
                        .reportview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                        header[data-testid="stHeader"] {
                            z-index: -1;
                        }
                        div[data-testid="stToolbar"] {
                        z-index: 100;
                        }
                        div[data-testid="stDecoration"] {
                        z-index: 100;
                        }
                        .reportview-container .sidebar-content {
                            padding-top: 0rem;
                        }
                </style>
                """

SUMMARY_PROMPT = """
あなたはプロのシステムエンジニアです。
以下のテキストはプログラムモジュールの仕様を説明したものです。
注意点に従って要約してください。

## 注意点
- 日本語で生成する。
- 300字以内とする。
- 記載されている機能はすべて網羅する。
- 説明文は不要で生成した要約分のみ出力する。

## テキスト
%%content_place%%

"""

FROM_DOCS_TAGS_PROMPT = """
あなたはプロのシステムエンジニアです。
以下のテキストはプログラムモジュールの仕様を説明したものです。
注意点に従って、モジュールの固有の機能と特徴にのみ焦点を当てたシンプルなタグのリストを生成してください。

## 注意点
- 日本語で生成する。
- タグは20個以内とする。
- 記載されている機能はすべて網羅する。
- 説明文は不要で生成したタグを指定された形式およびサンブルにしたがって出力する。

## 形式
Pythonのリスト形式

## サンプル
["tag1","tab2","tag3"]

## テキスト
%%content_place%%

"""

FROM_INPUT_TAGS_PROMPT = """
あなたはプロのシステムエンジニアです。
以下のテキストはプログラムモジュールを組み合わせて実現したい機能を説明したものです。
注意点に従って、モジュールの固有の機能と特徴にのみ焦点を当てたシンプルなタグのリストを生成してください。

## 注意点
- 日本語で生成する。
- タグは10個以内とする。
- 不足する情報がある場合も機能を実現するために必要と考えられる要素をできる限り洗い出す。
- あいまい一致に利用するため、できる限り短い単語で構成する。
- 説明文は不要で生成したタグを指定された形式およびサンブルにしたがって出力する。

## 形式
Pythonのリスト形式

## サンプル
["tag1","tab2","tag3"]

## テキスト
%%content_place%%

"""
