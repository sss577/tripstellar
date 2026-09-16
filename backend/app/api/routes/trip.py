"""旅行规划 API 路由 - WebSocket 同步 + 轮询兼容模式（数据库持久化 + 用户隔离）"""

import asyncio
import traceback
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from ...agents.trip_planner_agent import get_trip_planner_agent
from ...database import AsyncSessionLocal
from ...models.db_models import TripTaskRecord, User
from ...models.schemas import TripPlanResponse, TripRequest
from ...services.auth_service import decode_access_token, generate_task_id
from ...services.knowledge_graph_service import build_knowledge_graph
from ..deps import get_current_user

router = APIRouter(prefix="/trip", tags=["旅行规划"])

# 内存任务状态（含 WebSocket 订阅者队列；持久化在数据库）
_tasks: Dict[str, Dict[str, Any]] = {}
_FINAL_TASK_STATUS = {"completed", "failed"}
_PRELOAD_LIMIT = 200


def _create_task_state(task_id: str, user_id: int) -> Dict[str, Any]:
    """初始化任务状态。"""
    return {
        "task_id": task_id,
        "user_id": user_id,
        "plan_id": task_id,
        "status": "processing",
        "stage": "submitted",
        "progress": 0,
        "message": "任务已提交，等待执行...",
        "result": None,
        "error": None,
        "request_payload": None,
        "subscribers": [],  # list[asyncio.Queue]
    }


def _serialize_result(result: Any) -> Any:
    if result is None:
        return None
    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")
    return result


async def _persist_task_state(task_id: str, task: Dict[str, Any]) -> None:
    """将任务状态持久化到数据库。"""
    try:
        async with AsyncSessionLocal() as session:
            record = await session.get(TripTaskRecord, task_id)
            if record is None:
                record = TripTaskRecord(task_id=task_id, user_id=task["user_id"])
                session.add(record)
            record.plan_id = task.get("plan_id", task_id)
            record.status = task.get("status", "processing")
            record.stage = task.get("stage", "")
            record.progress = task.get("progress", 0)
            record.message = str(task.get("message", ""))[:500]
            record.error = task.get("error")
            record.result = _serialize_result(task.get("result"))
            record.request_payload = task.get("request_payload")
            await session.commit()
    except Exception as e:
        print(f"⚠️  持久化任务 {task_id} 失败: {e}")


def _normalize_loaded_task(record: TripTaskRecord) -> Dict[str, Any]:
    """将数据库记录恢复为内存可用格式。"""
    task = _create_task_state(record.task_id, record.user_id)
    task.update(
        {
            "plan_id": record.plan_id or record.task_id,
            "status": record.status,
            "stage": record.stage,
            "progress": record.progress,
            "message": record.message,
            "result": record.result,
            "error": record.error,
            "request_payload": record.request_payload,
        }
    )
    task["subscribers"] = []

    # 服务重启后，处理中任务无法恢复执行，直接标记为失败，避免前端无限等待。
    if task["status"] not in _FINAL_TASK_STATUS:
        task["status"] = "failed"
        task["stage"] = "failed"
        task["progress"] = 100
        task["error"] = "服务已重启，未完成的旅行规划任务无法恢复，请重新生成。"
        task["message"] = task["error"]

    return task


async def _load_task_from_db(task_id: str) -> Dict[str, Any] | None:
    """从数据库加载单个任务并缓存到内存。"""
    async with AsyncSessionLocal() as session:
        record = await session.get(TripTaskRecord, task_id)
    if record is None:
        return None
    task = _normalize_loaded_task(record)
    _tasks[task_id] = task
    return task


async def load_persisted_tasks() -> None:
    """服务启动时预加载最近的已完成任务到内存。"""
    try:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(TripTaskRecord)
                .order_by(TripTaskRecord.updated_at.desc())
                .limit(_PRELOAD_LIMIT)
            )
            records = (await session.execute(stmt)).scalars().all()
    except Exception as e:
        print(f"⚠️  加载历史任务失败: {e}")
        return

    for record in records:
        _tasks[record.task_id] = _normalize_loaded_task(record)
    if records:
        print(f"📦 已从数据库加载 {len(records)} 个旅行任务")


async def _get_task(task_id: str) -> Dict[str, Any] | None:
    """优先从内存读取任务，不存在时回退到数据库。"""
    return _tasks.get(task_id) or await _load_task_from_db(task_id)


