from rag.vectorstore import query_rag

# def pdf_qa_agent(query, memory):
#     history = memory.load_memory_variables({})["history"]
#     result = query_rag(query, history)
#     memory.save_context({"input": query}, {"output": result})
#     return result

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
import asyncio
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from dotenv import load_dotenv
load_dotenv()  # 載入環境變數
import os
# 確保已經設定了 OPENAI_API_KEY 環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 取得環境變數的值
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
from rag.vectorstore import build_vectorstore  # 你自己的 FAISS 載入器

async def pdf_qa_agent_stream(query, memory):
    # Step 1: 準備向量資料庫與檢索器
    vectordb = build_vectorstore()
    retriever = vectordb.as_retriever()

    # Step 2: Streaming LLM
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        temperature=0,
        streaming=True,
        callbacks=[callback],
    )

    prompt_template = PromptTemplate.from_template("""
        你是一位數學助教，擅長根據教材內容幫助學生解題與理解。請直接根據教材作答，不要重述問題，也不要反問。請具體說明，並避免籠統或模糊的回答。

        教材內容：
        {context}

        學生問題：
        {question}

        請回答：
    """)

    # Step 3: Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        ("human", "{question}")
    ])

    # Step 4: Chain 組合
    def format_docs(docs: list[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Step 5: 啟動生成 + 回傳串流 token
    task = asyncio.create_task(rag_chain.ainvoke(query))
    full_response = ""
    async for chunk in callback.aiter():
        full_response += chunk
        yield chunk
    await task
    memory.save_context({"input": query}, {"output": full_response})