from langchain.agents import Tool

def check_status(student_id):
    # 模擬報名系統查詢
    return f"學員 {student_id} 的報名狀態為：已完成報名，等待繳費。"

def get_enrollment_status_tool():
    return Tool(
        name="EnrollmentStatusChecker",
        func=lambda x: check_status(x),
        description="查詢學生的報名狀態，輸入學生編號"
    )