def _build_history_item(record: TripTaskRecord) -> Dict[str, Any] | None:
    """从数据库任务记录中提取首页历史列表所需的摘要。"""
    if record.status != "completed":
        return None

    result = record.result or {}
    plan = result.get("data") or {}
    request_payload = record.request_payload or {}

    city = plan.get("city") or request_payload.get("city") or ""
    cities = plan.get("cities") or []
    start_date = plan.get("start_date") or request_payload.get("start_date") or ""
    end_date = plan.get("end_date") or request_payload.get("end_date") or ""
    days = plan.get("days") or []
    travel_days = request_payload.get("travel_days") or (len(days) if isinstance(days, list) else 0)
    overall_suggestions = plan.get("overall_suggestions") or result.get("message") or ""

    if not city and not cities:
        return None

    # 多城市时 city 显示为 "北京 → 西安" 形式
    display_city = ' → '.join(cities) if len(cities) > 1 else city

    return {
        "plan_id": record.plan_id or record.task_id,
        "task_id": record.task_id,
        "city": display_city,
        "cities": cities,
        "start_date": start_date,
        "end_date": end_date,
        "travel_days": travel_days,
        "updated_at": record.updated_at.isoformat(timespec="seconds") if record.updated_at else "",
        "overall_suggestions": overall_suggestions,
    }


def _build_task_event(task_id: str, task: Dict[str, Any], include_result: bool = True) -> Dict[str, Any]:
    """从任务状态构建对前端可消费的事件对象。"""
    event = {
        "task_id": task_id,
        "plan_id": task.get("plan_id", task_id),
        "status": task.get("status", "processing"),
        "stage": task.get("stage", ""),
        "progress": task.get("progress", 0),
        "message": task.get("message", ""),
    }
    if task.get("error"):
        event["error"] = task["error"]
    if task.get("status") == "failed" and task.get("request_payload") is not None:
        event["request_payload"] = task["request_payload"]
    if include_result and task.get("result") is not None:
        event["result"] = _serialize_result(task["result"])
    return event


def _broadcast_task_event(task_id: str, event: Dict[str, Any]) -> None:
    """将任务事件广播给当前所有 WebSocket 订阅者。"""
    task = _tasks.get(task_id)
    if not task:
        return

    dead_queues = []
    for queue in task.get("subscribers", []):
        try:
            queue.put_nowait(event)
        except Exception:
            dead_queues.append(queue)

    if dead_queues:
        task["subscribers"] = [q for q in task.get("subscribers", []) if q not in dead_queues]


async def _update_task_state(
    task_id: str,
    *,
    status: str | None = None,
    stage: str | None = None,
    progress: int | None = None,
    message: str | None = None,
    result: Any = None,
    error: str | None = None,
) -> None:
    """更新任务状态并广播事件。"""
    task = _tasks.get(task_id)
    if not task:
        return

    if status is not None:
        task["status"] = status
    if stage is not None:
        task["stage"] = stage
    if progress is not None:
        task["progress"] = progress
    if message is not None:
        task["message"] = message
    if result is not None:
        task["result"] = result
    if error is not None:
        task["error"] = error

    await _persist_task_state(task_id, task)
    event = _build_task_event(task_id, task, include_result=True)
    _broadcast_task_event(task_id, event)


@router.post(
    "/plan",
    summary="提交旅行规划任务",
    description="异步提交旅行规划请求（需要登录），立即返回 task_id；可通过 WebSocket 或 /trip/status/{task_id} 获取执行状态",
)
async def plan_trip(
    request: TripRequest,
    user: User = Depends(get_current_user),
):
    """提交旅行规划任务（立即返回 task_id）。"""
    task_id = generate_task_id()
    _tasks[task_id] = _create_task_state(task_id, user.id)
    _tasks[task_id]["request_payload"] = request.model_dump(mode="json")
    await _persist_task_state(task_id, _tasks[task_id])

    _city_display = ' → '.join(cs.city for cs in request.cities) if request.cities else request.city
    print(f"\n{'=' * 60}")
    print(f"📥 收到旅行规划请求 (task_id={task_id}, user={user.username}):")
    print(f"   城市: {_city_display}")
    print(f"   日期: {request.start_date} - {request.end_date}")
    print(f"   天数: {request.travel_days}")
    print(f"{'=' * 60}\n")

    await _update_task_state(
        task_id,
        status="processing",
        stage="submitted",
        progress=5,
        message="任务已提交，正在初始化流程...",
    )

    # 启动后台任务
    asyncio.create_task(_run_trip_planning(task_id, request))

    return {
        "task_id": task_id,
        "plan_id": task_id,
        "status": "processing",
        "ws_url": f"/api/trip/ws/{task_id}",
        "message": f"任务已提交，可通过 WebSocket /api/trip/ws/{task_id} 实时订阅状态",
    }


