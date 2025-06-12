import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv 
load_dotenv('.env')  # 載入環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")


# 預先讀文件建立索引，避免每次查詢都重建
def build_vectorstore():
    docs = []
    for f in os.listdir("docs"):
        if f.endswith(".pdf") or f.endswith(".txt"):
            loader = PyMuPDFLoader(f"docs/{f}")
            docs.extend(loader.load())
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = FAISS.from_documents(texts, embeddings)
    print(f"Vectorstore built with {len(texts)} chunks.")
    # 儲存索引到本地，避免每次都重建
    # 如果需要重新建立索引，可以刪除 "vectorstore/faiss_index" 目錄
    if not os.path.exists("vectorstore/faiss_index"):
        os.makedirs("vectorstore/faiss_index")
        vectordb.save_local("vectorstore/faiss_index")
    else:
        print("Using existing vectorstore index.")
        vectordb = FAISS.load_local(
            "vectorstore/faiss_index",
            OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
            allow_dangerous_deserialization=True
        )
    return vectordb

# vectordb = build_vectorstore()

def query_rag(query, history=None):
    vectordb = build_vectorstore()
    results = vectordb.similarity_search(query, k=3)
    print(results)
    return "\n".join([doc.page_content for doc in results])
