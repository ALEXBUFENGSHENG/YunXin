from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import date, datetime
from app.models.math import MathOnboardRequest, MathAttemptRequest, MathTodayTasksResponse, MathTask
from mysql_storage import mysql_storage
from app.services.llm_service import get_llm_service
import json

router = APIRouter(prefix="/api/math", tags=["math"])

@router.post("/onboard")
async def onboard(request: MathOnboardRequest):
    """初始化数学学习画像"""
    user_id = mysql_storage.get_user_id(request.username)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    success = mysql_storage.save_math_profile(
        user_id, 
        request.exam_name, 
        request.target_score, 
        request.exam_date, 
        request.daily_hours, 
        request.resources_config
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="保存画像失败")
    
    return {"message": "Onboarding successful", "status": "ready"}

@router.get("/today", response_model=MathTodayTasksResponse)
async def get_today_tasks(username: str):
    """获取今日数学学习任务"""
    user_id = mysql_storage.get_user_id(username)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 强制获取库中前 10 道真实题目作为任务
    connection = mysql_storage.get_connection()
    tasks = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, stem, tags FROM math_problems LIMIT 10")
            problems = cursor.fetchall()
            
            for p in problems:
                tags = json.loads(p['tags']) if isinstance(p['tags'], str) else p['tags']
                tasks.append(MathTask(
                    id=f"task_p_{p['id']}",
                    type="practice",
                    content=p['stem'],
                    duration_min=20,
                    metadata={"problem_id": p['id'], "tags": tags}
                ))
    except Exception as e:
        print(f"获取任务异常: {e}")
        # 数据库连接失败时提供演示题目
        demo_problems = [
            {
                "id": 1,
                "stem": r"（2023数一）求极限 $\lim_{n \to \infty} \sum_{k=1}^n \frac{k}{n^2 + k^2}$。",
                "tags": ["定积分定义", "极限计算", "高数"]
            },
            {
                "id": 2,
                "stem": r"（2022数一）设 $z = z(x, y)$ 由方程 $x^2 + y^2 + z^2 = 3xyz$ 确定，求 $\frac{\partial z}{\partial x}$。",
                "tags": ["隐函数求导", "多元函数微分", "高数"]
            },
            {
                "id": 3,
                "stem": r"（2021数一）已知矩阵 $A$ 的特征值为 1, 2, 3，求 $A^2 - 3A + 2E$ 的特征值。",
                "tags": ["特征值", "矩阵运算", "线代"]
            }
        ]
        
        for p in demo_problems:
            tasks.append(MathTask(
                id=f"demo_p_{p['id']}",
                type="practice",
                content=p['stem'],
                duration_min=20,
                metadata={"problem_id": p['id'], "tags": p['tags']}
            ))

    if not tasks:
        return MathTodayTasksResponse(tasks=[], summary="题库暂无数据，请检查数据库初始化状态。")
    
    return MathTodayTasksResponse(
        tasks=tasks,
        summary=f"已为你从真题库中提取了 {len(tasks)} 道核心训练题。"
    )

@router.get("/problem/{problem_id}")
async def get_problem_detail(problem_id: int):
    """获取题目详情"""
    connection = mysql_storage.get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM math_problems WHERE id = %s", (problem_id,))
        problem = cursor.fetchone()
        if not problem:
            raise HTTPException(status_code=404, detail="题目不存在")
        return problem

@router.post("/attempt")
async def submit_attempt(request: MathAttemptRequest):
    """提交作答记录并获取 AI 点评"""
    user_id = mysql_storage.get_user_id(request.username)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 1. 获取题目详情用于 AI 上下文
    problem_content = "未知题目"
    try:
        connection = mysql_storage.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT stem FROM math_problems WHERE id = %s", (request.problem_id,))
            res = cursor.fetchone()
            if res:
                problem_content = res['stem']
    except Exception as e:
        print(f"Failed to fetch problem: {e}")

    # 2. 调用 AI 进行深度批改 (基于云心模型)
    analysis_result = {}
    try:
        # 构造 prompt 请求结构化分析
        prompt = f"""
        你是一位考研数学阅卷专家。请对学生的解题步骤进行深度诊断。
        
        题目：{problem_content}
        学生作答：{request.user_steps}
        
        请输出 JSON 格式（不要输出 Markdown 代码块标记），包含以下字段：
        1. scores: 维度评分 (0-1)，包含 logic (逻辑严密性), calculation (计算准确度), completeness (步骤完整性)。
        2. error_tags: 错误类型标签列表 (如：计算错误, 公式误用, 审题不清, 逻辑跳跃)。
        3. feedback: 简短的阅卷点评 (Markdown格式)。
        4. solution_path: 标准解题路径的关键步骤列表 (用于生成图谱)，例如 ["审题", "列出方程", "解微分方程", "代入初值"]。
        5. guidance: 思路引导，如果下次遇到此类题应该怎么想。
        """
        
        response = await get_llm_service().generate_response([
            {"role": "system", "content": "你是一个严格的数学阅卷AI。只输出纯 JSON。"},
            {"role": "user", "content": prompt}
        ])
        
        # 清洗 JSON
        clean_json = response.replace("```json", "").replace("```", "").strip()
        analysis_result = json.loads(clean_json)
        
        # 提取 feedback 用于兼容旧字段
        ai_feedback = analysis_result.get("feedback", "阅卷完成。")
        
    except Exception as e:
        print(f"AI grading failed: {e}")
        ai_feedback = "AI 老师正在休息，无法提供深度诊断。请稍后查看复盘报告。"
        analysis_result = {
            "scores": {"logic": 0.5, "calculation": 0.5, "completeness": 0.5},
            "error_tags": ["系统繁忙"],
            "solution_path": ["未知路径"],
            "guidance": "请检查网络连接。"
        }

    # 3. 保存记录 (增强字段)
    # 注意：mysql_storage.save_math_attempt 可能需要更新以存储 analysis_result，或者我们暂时只存 error_tags
    # 这里为了演示，我们先不改数据库 schema，只在返回给前端时携带数据
    success = mysql_storage.save_math_attempt(
        user_id,
        request.problem_id,
        request.self_score,
        request.time_spent_sec,
        request.user_steps,
        request.key_check_result,
        request.error_tags or analysis_result.get("error_tags", [])
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="保存作答记录失败")
    
    # 如果分数较低，自动加入复习队列
    if request.self_score <= 3:
        # TODO: 插入 math_study_items
        pass

    return {
        "message": "Attempt saved", 
        "status": "success",
        "feedback": ai_feedback,
        "analysis": analysis_result # 返回完整的结构化分析
    }

@router.get("/progress")
async def get_progress(username: str):
    """获取学习进度"""
    user_id = mysql_storage.get_user_id(username)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    mastery = mysql_storage.get_math_kp_mastery(user_id)
    profile = mysql_storage.get_math_profile(user_id)
    
    return {
        "mastery": mastery,
        "profile": profile,
        "summary": {
            "completed_hours": 0, # TODO: 从 attempts 计算
            "accuracy": 0.85 # TODO: 从 attempts 计算
        }
    }
