import streamlit as st
import boto3
import json
import const

def user_change():
    st.session_state.messages=[]

def init():
    if "messages" not in st.session_state:
        st.session_state.messages=[]
        
    st.set_page_config(page_title="ゆうひほけんチャット", page_icon="❣️")
    st.markdown(const.HIDE_ST_STYLE,unsafe_allow_html=True)
    st.session_state["knowledge_base_id"] = st.secrets["KNOWLEDGE_ID"]
    
    # 左サイドバー
    with st.sidebar:
        st.session_state["user_name"] = st.selectbox("契約者を選択",options=["伊藤 智也","田中 真綾","加藤 充","松田 結衣"],on_change=user_change)
        bedrock_model = st.selectbox("Bedrockのモデルを選択してください", (const.BEDROCK_MODEL_LIST))
        st.session_state["bedrock_model"] = bedrock_model
    
def main():
    st.markdown("<center><h1>ゆうひほけんチャット🌇</h1></center>",unsafe_allow_html=True)

    with st.chat_message("Assistant"):
        st.write(f"{st.session_state['user_name']}さん、こんにちは！何かお困りごとはありますか？")
    for info in st.session_state.messages:
        with st.chat_message(info["role"]):
            st.write(info["content"])

    if prompt := st.chat_input(""):
        st.session_state.messages.append({"role": "Human", "content": prompt})
        with st.chat_message("Human"):
            st.markdown(prompt)
    
        with st.chat_message("Assistant"):
            message_placeholder = st.empty()
            response = retrieve(prompt,message_placeholder)
                
        st.session_state.messages.append({"role": "Assistant", "content": response})

def invoke_model(message_placeholder, docs_input=""):
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=const.REGION_NAME)
    messages = [message["role"] + ":" + message["content"] for message in st.session_state.messages]

    body = json.dumps(
        {
            "prompt": "system:"+const.SYSTEM_PROMPT.replace("%%user_name%%",st.session_state["user_name"])+ "infomations:"+docs_input+"\n\n" + "\n\n".join(messages) + "\n\nAssistant:",
            "max_tokens_to_sample":1000
        }
    )
    try:
        with st.spinner("確認中..."):
            response = bedrock.invoke_model(modelId=st.session_state["bedrock_model"], body=body)
        stream = response.get("body")
        full_response=""
        if stream:
            for event in stream:
                chunk = event.get("chunk")
                if chunk:
                    full_response += json.loads(chunk.get("bytes").decode("utf-8"))["completion"]
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.write(full_response)
    except:
        st.error("エラーが発生しました。しばらく時間をおいてから再度ご利用ください。")
        st.stop()

    return full_response

def retrieve(input,message_placeholder):
    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=const.REGION_NAME)
    try:
        with st.spinner("確認中..."):
            retrieve_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId= st.session_state["knowledge_base_id"],
            retrievalQuery={"text":input},
        )
    except:
        st.error("エラーが発生しました。しばらく時間をおいてから再度ご利用ください。")
        st.stop()

    full_response=invoke_model(message_placeholder,retrieve_response["retrievalResults"][0]["content"]["text"])

    return full_response


if __name__ == "__main__":
    init()
    main()