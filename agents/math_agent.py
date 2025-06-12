def math_solver_agent(query, memory):
    # 模擬簡單計算處理
    try:
        result = str(eval(query, {}, {}))
    except:
        result = "無法解析數學問題"
    memory.save_context({"input": query}, {"output": result})
    return result