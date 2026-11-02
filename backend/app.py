"""FastAPI application for the single-user local prototype."""

from __future__ import annotations

import logging
import re
import sqlite3
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import database
from .agent import AgentClient, AgentError, LowCodeAgent
from .config import ROOT, Settings, load_settings
from .context import build_query

logger = logging.getLogger(__name__)

FRONTEND_DIR = ROOT / "frontend"
APP_NAME = "职业探索助手"
CLIENT_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")
MESSAGE_LIMIT = 4000
PROFILE_LIMIT = 2000
PLAN_FIELD_LIMIT = 8000
PLAN_NOTE_LIMIT = 500
CATEGORIES = (
    "兴趣与偏好",
    "经历与做过的事",
    "专业与年级",
    "技能与能力（自述）",
    "现实约束（时间/地点/预算）",
    "目标与待探索问题",
    "其他",
)
SOURCES = ("self_reported", "assistant_inferred")


class MessageCreate(BaseModel):
    content: str = ""
    client_id: str = ""


class ProfileCreate(BaseModel):
    category: str = ""
    content: str = ""
    source: str = "self_reported"


class ProfilePatch(BaseModel):
    category: str | None = None
    content: str | None = None
    source: str | None = None


class PlanFields(BaseModel):
    directions: str = ""
    gaps: str = ""
    stage_goals: str = ""
    actions: str = ""
    change_note: str = ""


def _now(settings: Settings) -> str:
    return datetime.now(ZoneInfo(settings.timezone)).isoformat(timespec="microseconds")


def _clean(value: str, limit: int, field: str, *, required: bool = False) -> str:
    text = (value or "").strip()
    if required and not text:
        raise HTTPException(status_code=400, detail=f"请填写{field}。")
    if len(text) > limit:
        raise HTTPException(
            status_code=400, detail=f"{field}过长，请控制在 {limit} 字以内。"
        )
    return text


