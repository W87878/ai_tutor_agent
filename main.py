from fastapi import FastAPI, WebSocket
# from agents.pdf_agent import pdf_qa_agent
from agents.pdf_agent import pdf_qa_agent_stream
from agents.math_agent import math_solver_agent
from agents.review_agent import review_summary_agent
from memory.chat_memory import get_memory
from langchain_openai import OpenAI
from dotenv import load_dotenv 
from starlette.websockets import WebSocketDisconnect

load_dotenv()  # 載入環境變數
import os
# 確保已經設定了 OPENAI_API_KEY 環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 取得環境變數的值
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

app = FastAPI()

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

def detect_intent(text):
    prompt = f"""
    你是一個專門用來判斷語句意圖的分類器，請根據句子的內容，推理並分類為以下其中一類：
    - MATH：如果句子是純算數問題（可以直接計算的），屬於 MATH。
    - PDF：如果是與數學知識、公式、概念、理解、應用等相關的問題，屬於 PDF。
    - REVIEW：如果是複習、整理、總結學習內容的需求，屬於 REVIEW。
    - OTHER：不屬於以上任一類。

    請模仿以下範例的格式與推理方式進行判斷，並只輸出分類名稱（MATH、PDF、REVIEW 或 OTHER）：

    ---

    **範例 1：**  
    句子：12 + 5 是多少？  
    推理：這是一個可以直接計算的加法問題，屬於純算數問題。  
    分類：MATH

    ---

    **範例 2：**  
    句子：如何解一元二次方程式？  
    推理：這是對某個數學概念的詢問，屬於數學知識問題。  
    分類：PDF

    ---

    **範例 3：**  
    句子：幫我整理今天學習的內容。  
    推理：這是要求對既有學習內容進行複習與整理。  
    分類：REVIEW

    ---

    **範例 4：**  
    句子：你今天心情怎麼樣？  
    推理：這是一句日常對話，與數學或複習無關。  
    分類：OTHER

    ---

    **請根據上述邏輯推理以下句子：**  
    句子：{text}

    請直接輸出分類名稱（MATH、PDF、REVIEW 或 OTHER），不要包含推理過程。
    """
    intent = llm.invoke(prompt).strip().replace("分類：", "").upper()
    if intent not in ["PDF", "MATH", "REVIEW"]:
        intent = "OTHER"
    return intent

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     memory = get_memory()
#     while True:
#         try:
#             data = await websocket.receive_text()
            
#             if not data.strip():
#                 await websocket.send_text("請輸入內容")
#                 return
            
#             intent = detect_intent(data)
#             print(f"使用者輸入：{data}，判斷意圖：{intent}")
#             if intent == "PDF":
#                 response = pdf_qa_agent(data, memory)
#             elif intent == "MATH":
#                 response = math_solver_agent(data, memory)
#             elif intent == "REVIEW":
#                 response = review_summary_agent(data, memory)
#             else:
#                 response = (
#                     "請明確輸入您的需求，例如：\n"
#                     "- 查詢數學概念（例如：如何解聯立方程式）\n"
#                     "- 進行簡單算數（例如：12 * 7 是多少）\n"
#                     "- 整理複習重點（例如：幫我整理今天的內容）"
#                 )
#             await websocket.send_text(response)
#         except WebSocketDisconnect:
#             print("使用者中斷連線")
#             break
#         except Exception as e:
#             print(f"處理過程中發生錯誤：{e}")
#             await websocket.send_text("伺服器發生錯誤，請稍後再試")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    memory = get_memory()
    try:
        while True:
            data = await websocket.receive_text()
            intent = detect_intent(data)

            async def stream_agent(agent_func):
                async for chunk in agent_func(data, memory):
                    await websocket.send_text(chunk)

            if intent == "PDF":
                await stream_agent(pdf_qa_agent_stream)
            elif intent == "MATH":
                await websocket.send_text(math_solver_agent(data, memory))  # 假設這不需要 stream
            elif intent == "REVIEW":
                await websocket.send_text(review_summary_agent(data, memory))  # 同上
            else:
                # OTHER 類型：讓 LLM 根據整段歷史給出一般性對答
                history = memory.load_memory_variables({})["history"]
                print(history)
                prompt = f"""
                    你是一位親切的教育顧問，請根據以下歷史對話與使用者的最新問題，給出自然且有幫助的回應。

                    歷史對話：
                    {history}

                    使用者提問：
                    {data}

                    請回覆：
                    
                    若不太清楚使用者的意思，請給出一些引導性問題或建議，幫助使用者更清楚地表達需求。
                    例如：請明確輸入您的需求，例如PDF查詢、數學計算或複習摘要
                """
                response = llm.invoke(prompt)
                await websocket.send_text(response)

    except WebSocketDisconnect:
        print("客戶端中斷連線")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# This code sets up a FastAPI application with a WebSocket endpoint.    