async def _run_trip_planning(task_id: str, request: TripRequest):
    """后台执行旅行规划并推送进度。"""
    try:
        await _update_task_state(
            task_id,
            status="processing",
            stage="initializing",
            progress=10,
            message="正在获取多智能体系统实例...",
        )
        agent = get_trip_planner_agent()

        async def progress_callback(stage: str, message: str, progress: int) -> None:
            await _update_task_state(
                task_id,
                status="processing",
                stage=stage,
                progress=progress,
                message=message,
            )

        trip_plan = await agent.plan_trip(request, progress_callback=progress_callback)

        await _update_task_state(
            task_id,
            status="processing",
            stage="graph_building",
            progress=95,
            message="正在构建知识图谱...",
        )
        graph_data = build_knowledge_graph(trip_plan, language=getattr(request, 'language', 'zh') or 'zh')

        trip_result = TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            plan_id=task_id,
            data=trip_plan,
            graph_data=graph_data,
        )

        print(f"✅ 任务 {task_id} 完成")
        await _update_task_state(
            task_id,
            status="completed",
            stage="completed",
            progress=100,
            message="旅行计划生成成功",
            result=trip_result,
        )

    except Exception as e:
        print(f"❌ 任务 {task_id} 失败: {e}")
        traceback.print_exc()

        # 针对小红书 Cookie 过期异常做出特殊处理返回给前端
        try:
            from ...services.xhs_service import XHSCookieExpiredError

            if isinstance(e, XHSCookieExpiredError):
                error_msg = f"【认证失败】{str(e)}"
            else:
                error_msg = str(e)
        except ImportError:
            error_msg = str(e)

        await _update_task_state(
            task_id,
            status="failed",
            stage="failed",
            progress=100,
            message=error_msg,
            error=error_msg,
        )


@router.websocket("/ws/{task_id}")
async def trip_task_ws(websocket: WebSocket, task_id: str):
    """WebSocket 订阅任务状态（通过 ?token= 传递访问令牌）。"""
    await websocket.accept()

    # WebSocket 无法携带 Authorization 头，改用 query 参数校验令牌
    token = websocket.query_params.get("token")
    user_id = decode_access_token(token) if token else None
    if user_id is None:
        await websocket.send_json(
            {
                "task_id": task_id,
                "plan_id": task_id,
                "status": "failed",
                "stage": "failed",
                "progress": 100,
                "message": "未登录或令牌已失效",
                "error": "未登录或令牌已失效",
            }
        )
        await websocket.close(code=1008)
        return

    task = await _get_task(task_id)
    if not task or task.get("user_id") != user_id:
        # 任务不存在或无权访问（不泄露他人任务是否存在）
        await websocket.send_json(
            {
                "task_id": task_id,
                "plan_id": task_id,
                "status": "failed",
                "stage": "failed",
                "progress": 100,
                "message": "任务不存在",
                "error": "任务不存在",
            }
        )
        await websocket.close(code=1008)
        return

    queue: asyncio.Queue = asyncio.Queue()
    task["subscribers"].append(queue)

    # 先发送快照，保证前端后连也能同步当前状态
    snapshot = _build_task_event(task_id, task, include_result=True)
    await websocket.send_json(snapshot)
    if snapshot["status"] in _FINAL_TASK_STATUS:
        try:
            await websocket.close()
        except Exception:
            pass
        task["subscribers"] = [q for q in task.get("subscribers", []) if q is not queue]
        return

    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
            if event.get("status") in _FINAL_TASK_STATUS:
                break
    except WebSocketDisconnect:
        pass
    finally:
        task = _tasks.get(task_id)
        if task:
            task["subscribers"] = [q for q in task.get("subscribers", []) if q is not queue]
        try:
            await websocket.close()
        except Exception:
            pass


@router.get(
    "/history",
    summary="最近历史计划",
    description="返回当前用户最近成功生成的旅行计划摘要（需要登录，按用户隔离）",
)
async def get_trip_history(limit: int = 10, user: User = Depends(get_current_user)):
    """查询当前用户的历史计划摘要。"""
    safe_limit = max(1, min(int(limit or 10), 50))

    async with AsyncSessionLocal() as session:
        stmt = (
            select(TripTaskRecord)
            .where(TripTaskRecord.user_id == user.id, TripTaskRecord.status == "completed")
            .order_by(TripTaskRecord.updated_at.desc())
            .limit(safe_limit)
        )
        records = (await session.execute(stmt)).scalars().all()

    items = [item for record in records if (item := _build_history_item(record)) is not None]
    return {
        "items": items,
    }


@router.get(
    "/status/{task_id}",
    summary="查询任务状态",
    description="轮询旅行规划任务的执行状态和结果（需要登录，仅可访问自己的任务）",
)
async def get_task_status(task_id: str, user: User = Depends(get_current_user)):
    """查询任务执行状态。"""
    task = await _get_task(task_id)
    if task is None or task.get("user_id") != user.id:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task["status"] == "completed":
        return {
            "task_id": task_id,
            "plan_id": task.get("plan_id", task_id),
            "status": "completed",
            "result": _serialize_result(task.get("result")),
        }
    if task["status"] == "failed":
        return {
            "task_id": task_id,
            "plan_id": task.get("plan_id", task_id),
            "status": "failed",
            "error": task.get("error", ""),
            "request_payload": task.get("request_payload"),
        }
    return {
        "task_id": task_id,
        "plan_id": task.get("plan_id", task_id),
        "status": "processing",
        "stage": task.get("stage", ""),
        "progress": task.get("progress", 0),
        "progress_text": task.get("message", "处理中..."),
    }


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常",
)
async def health_check():
    """健康检查。"""
    try:
        agent = get_trip_planner_agent()
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.planner_agent.name,
            "tools_count": len(agent.weather_agent.list_tools()) + len(agent.hotel_agent.list_tools()),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")