def _conversation_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _message_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "role": row["role"],
        "content": row["content"],
        "status": row["status"],
        "error": row["error"],
        "reply_to": row["reply_to"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _profile_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "category": row["category"],
        "content": row["content"],
        "source": row["source"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "confirmed_at": row["confirmed_at"],
    }


def _plan_version_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "version_no": row["version_no"],
        "status": row["status"],
        "directions": row["directions"],
        "gaps": row["gaps"],
        "stage_goals": row["stage_goals"],
        "actions": row["actions"],
        "change_note": row["change_note"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "confirmed_at": row["confirmed_at"],
    }


def _make_title(content: str) -> str:
    title = " ".join(content.split())
    if len(title) > 20:
        title = title[:20] + "…"
    return title or "新的对话"


def _compact_preview(content: str | None) -> str:
    preview = " ".join((content or "").split())
    return preview[:50] + ("…" if len(preview) > 50 else "")


def _plan_texts(body: PlanFields) -> dict[str, str]:
    return {
        "directions": _clean(body.directions, PLAN_FIELD_LIMIT, "候选方向及依据"),
        "gaps": _clean(body.gaps, PLAN_FIELD_LIMIT, "差距与关键未知"),
        "stage_goals": _clean(body.stage_goals, PLAN_FIELD_LIMIT, "阶段目标"),
        "actions": _clean(body.actions, PLAN_FIELD_LIMIT, "近期学习实践安排"),
    }


def _ensure_plan(conn: sqlite3.Connection, now: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM plans WHERE id = 'main'").fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO plans (id, title, created_at) VALUES ('main', ?, ?)",
            ("我的职业规划", now),
        )
        row = conn.execute("SELECT * FROM plans WHERE id = 'main'").fetchone()
    return row


def create_app(
    settings: Settings | None = None, agent: AgentClient | None = None
) -> FastAPI:
    settings = settings or load_settings()
    database.init_db(settings.db_path)
    agent = agent or LowCodeAgent(
        settings.lowcode_url,
        settings.lowcode_api_key,
        timeout=settings.agent_timeout,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        database.recover_interrupted_replies(settings.db_path)
        yield

    app = FastAPI(
        title=APP_NAME,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.agent = agent
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/api/meta")
    def get_meta() -> dict[str, Any]:
        return {"app_name": APP_NAME, "agent_configured": bool(agent.configured)}

    @app.get("/api/conversations")
    def list_conversations() -> dict[str, Any]:
        with database.get_connection(settings.db_path) as conn:
            rows = conn.execute(
                """
                SELECT c.*,
                       (SELECT COUNT(*) FROM messages m
                         WHERE m.conversation_id = c.id) AS message_count,
                       (SELECT m.content FROM messages m
                         WHERE m.conversation_id = c.id
                         ORDER BY m.created_at DESC, m.rowid DESC LIMIT 1) AS last_content
                  FROM conversations c
                 ORDER BY c.updated_at DESC, c.rowid DESC
                """
            ).fetchall()
        conversations = []
        for row in rows:
            item = _conversation_payload(row)
            item["message_count"] = row["message_count"]
            item["last_preview"] = _compact_preview(row["last_content"])
            conversations.append(item)
        return {"conversations": conversations}

    @app.post("/api/conversations")
    def create_conversation() -> dict[str, Any]:
        now = _now(settings)
        conversation_id = uuid.uuid4().hex
        with database.get_connection(settings.db_path) as conn:
            conn.execute(
                """
                INSERT INTO conversations (id, title, created_at, updated_at)
                VALUES (?, '新的对话', ?, ?)
                """,
                (conversation_id, now, now),
            )
            row = conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
        return {"conversation": _conversation_payload(row)}

    @app.get("/api/conversations/{conversation_id}")
    def get_conversation(conversation_id: str) -> dict[str, Any]:
        with database.get_connection(settings.db_path) as conn:
            conversation = conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
            if conversation is None:
                raise HTTPException(status_code=404, detail="没有找到这个对话。")
            messages = conn.execute(
                """
                SELECT * FROM messages
                 WHERE conversation_id = ?
                 ORDER BY created_at, rowid
                """,
                (conversation_id,),
            ).fetchall()
        return {
            "conversation": _conversation_payload(conversation),
            "messages": [_message_payload(row) for row in messages],
        }

    @app.post("/api/conversations/{conversation_id}/messages")
    def create_message(
        conversation_id: str, body: MessageCreate
    ) -> dict[str, Any]:
        content = _clean(body.content, MESSAGE_LIMIT, "消息", required=True)
        client_id = (body.client_id or "").strip()
        if not CLIENT_ID_RE.fullmatch(client_id):
            raise HTTPException(status_code=400, detail="消息请求标识无效。")
        now = _now(settings)
        with database.get_connection(settings.db_path) as conn:
            conversation = conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
            if conversation is None:
                raise HTTPException(status_code=404, detail="没有找到这个对话。")

            existing = conn.execute(
                "SELECT * FROM messages WHERE client_id = ?", (client_id,)
            ).fetchone()
            if existing is not None:
                if existing["conversation_id"] != conversation_id:
                    raise HTTPException(
                        status_code=409, detail="这条消息已保存在另一个对话中。"
                    )
                return {"message": _message_payload(existing)}

            user_count = conn.execute(
                """
                SELECT COUNT(*) FROM messages
                 WHERE conversation_id = ? AND role = 'user'
                """,
                (conversation_id,),
            ).fetchone()[0]
            message_id = uuid.uuid4().hex
            try:
                conn.execute(
                    """
                    INSERT INTO messages
                        (id, conversation_id, role, content, status, error,
                         client_id, reply_to, created_at, updated_at)
                    VALUES (?, ?, 'user', ?, 'pending', NULL, ?, NULL, ?, ?)
                    """,
                    (message_id, conversation_id, content, client_id, now, now),
                )
            except sqlite3.IntegrityError:
                existing = conn.execute(
                    "SELECT * FROM messages WHERE client_id = ?", (client_id,)
                ).fetchone()
                if existing is not None:
                    if existing["conversation_id"] != conversation_id:
                        raise HTTPException(
                            status_code=409, detail="这条消息已保存在另一个对话中。"
                        )
                    return {"message": _message_payload(existing)}
                raise

            if user_count == 0 and conversation["title"] == "新的对话":
                conn.execute(
                    "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                    (_make_title(content), now, conversation_id),
                )
            else:
                conn.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (now, conversation_id),
                )
            row = conn.execute(
                "SELECT * FROM messages WHERE id = ?", (message_id,)
            ).fetchone()
        return {"message": _message_payload(row)}

    @app.post("/api/messages/{message_id}/respond")
    def respond_to_message(message_id: str) -> dict[str, Any]:
        with database.get_connection(settings.db_path) as conn:
            message = conn.execute(
                "SELECT * FROM messages WHERE id = ?", (message_id,)
            ).fetchone()
            if message is None or message["role"] != "user":
                raise HTTPException(status_code=404, detail="没有找到这条消息。")
            existing = conn.execute(
                "SELECT * FROM messages WHERE reply_to = ? ORDER BY created_at LIMIT 1",
                (message_id,),
            ).fetchone()
            if existing is not None:
                return {
                    "user_message": _message_payload(message),
                    "reply": _message_payload(existing),
                }
            conversation = conn.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (message["conversation_id"],),
            ).fetchone()
            if conversation is None:
                raise HTTPException(status_code=404, detail="没有找到这个对话。")
            now = _now(settings)
            conn.execute(
                """
                UPDATE messages
                   SET status = 'pending', error = NULL, updated_at = ?
                 WHERE id = ?
                """,
                (now, message_id),
            )
            message = conn.execute(
                "SELECT * FROM messages WHERE id = ?", (message_id,)
            ).fetchone()

        try:
            reply = agent.reply(
                session_id=message["conversation_id"],
                message=build_query(settings.db_path, message["content"]),
            )
        except AgentError as exc:
            with database.get_connection(settings.db_path) as conn:
                conn.execute(
                    """
                    UPDATE messages
                       SET status = 'failed', error = ?, updated_at = ?
                     WHERE id = ? AND reply_to IS NULL
                    """,
                    (exc.message, _now(settings), message_id),
                )
                user_message = conn.execute(
                    "SELECT * FROM messages WHERE id = ?", (message_id,)
                ).fetchone()
            status_code = 503 if exc.code == "not_configured" else 502
            raise HTTPException(
                status_code=status_code,
                detail={"message": exc.message, "code": exc.code},
            ) from None
        except Exception as exc:  # defensive boundary: never expose internals
            logger.warning(
                "agent call failed unexpectedly: %s", type(exc).__name__
            )
            friendly = "调用助手时出现异常，请稍后重试；你的消息已保存。"
            with database.get_connection(settings.db_path) as conn:
                conn.execute(
                    """
                    UPDATE messages
                       SET status = 'failed', error = ?, updated_at = ?
                     WHERE id = ? AND reply_to IS NULL
                    """,
                    (friendly, _now(settings), message_id),
                )
            raise HTTPException(
                status_code=502,
                detail={"message": friendly, "code": "agent_error"},
            ) from None

        now = _now(settings)
        with database.get_connection(settings.db_path) as conn:
            existing = conn.execute(
                "SELECT * FROM messages WHERE reply_to = ? ORDER BY created_at LIMIT 1",
                (message_id,),
            ).fetchone()
            if existing is not None:
                user_message = conn.execute(
                    "SELECT * FROM messages WHERE id = ?", (message_id,)
                ).fetchone()
                return {
                    "user_message": _message_payload(user_message),
                    "reply": _message_payload(existing),
                }
            reply_id = uuid.uuid4().hex
            try:
                conn.execute(
                    """
                    INSERT INTO messages
                        (id, conversation_id, role, content, status, error,
                         client_id, reply_to, created_at, updated_at)
                    VALUES (?, ?, 'assistant', ?, 'complete', NULL, NULL, ?, ?, ?)
                    """,
                    (
                        reply_id,
                        message["conversation_id"],
                        reply.text,
                        message_id,
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError:
                # Two requests may race after both called the agent. The unique
                # reply_to index keeps one assistant reply; return that one.
                existing = conn.execute(
                    "SELECT * FROM messages WHERE reply_to = ? ORDER BY created_at LIMIT 1",
                    (message_id,),
                ).fetchone()
                if existing is None:
                    raise
                conn.execute(
                    """
                    UPDATE messages
                       SET status = 'complete', error = NULL, updated_at = ?
                     WHERE id = ?
                    """,
                    (now, message_id),
                )
                user_message = conn.execute(
                    "SELECT * FROM messages WHERE id = ?", (message_id,)
                ).fetchone()
                return {
                    "user_message": _message_payload(user_message),
                    "reply": _message_payload(existing),
                }
            conn.execute(
                """
                UPDATE messages
                   SET status = 'complete', error = NULL, updated_at = ?
                 WHERE id = ?
                """,
                (now, message_id),
            )
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, message["conversation_id"]),
            )
            reply_row = conn.execute(
                "SELECT * FROM messages WHERE id = ?", (reply_id,)
            ).fetchone()
            user_message = conn.execute(
                "SELECT * FROM messages WHERE id = ?", (message_id,)
            ).fetchone()
        return {
            "user_message": _message_payload(user_message),
            "reply": _message_payload(reply_row),
        }

    @app.get("/api/profile")
    def list_profile() -> dict[str, Any]:
        with database.get_connection(settings.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM profile_items
                 ORDER BY CASE status WHEN 'unconfirmed' THEN 0 ELSE 1 END,
                          updated_at DESC, rowid DESC
                """
            ).fetchall()
        return {"items": [_profile_payload(row) for row in rows]}

    @app.post("/api/profile")
    def create_profile_item(body: ProfileCreate) -> dict[str, Any]:
        category = (body.category or "").strip()
        if category not in CATEGORIES:
            raise HTTPException(status_code=400, detail="请选择有效的线索类别。")
        content = _clean(body.content, PROFILE_LIMIT, "线索内容", required=True)
        source = (body.source or "").strip()
        if source not in SOURCES:
            raise HTTPException(status_code=400, detail="请选择有效的线索来源。")
        now = _now(settings)
        item_id = uuid.uuid4().hex
        with database.get_connection(settings.db_path) as conn:
            conn.execute(
                """
                INSERT INTO profile_items
                    (id, category, content, source, status,
                     created_at, updated_at, confirmed_at)
                VALUES (?, ?, ?, ?, 'unconfirmed', ?, ?, NULL)
                """,
                (item_id, category, content, source, now, now),
            )
            row = conn.execute(
                "SELECT * FROM profile_items WHERE id = ?", (item_id,)
            ).fetchone()
        return {"item": _profile_payload(row)}

    @app.patch("/api/profile/{item_id}")
    def update_profile_item(item_id: str, body: ProfilePatch) -> dict[str, Any]:
        with database.get_connection(settings.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM profile_items WHERE id = ?", (item_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="没有找到这条线索。")
            category = row["category"]
            content = row["content"]
            source = row["source"]
            if body.category is not None:
                category = body.category.strip()
                if category not in CATEGORIES:
                    raise HTTPException(status_code=400, detail="请选择有效的线索类别。")
            if body.content is not None:
                content = _clean(body.content, PROFILE_LIMIT, "线索内容", required=True)
            if body.source is not None:
                source = body.source.strip()
                if source not in SOURCES:
                    raise HTTPException(status_code=400, detail="请选择有效的线索来源。")
            now = _now(settings)
            conn.execute(
                """
                UPDATE profile_items
                   SET category = ?, content = ?, source = ?,
                       status = 'unconfirmed', confirmed_at = NULL, updated_at = ?
                 WHERE id = ?
                """,
                (category, content, source, now, item_id),
            )
            row = conn.execute(
                "SELECT * FROM profile_items WHERE id = ?", (item_id,)
            ).fetchone()
        return {"item": _profile_payload(row)}

    @app.post("/api/profile/{item_id}/confirm")
    def confirm_profile_item(item_id: str) -> dict[str, Any]:
        now = _now(settings)
        with database.get_connection(settings.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM profile_items WHERE id = ?", (item_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="没有找到这条线索。")
            conn.execute(
                """
                UPDATE profile_items
                   SET status = 'confirmed', confirmed_at = ?, updated_at = ?
                 WHERE id = ?
                """,
                (now, now, item_id),
            )
            row = conn.execute(
                "SELECT * FROM profile_items WHERE id = ?", (item_id,)
            ).fetchone()
        return {"item": _profile_payload(row)}

    @app.delete("/api/profile/{item_id}")
    def delete_profile_item(item_id: str) -> dict[str, Any]:
        with database.get_connection(settings.db_path) as conn:
            row = conn.execute(
                "SELECT id FROM profile_items WHERE id = ?", (item_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="没有找到这条线索。")
            conn.execute("DELETE FROM profile_items WHERE id = ?", (item_id,))
        return {"deleted": True}

    @app.get("/api/plan")
    def get_plan() -> dict[str, Any]:
        now = _now(settings)
        with database.get_connection(settings.db_path) as conn:
            plan = _ensure_plan(conn, now)
            rows = conn.execute(
                """
                SELECT * FROM plan_versions
                 WHERE plan_id = 'main'
                 ORDER BY version_no DESC
                """
            ).fetchall()
        versions = [_plan_version_payload(row) for row in rows]
        draft = next((item for item in versions if item["status"] == "draft"), None)
        confirmed = next(
            (item for item in versions if item["status"] == "confirmed"), None
        )
        return {
            "plan": {
                "id": plan["id"],
                "title": plan["title"],
                "created_at": plan["created_at"],
            },
            "versions": versions,
            "draft": draft,
            "confirmed": confirmed,
        }

    @app.post("/api/plan/versions")
    def create_plan_version(body: PlanFields) -> dict[str, Any]:
        texts = _plan_texts(body)
        if not any(texts.values()):
            raise HTTPException(
                status_code=400, detail="至少填写一项规划内容再保存。"
            )
        note = _clean(body.change_note, PLAN_NOTE_LIMIT, "修改说明")
        now = _now(settings)
        with database.get_connection(settings.db_path) as conn:
            _ensure_plan(conn, now)
            next_no = conn.execute(
                "SELECT COALESCE(MAX(version_no), 0) + 1 FROM plan_versions WHERE plan_id = 'main'"
            ).fetchone()[0]
            version_id = uuid.uuid4().hex
            try:
                conn.execute(
                    """
                    INSERT INTO plan_versions
                        (id, plan_id, version_no, status, directions, gaps,
                         stage_goals, actions, change_note, created_at,
                         updated_at, confirmed_at)
                    VALUES (?, 'main', ?, 'draft', ?, ?, ?, ?, ?, ?, ?, NULL)
                    """,
                    (
                        version_id,
                        next_no,
                        texts["directions"],
                        texts["gaps"],
                        texts["stage_goals"],
                        texts["actions"],
                        note,
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError:
                raise HTTPException(
                    status_code=409, detail="规划版本冲突，请刷新后重试。"
                ) from None
            row = conn.execute(
                "SELECT * FROM plan_versions WHERE id = ?", (version_id,)
            ).fetchone()
        return {"version": _plan_version_payload(row)}

    @app.put("/api/plan/versions/{version_id}")
    def update_plan_version(version_id: str, body: PlanFields) -> dict[str, Any]:
        texts = _plan_texts(body)
        if not any(texts.values()):
            raise HTTPException(
                status_code=400, detail="至少填写一项规划内容再保存。"
            )
        note = _clean(body.change_note, PLAN_NOTE_LIMIT, "修改说明")
        now = _now(settings)
        with database.get_connection(settings.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM plan_versions WHERE id = ?", (version_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="没有找到这个规划版本。")
            if row["status"] != "draft":
                raise HTTPException(
                    status_code=409,
                    detail="只有草稿可以修改；已确认的版本会保留为历史。",
                )
            conn.execute(
                """
                UPDATE plan_versions
                   SET directions = ?, gaps = ?, stage_goals = ?, actions = ?,
                       change_note = ?, updated_at = ?
                 WHERE id = ?
                """,
                (
                    texts["directions"],
                    texts["gaps"],
                    texts["stage_goals"],
                    texts["actions"],
                    note,
                    now,
                    version_id,
                ),
            )
            row = conn.execute(
                "SELECT * FROM plan_versions WHERE id = ?", (version_id,)
            ).fetchone()
        return {"version": _plan_version_payload(row)}

    @app.post("/api/plan/versions/{version_id}/confirm")
    def confirm_plan_version(version_id: str) -> dict[str, Any]:
        now = _now(settings)
        with database.get_connection(settings.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM plan_versions WHERE id = ?", (version_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="没有找到这个规划版本。")
            if row["status"] != "draft":
                raise HTTPException(
                    status_code=409, detail="只有草稿可以确认。"
                )
            conn.execute(
                """
                UPDATE plan_versions
                   SET status = 'superseded', updated_at = ?
                 WHERE plan_id = ? AND status = 'confirmed'
                """,
                (now, row["plan_id"]),
            )
            conn.execute(
                """
                UPDATE plan_versions
                   SET status = 'confirmed', confirmed_at = ?, updated_at = ?
                 WHERE id = ?
                """,
                (now, now, version_id),
            )
            row = conn.execute(
                "SELECT * FROM plan_versions WHERE id = ?", (version_id,)
            ).fetchone()
        return {"version": _plan_version_payload(row)}

    return app
