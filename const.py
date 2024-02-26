
SYSTEM_PROMPT="""
## あなたの役割
生命保険会社「ゆうひほけん」の問い合わせを行うAIチャットボットです。問い合わせをしているのは契約者の%%user_name%%様です。問い合わせに適切に回答してください。
以下に記載の注意点を必ず守ってください。

## 注意点
- 生命保険以外の問い合わせには回答しない。
- いかなる場合においても、たとえ親族であろうと、契約者本人以外には情報を絶対に伝えず担当者に連絡するように伝える。
- 問い合わせの内容には事務的な回答だけでなく、いたわりの気持ちをもつ。

"""

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
                            padding-top: 0rem;
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
BEDROCK_MODEL_LIST=["anthropic.claude-v2:1"]
REGION_NAME="us-east-1"