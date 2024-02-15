import json
import os
import tempfile
import time
from pathlib import Path

import const
import openai
import streamlit as st
from llama_index import download_loader
from modules.database import Database
from modules.s3 import s3_get_index
from streamlit_option_menu import option_menu


class DocsSearch:
    def __init__(_self):
        # OpenAIのクライアントを初期化
        openai.api_key = st.secrets["OPEN_AI_KEY"]

        if "all_text" not in st.session_state:
            st.session_state.all_text = []

        # SupaBaseのコネクションを初期化
        _self.db = Database()

    def ask_ai(_self, prompt):
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_tags(_self, content, from_docs=True):
        with st.spinner("タグ生成中..."):
            prompt = (
                const.FROM_DOCS_TAGS_PROMPT
                if from_docs
                else const.FROM_INPUT_TAGS_PROMPT
            )
            for num in range(3):
                try:
                    response = _self.ask_ai(
                        prompt.replace("%%content_place%%", content)
                    )
                    user_tags = json.loads(
                        response.replace("```", "").replace("json", "")
                    )
                    return user_tags
                except Exception as e:
                    print(e.args)
                    print(f"[{num}/3]Falid:{response}")
            st.error("タグ生成失敗")
            st.stop()

    def generate_summary(_self, content):
        with st.spinner("要約文生成中..."):
            for num in range(3):
                try:
                    response = _self.ask_ai(
                        const.SUMMARY_PROMPT.replace("%%content_place%%", content)
                    )
                    return response
                except Exception as e:
                    print(e.args)
                    print(f"[{num}/3]Falid:{response}")
            st.error("要約文生成失敗")
            st.stop()

    def docs_read(_self, uploaded_file):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            fp = Path(tmp_file.name)
            fp.write_bytes(uploaded_file.getvalue())
            _, ext = os.path.splitext(uploaded_file.name)
            lower_ext = ext.lower()
            if lower_ext == ".pdf":
                PDFReader = download_loader("PDFReader", custom_path="local_dir")
                loader = PDFReader()
                documents = loader.load_data(file=fp)
            elif lower_ext in [".txt", ".md"]:
                MarkdownReader = download_loader(
                    "MarkdownReader", custom_path="local_dir"
                )
                loader = MarkdownReader()
                documents = loader.load_data(file=fp)
            elif lower_ext == ".pptx":
                PptxReader = download_loader("PptxReader", custom_path="local_dir")
                loader = PptxReader()
                documents = loader.load_data(file=fp)
            elif lower_ext == ".docx":
                DocxReader = download_loader("DocxReader", custom_path="local_dir")
                loader = DocxReader()
                documents = loader.load_data(file=fp)
            elif lower_ext in [
                ".xls",
                ".xlsx",
                ".xlsm",
                ".xlsb",
                ".odf",
                ".ods",
                ".odt",
            ]:
                PandasExcelReader = download_loader(
                    "PandasExcelReader", custom_path="local_dir"
                )
                loader = PandasExcelReader(pandas_config={"header": None})
                documents = loader.load_data(file=fp)
            else:
                try:
                    MarkdownReader = download_loader(
                        "MarkdownReader", custom_path="local_dir"
                    )
                    loader = MarkdownReader()
                    documents = loader.load_data(file=fp)
                except:
                    st.error(f"非対応のファイル形式です。：{lower_ext}")
                    st.stop()
        return documents

    def docs_upload(_self):
        st.header("ドキュメント取込")
        uploaded_files = st.file_uploader(
            "ドキュメントをアップロードしてください",
            type=[
                ".txt",
                ".pptx",
                ".pdf",
                ".md",
                ".docx",
                ".xls",
                ".xlsx",
                ".xlsm",
                ".xlsb",
                ".odf",
                ".ods",
                ".odt",
            ],
            accept_multiple_files=True,
        )
        if st.button("取り込み"):
            if uploaded_files:
                contents = []
                for num, uploaded_file in enumerate(uploaded_files):
                    with st.spinner(
                        f"[{num+1}/{len(uploaded_files)}]{uploaded_file.name} 取込中..."
                    ):
                        contents.append(_self.docs_read(uploaded_file))

                        for content in contents:
                            try:
                                _self.db.insert_index(content)
                            except Exception as e:
                                print(e.args)
                                _self.db.create_vector_store_index(content)

                st.info("取込完了")

    def requirements_input(_self):
        # ユーザー入力画面
        user_prompt = st.chat_input("user:")
        assistant_text = ""

        for text_info in st.session_state.all_text:
            with st.chat_message(text_info["role"], avatar=text_info["role"]):
                st.write(text_info["role"] + ":\n\n" + text_info["content"])

        if user_prompt:
            with st.chat_message("user", avatar="user"):
                st.write("user" + ":\n\n" + user_prompt)

            st.session_state.all_text.append({"role": "user", "content": user_prompt})

            if len(st.session_state.all_text) > 10:
                st.session_state.all_text.pop(1)

            response = _self.db.query_index(s3_get_index(), user_prompt)

            with st.chat_message("assistant", avatar="assistant"):
                place = st.empty()
                for next_text in response.response_gen:
                    content = next_text.replace("。", "。\n\n")
                    if content:
                        assistant_text += content
                        place.write("assistant" + ":\n\n" + assistant_text)

            st.session_state.all_text.append(
                {"role": "assistant", "content": assistant_text}
            )

    def show_docs(_self):
        # ドキュメントDB照会画面
        st.header("DB照会")
        doc_ids = _self.db.view_index()
        select_doc_id = st.selectbox("削除するdoc_idを選択", options=doc_ids)
        if st.button("削除"):
            _self.db.delete_index(select_doc_id)
            st.info("削除しました。")
            time.sleep(0.5)
            st.rerun()

    def main(_self):
        # Streamlit UI
        with st.sidebar:
            selected = option_menu(
                "ほけんAIチャット",
                ["チャット", "資料取り込み", "DB照会"],
                icons=["bi-chat-dots", "bi-cloud-arrow-up", "bi-book"],
                menu_icon="bi-search",
                default_index=0,
                styles={
                    "container": {
                        "margin": "0!important",
                        "padding": "0!important",
                        "background-color": "#fafafa",
                    },
                    "icon": {"color": "fafafa", "font-size": "25px"},
                    "nav-link": {
                        "font-size": "20px",
                        "margin": "0px",
                        "--hover-color": "#eee",
                    },
                    "nav-link-selected": {"background-color": "004a55"},
                },
            )

        if selected == "チャット":
            _self.requirements_input()
        elif selected == "資料取り込み":
            _self.docs_upload()
        elif selected == "DB照会":
            _self.show_docs()


if __name__ == "__main__":
    st.set_page_config(
        page_title="ほけんAIチャット", page_icon="❣️"
    )
    st.markdown(const.HIDE_ST_STYLE, unsafe_allow_html=True)
    app = DocsSearch()
    app.main()
