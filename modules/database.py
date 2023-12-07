import streamlit as st
from st_supabase_connection import SupabaseConnection


class Database:
    def __init__(_self, connection_name: str = "init"):
        print("__init_")
        _self.supabase = _self.get_connection(connection_name)

    @st.cache_resource
    def get_connection(_self, connection_name):
        print("get_connection")
        supabase = st.connection(
            name=connection_name,
            type=SupabaseConnection,
            url=st.secrets["supabase_url"],
            key=st.secrets["supabase_key"],
        )
        return supabase

    def get_document_by_name(_self, document_name):
        result = (
            _self.supabase.table("documents")
            .select("*")
            .eq("name", document_name)
            .execute()
        )
        return result.data

    def get_all_documents(_self):
        result = _self.supabase.table("documents").select("*").execute()
        return result.data

    def delete_document(_self, document_name):
        # 関連するドキュメントタグを削除
        _self.supabase.table("document_tags").delete().eq(
            "name", document_name
        ).execute()

        # ドキュメント自体を削除
        _self.supabase.table("documents").delete().eq("name", document_name).execute()

    def upload_document(_self, file, summary, tags):
        # ドキュメントの内容をアップサート（挿入または更新）
        document_data = {"name": file.name, "summary": summary, "tags": tags}
        upserted_document = (
            _self.supabase.table("documents").upsert(document_data).execute()
        )

        name = upserted_document.data[0]["name"]

        # ドキュメントタグ関連をアップサート（挿入または更新）
        for tag in tags:
            _self.supabase.table("document_tags").upsert(
                {"name": name, "tag_id": tag}
            ).execute()

    def search_documents_by_tags(_self, tags):
        # タグに基づくドキュメントを検索

        final_results = []
        for tag in tags:
            search_term = f"%{tag}%"
            result = (
                _self.supabase.query("name,tag_id", table="document_tags")
                .ilike("tag_id", search_term)
                .execute()
            )
            print(tag, result.data)

            final_results.extend(result.data)

        return final_results
