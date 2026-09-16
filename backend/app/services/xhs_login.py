"""小红书扫码登录服务 - 基于 Playwright 自动获取 Cookie

后端用 headless 浏览器打开小红书登录页，截图二维码返回给前端展示，
用户用小红书 App 扫码确认后，自动提取登录态 Cookie 并写入运行时配置
（runtime_settings.json），彻底告别手动从浏览器 DevTools 复制 Cookie。

扫码成功写入的是登录态 Cookie，寿命远长于游客 Cookie，
且失效后只需再次扫码即可秒级更新。
"""

import base64
import logging
import threading
import time
from typing import Any, Dict

from ..config import update_runtime_settings

logger = logging.getLogger(__name__)

# 登录二维码有效期（秒），超时后前端可重新发起
_LOGIN_POLL_TIMEOUT = 180
_LOGIN_POLL_INTERVAL = 2
# 等待旧会话线程退出的最长时间（秒）
_THREAD_JOIN_TIMEOUT = 25

_STATE_LOCK = threading.Lock()
_STATE: Dict[str, Any] = {
    "status": "idle",  # idle | pending | success | failed | timeout
    "message": "",
    "qrcode_base64": "",
}
_SESSION: Dict[str, Any] = {
    "cancel": False,
    "thread": None,
}

# 登录二维码元素选择器（按优先级依次尝试，兼容小红书改版）
_QR_SELECTORS = [
    "div.login-container",
    ".qrcode",
    "img.qrcode-img",
]

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _set_state(status: str, message: str) -> None:
    with _STATE_LOCK:
        _STATE["status"] = status
        _STATE["message"] = message


def _set_qrcode(qrcode_base64: str) -> None:
    with _STATE_LOCK:
        _STATE["qrcode_base64"] = qrcode_base64


def get_xhs_login_status() -> Dict[str, Any]:
    """获取当前扫码登录会话状态（含二维码 base64）。"""
    with _STATE_LOCK:
        return {
            "status": _STATE["status"],
            "message": _STATE["message"],
            "qrcode_base64": _STATE["qrcode_base64"],
        }


def cancel_xhs_login() -> None:
    """请求取消当前进行中的扫码登录会话。"""
    with _STATE_LOCK:
        if _STATE["status"] == "pending":
            _SESSION["cancel"] = True


def start_xhs_login() -> Dict[str, Any]:
    """启动（或重启）扫码登录会话，立即返回，二维码通过 status 接口轮询获取。"""
    # 先取消并等待旧会话退出，避免多个浏览器实例并发写状态
    cancel_xhs_login()
    old_thread = _SESSION.get("thread")
    if old_thread and old_thread.is_alive():
        old_thread.join(timeout=_THREAD_JOIN_TIMEOUT)
        if old_thread.is_alive():
            logger.warning("旧的扫码登录线程仍未退出，可能出现状态串扰")

    with _STATE_LOCK:
        _STATE.update(status="pending", message="", qrcode_base64="")
        _SESSION["cancel"] = False

    thread = threading.Thread(target=_run_login_session, daemon=True)
    with _STATE_LOCK:
        _SESSION["thread"] = thread
    thread.start()

    return {"status": "pending"}


def _run_login_session() -> None:
    """在独立线程中运行 Playwright：截取二维码 -> 轮询扫码结果 -> 保存 Cookie。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        _set_state(
            "failed",
            "服务器未安装 Playwright（pip install playwright && playwright install chromium），"
            "请手动粘贴 Cookie",
        )
        return

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ],
            )
            try:
                context = browser.new_context(
                    user_agent=_USER_AGENT,
                    viewport={"width": 1280, "height": 800},
                )
                # 隐藏 webdriver 特征，降低风控概率
                context.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
                )
                page = context.new_page()
                page.goto(
                    "https://www.xiaohongshu.com",
                    wait_until="domcontentloaded",
                    timeout=30000,
                )

                # 截图登录二维码
                qrcode_base64 = ""
                for selector in _QR_SELECTORS:
                    try:
                        locator = page.locator(selector).first
                        locator.wait_for(state="visible", timeout=5000)
                        png = locator.screenshot()
                        qrcode_base64 = base64.b64encode(png).decode("utf-8")
                        break
                    except Exception:
                        continue

                if not qrcode_base64:
                    _set_state(
                        "failed",
                        "未能获取小红书登录二维码（页面结构可能已变更），请手动粘贴 Cookie",
                    )
                    return
                _set_qrcode(qrcode_base64)

                # 轮询等待用户扫码，登录成功后会出现非空 web_session Cookie
                deadline = time.time() + _LOGIN_POLL_TIMEOUT
                while time.time() < deadline:
                    if _SESSION.get("cancel"):
                        _set_state("idle", "已取消扫码登录")
                        return

                    cookies = [
                        c
                        for c in context.cookies()
                        if "xiaohongshu.com" in (c.get("domain") or "")
                    ]
                    if any(
                        c.get("name") == "web_session" and c.get("value")
                        for c in cookies
                    ):
                        cookie_str = "; ".join(
                            f'{c["name"]}={c["value"]}' for c in cookies
                        )
                        update_runtime_settings({"xhs_cookie": cookie_str})
                        _set_state("success", "扫码登录成功，小红书 Cookie 已自动更新")
                        return

                    time.sleep(_LOGIN_POLL_INTERVAL)

                _set_state("timeout", "二维码已过期，请刷新后重新扫码")
            finally:
                try:
                    browser.close()
                except Exception:
                    pass
    except Exception as e:
        logger.exception("小红书扫码登录会话异常")
        _set_state("failed", f"扫码登录会话异常: {e}")
