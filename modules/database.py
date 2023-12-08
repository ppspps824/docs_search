import logging
import sys

import streamlit as st
from llama_index import VectorStoreIndex
from modules.s3 import s3_get_index, s3_upload

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


class Database:
    def __init__(_self):
        pass

    def create_vector_store_index(_self, documents):
        index = VectorStoreIndex.from_documents(documents)
        s3_upload(index)

        return index

    def query_index(_self, index, query):
        query_engine = index.as_query_engine(streaming=True)
        response = query_engine.query(query)
        return response

    def insert_index(_self, documents):
        index = s3_get_index()
        for doc in documents:
            index.insert(doc)
        s3_upload(index)

    def view_index(_self):
        try:
            index = s3_get_index()
        except Exception as e:
            print(e.args)
            st.error("作成されたindexがありません。")
            st.stop()

        joined_dict = {}
        for ref_doc_id, ref_doc_info in index.ref_doc_info.items():
            joined_text = ""
            for node_id in ref_doc_info.node_ids:
                joined_text += f"\n{index.storage_context.docstore.docs[node_id].text}"
            joined_dict[ref_doc_id] = joined_text

        st.dataframe(joined_dict)

        return joined_dict.keys()

    def delete_index(_self, doc_id):
        index = s3_get_index()
        # for ref_doc_id, ref_doc_info in index.ref_doc_info.items():
        #     for node_id in ref_doc_info.node_ids:
        #         index.storage_context.docstore.delete_document(node_id)
        index.delete(doc_id)

        s3_upload(index)
