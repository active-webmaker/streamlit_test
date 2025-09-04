import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 로드 (환경변수 우선)
load_dotenv(override=False)

st.set_page_config(page_title="부트캠프 멘토 챗봇", page_icon="🧑‍💻", layout="centered")

st.title("🧑‍💻 부트캠프 멘토 챗봇")

# 간단한 스타일 개선
st.markdown(
    """
    <style>
      .stChatMessage {font-size: 1.02rem}
      .st-emotion-cache-ue6h4q {max-width: 900px; margin: auto;}
      .st-emotion-cache-1jicfl2 {max-width: 900px; margin: auto;}
      .st-emotion-cache-13k62yr {max-width: 900px; margin: auto;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("설정")
openai_api_key = st.sidebar.text_input("OpenAI 키를 입력하세요", type="password")

if st.sidebar.button("대화 초기화"):
    st.session_state.pop("messages", None)
    st.rerun()

if not openai_api_key:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.sidebar.warning("OpenAI 키를 입력해주세요.")
        st.stop()

client = OpenAI(api_key=openai_api_key)

model = st.sidebar.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4"])
temperature = st.sidebar.slider("응답 온도", min_value=0.0, max_value=1.0, value=0.7)

if "messages" not in st.session_state:
    st.session_state.messages = [  
        {"role": "system", 
         "content": (
             "당신은 부트캠프 참가자를 돕는 멘토 챗봇입니다. 기본적으로 한국어로 답하고, 필요 시 영어 병기도 제공합니다. "
             "다루는 주제는 프로그래밍 학습, 커리어 조언, 과제 힌트, 프로젝트 기획/디버깅, 학습전략 등 부트캠프 관련 내용으로 제한합니다. "
             "부정확한 정보는 만들지 말고, 모르는 내용은 모른다고 말한 뒤 신뢰할 수 있는 접근 방법(검색 키워드, 공식 문서 경로)을 제안하세요. "
             "답변은 가능한 한 구조적으로 제공하고(개요→단계→예시→다음 단계), 필요한 경우 추가 질문으로 요구사항을 명확히 하세요."
         )
        }  
    ]

# 사용 가이드 & 안내
with st.expander("사용 가이드 보기", expanded=True):
    st.markdown(
        """
- 명확한 목표를 적어주세요: 예) "파이썬으로 파일 입출력 예제를 알려줘"
- 코드/에러는 그대로 붙여넣기: 가능한 한 전체 Traceback과 코드 블록을 포함하세요.
- 원하는 답변 형식을 지정: 예) 단계별 가이드, 코드 예제, 체크리스트 등
- 범위를 제한: 예) "Streamlit에서 파일 업로드 부분만"
- 개인 정보는 공유하지 마세요. 예) 이메일/전화번호/액세스 키 등
        """
    )
st.markdown(
    "<hr style='margin: 0.5rem 0 1rem 0; opacity: 0.3;'>",
    unsafe_allow_html=True,
)

# 이전 대화 표시
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    role = message["role"]
    avatar = "🧑‍🎓" if role == "user" else "🤖"
    with st.chat_message("user" if role == "user" else "assistant", avatar=avatar):
        st.markdown(message["content"])

# 사용자 입력 (챗 입력창) 및 스트리밍 응답
if prompt := st.chat_input("부트캠프 관련 질문을 입력하세요…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_content = ""
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_content += delta
                    placeholder.markdown(full_content)
        except Exception as e:
            st.error(f"응답 중 오류가 발생했어요: {e}")
            full_content = ""
        if full_content:
            st.session_state.messages.append({"role": "assistant", "content": full_content})