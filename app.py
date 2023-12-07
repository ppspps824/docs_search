import json
import os
import tempfile
from pathlib import Path

import const
import openai
import streamlit as st
from llama_index import download_loader
from modules.database import Database
from streamlit_option_menu import option_menu


class DocsSearch:
    def __init__(_self):
        # OpenAIのクライアントを初期化
        openai.api_key = st.secrets["OPEN_AI_KEY"]

        # SupaBaseのコネクションを初期化
        _self.db = Database()

    def ask_ai(_self, prompt):
        response = openai.chat.completions.create(
            model="gpt-4-1106-preview", messages=[{"role": "user", "content": prompt}]
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
                PDFReader = download_loader("PDFReader")
                loader = PDFReader()
                documents = loader.load_data(file=fp)
            elif lower_ext in [".txt", ".md"]:
                MarkdownReader = download_loader("MarkdownReader")
                loader = MarkdownReader()
                documents = loader.load_data(file=fp)
            elif lower_ext == ".pptx":
                PptxReader = download_loader("PptxReader")
                loader = PptxReader()
                documents = loader.load_data(file=fp)
            elif lower_ext == ".docx":
                DocxReader = download_loader("DocxReader")
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
                PandasExcelReader = download_loader("PandasExcelReader")
                loader = PandasExcelReader(pandas_config={"header": None})
                documents = loader.load_data(file=fp)
            else:
                try:
                    MarkdownReader = download_loader("MarkdownReader")
                    loader = MarkdownReader()
                    documents = loader.load_data(file=fp)
                except:
                    st.error(f"非対応のファイル形式です。：{lower_ext}")
                    st.stop()
        content = documents[0].text

        return content

    def docs_upload(_self):
        st.header("ドキュメント取込")
        uploaded_files = st.file_uploader(
            "ドキュメントをアップロードしてください",
            type=[
                "txt",
                "md",
                "docx",
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
                for num, uploaded_file in enumerate(uploaded_files):
                    with st.spinner(
                        f"[{num+1}/{len(uploaded_files)}]{uploaded_file.name} 取込中..."
                    ):
                        content = _self.docs_read(uploaded_file)
                        summary = _self.generate_summary(content)
                        tags = _self.generate_tags(content)
                        _self.db.upload_document(uploaded_file, summary, tags)
                        with st.expander(
                            f"[{num+1}/{len(uploaded_files)}]取込完了:\n{uploaded_file.name}"
                        ):
                            st.write(summary)
                            st.write(tags)

    def requirements_input(_self):
        # ユーザー入力画面
        st.header("ドキュメント検索")
        user_input = st.text_area("実現したい機能を入力してください")
        if st.button("検索"):
            user_tags = _self.generate_tags(user_input, from_docs=False)  # タグ生成
            st.json(user_tags)
            modules = _self.db.search_documents_by_tags(user_tags)
            print(modules)
            if modules:
                for module in modules:
                    module_name = module["name"]
                    with st.expander(module_name):
                        document = _self.db.get_document_by_name(module_name)[0]
                        st.write(document["summary"])
                        st.write(document["tags"])
            else:
                st.write("該当するモジュールなし")

    def show_docs(_self):
        # ドキュメントDB照会画面
        st.header("ドキュメントDB照会")

        # ドキュメントの一覧を取得
        documents = _self.db.get_all_documents()
        document_names = [doc["name"] for doc in documents]
        selected_document_name = st.selectbox(
            "ドキュメントを選択してください", document_names
        )

        # 選択されたドキュメントの詳細情報を表示
        if selected_document_name:
            selected_document = next(
                (doc for doc in documents if doc["name"] == selected_document_name),
                None,
            )
            if selected_document:
                st.write("ドキュメント名: " + selected_document["name"])
                st.write("機能の要約: " + selected_document["summary"])
                st.write("タグ", selected_document["tags"])
            else:
                st.error("ドキュメントが見つかりませんでした。")

    def main(_self):
        # Streamlit UI
        selected = option_menu(
            "共通モジュール検索システム Ver.0.1",
            ["ドキュメント検索", "ドキュメント取込", "ドキュメントDB照会"],
            icons=["bi-universal-access", "bi-brush", "bi-play-btn"],
            menu_icon="bi-book",
            default_index=0,
            orientation="horizontal",
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

        if selected == "ドキュメント検索":
            _self.requirements_input()
        elif selected == "ドキュメント取込":
            _self.docs_upload()
        elif selected == "ドキュメントDB照会":
            _self.show_docs()


if __name__ == "__main__":
    st.set_page_config(
        page_title="共通モジュール検索システム", page_icon="📚", layout="wide"
    )
    st.markdown(const.HIDE_ST_STYLE, unsafe_allow_html=True)
    app = DocsSearch()
    app.main()
