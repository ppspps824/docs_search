import streamlit as st
import boto3
import json
import const


def init_page():

    if "messages" not in st.session_state:
        st.session_state.messages=[]
        
    st.set_page_config(page_title="ゆうひほけんチャット", page_icon="❣️")
    st.markdown(const.HIDE_ST_STYLE,unsafe_allow_html=True)
    # サイドバーを表示
    st.sidebar.title("基盤モデル設定")
    
    # 左サイドバー
    with st.sidebar:
        bedrock_model = st.selectbox("Bedrockのモデルを選択してください", (const.BEDROCK_MODEL_LIST))
        st.session_state["bedrock_model"] = bedrock_model
    
        st.session_state["knowledge_base_id"] = st.secrets["KNOWLEDGE_ID"]
        st.session_state["rag_on"] = st.toggle("Knowledge base",value=True)
    
def show_page():
    st.markdown("<center><h1>ゆうひほけんチャット🌇</h1></center>",unsafe_allow_html=True)
    # 過去のやり取りを表示
    with st.chat_message("Assistant"):
        st.write("伊藤 智也さん、こんにちは！何かお困りごとはありますか？")
    for info in st.session_state.messages:
        with st.chat_message(info["role"]):
            st.write(info["content"])

    # ユーザーからの新しい入力を取得(Bedrock用)
    if prompt := st.chat_input(""):
        st.session_state.messages.append({"role": "Human", "content": prompt})
        with st.chat_message("Human"):
            st.markdown(prompt)
    
        with st.chat_message("Assistant"):
            message_placeholder = st.empty()
            full_response = ""
            if st.session_state["rag_on"]:
                full_response = _retrieve_and_generate(prompt,message_placeholder,full_response)
            else:
                full_response = _invoke_model_with_response_stream_claude(message_placeholder, full_response)
                
        st.session_state.messages.append({"role": "Assistant", "content": full_response})

def _invoke_model_with_response_stream_claude(message_placeholder, full_response,docs_input=""):
    # Bedrockからのストリーミング応答を処理

    bedrock = boto3.client(service_name="bedrock-runtime", region_name=const.REGION_NAME)
    messages = [m["role"] + ":" + m["content"] for m in st.session_state.messages]

    body = json.dumps(
        {
            "prompt": "system:"+const.SYSTEM_PROMPT+ "infomations:"+docs_input+"\n\n" + "\n\n".join(messages) + "\n\nAssistant:",
            "max_tokens_to_sample":1000
        }
    )
    try:
        response = bedrock.invoke_model_with_response_stream(modelId=st.session_state["bedrock_model"], body=body)
    except:
        st.error("エラーが発生しました。しばらく時間をおいてから再度ご利用ください。")
        st.stop()
    
    stream = response.get("body")
    if stream:
        for event in stream:
            chunk = event.get("chunk")
            if chunk:
                full_response += json.loads(chunk.get("bytes").decode("utf-8"))["completion"]
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.write(full_response)

    return full_response

def _retrieve_and_generate(input,message_placeholder,full_response):
    # BedrockからのRAG応答を処理

    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=const.REGION_NAME)
    with st.spinner("確認中..."):
        try:
            retrieve_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId= st.session_state["knowledge_base_id"],
            retrievalQuery={"text":input},
        )
        except:
            st.error("エラーが発生しました。しばらく時間をおいてから再度ご利用ください。")
            st.stop()

    full_response=_invoke_model_with_response_stream_claude(message_placeholder,full_response,retrieve_response["retrievalResults"][0]["content"]["text"])

    return full_response


if __name__ == "__main__":
    init_page()
    show_page()