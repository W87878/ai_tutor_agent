def review_summary_agent(query, memory):
    # 根據歷史對話生成摘要
    history = memory.load_memory_variables({})["history"]
    points = "\n".join([f"- {line}" for line in history.splitlines() if line])
    summary = f"以下是你的複習重點整理：\n{points}"
    memory.save_context({"input": query}, {"output": summary})
    return summary