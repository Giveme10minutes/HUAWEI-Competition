"""Offline tests for the local prototype backend.

These tests use a fake agent; they do not call AgentArts.
"""

from __future__ import annotations

import tempfile
import json
import sqlite3
from contextlib import closing
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.agent import AgentError, AgentReply, _reply_events
from backend.app import create_app
from backend.config import Settings


class FakeAgent:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.failures = 0

    @property
    def configured(self) -> bool:
        return True

    def reply(self, session_id: str, message: str) -> AgentReply:
        self.calls.append((session_id, message))
        if self.failures:
            self.failures -= 1
            raise AgentError("模拟调用失败，请重试。", "test_failure")
        return AgentReply(text="这是助手的最终回答。")


class WebAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.settings = Settings(
            db_path=Path(self.tempdir.name) / "test.sqlite3",
            lowcode_url="",
            lowcode_api_key="",
            agent_timeout=10,
        )
        self.agent = FakeAgent()
        self.client = self.enterContext(
            TestClient(create_app(settings=self.settings, agent=self.agent))
        )

    def make_conversation(self) -> dict:
        response = self.client.post("/api/conversations")
        self.assertEqual(response.status_code, 200)
        return response.json()["conversation"]

    def send_message(
        self, conversation_id: str, content: str = "我很迷茫，不知道以后想做什么。",
        client_id: str = "client-0001",
    ) -> dict:
        response = self.client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"content": content, "client_id": client_id},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["message"]

    def test_meta_and_conversation_reply_flow(self) -> None:
        meta = self.client.get("/api/meta").json()
        self.assertTrue(meta["agent_configured"])
        self.assertNotIn("lowcode", str(meta).lower())
        self.assertNotIn("key", str(meta).lower())

        conversation = self.make_conversation()
        user = self.send_message(conversation["id"])
        self.assertEqual(user["role"], "user")
        self.assertEqual(user["status"], "pending")

        listed = self.client.get("/api/conversations").json()["conversations"]
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["title"], "我很迷茫，不知道以后想做什么。")
        self.assertEqual(listed[0]["message_count"], 1)

        duplicate = self.send_message(conversation["id"])
        self.assertEqual(duplicate["id"], user["id"])

        response = self.client.post(f"/api/messages/{user['id']}/respond")
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["reply"]["role"], "assistant")
        self.assertEqual(payload["reply"]["content"], "这是助手的最终回答。")
        self.assertEqual(payload["user_message"]["status"], "complete")
        self.assertEqual(len(self.agent.calls), 1)
        self.assertEqual(self.agent.calls[0][0], conversation["id"])

        again = self.client.post(f"/api/messages/{user['id']}/respond")
        self.assertEqual(again.status_code, 200)
        self.assertEqual(again.json()["reply"]["id"], payload["reply"]["id"])
        self.assertEqual(len(self.agent.calls), 1)

        detail = self.client.get(
            f"/api/conversations/{conversation['id']}"
        ).json()
        self.assertEqual(
            [message["role"] for message in detail["messages"]],
            ["user", "assistant"],
        )

        second = self.make_conversation()
        listed = self.client.get("/api/conversations").json()["conversations"]
        self.assertEqual(
            {item["id"] for item in listed}, {conversation["id"], second["id"]}
        )
        self.assertEqual(len(self.agent.calls), 1)

    def test_transport_yields_answer_before_end_and_summary_replaces_deltas(self) -> None:
        source_finished = []
        def upstream():
            yield {"event": "reasoning_content", "content": "不展示的思考"}
            yield {"event": "message", "content": "第一段"}
            yield {"event": "message", "content": "第二段"}
            yield {"event": "summary_response", "content": "最终校准回答"}
            source_finished.append(True)
            yield {"event": "done"}
        stream = _reply_events(upstream())
        self.assertEqual(next(stream), {"type": "delta", "text": "第一段"})
        self.assertFalse(source_finished)
        rest = list(stream)
        self.assertEqual(rest[-1]["reply"].text, "最终校准回答")
        self.assertNotIn("不展示的思考", str(rest))
        split_secret = list(_reply_events(iter([
            {"event": "message", "content": "内容secret-"},
            {"event": "message", "content": "key结尾"},
            {"event": "done"},
        ]), "secret-key"))
        self.assertNotIn("secret-", "".join(e.get("text", "") for e in split_secret))

    def test_stream_saves_only_complete_reply_and_replay_avoids_second_call(self) -> None:
        def stream(session_id, message):
            self.agent.calls.append((session_id, message))
            yield {"type": "delta", "text": "片段"}
            yield {"type": "complete", "reply": AgentReply(text="完整回答")}
        self.agent.stream = stream
        conversation = self.make_conversation()
        user = self.send_message(conversation["id"])
        path = f"/api/messages/{user['id']}/stream"
        response = self.client.post(path)
        events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
        self.assertEqual([e["type"] for e in events], ["start", "delta", "complete"])
        self.assertEqual(events[-1]["data"]["reply"]["content"], "完整回答")
        self.client.post(path)
        self.assertEqual(len(self.agent.calls), 1)
        self.assertEqual(len(self.client.get(f"/api/conversations/{conversation['id']}").json()["messages"]), 2)

    def test_stream_failure_does_not_save_partial_as_a_complete_reply(self) -> None:
        def stream(session_id, message):
            yield {"type": "delta", "text": "尚未完成的内容"}
            raise AgentError("模拟流中断", "interrupted")
        self.agent.stream = stream
        conversation = self.make_conversation()
        user = self.send_message(conversation["id"])
        response = self.client.post(f"/api/messages/{user['id']}/stream")
        self.assertIn('"type": "error"', response.text)
        messages = self.client.get(f"/api/conversations/{conversation['id']}").json()["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["status"], "failed")

    def test_failure_keeps_message_and_retry_does_not_duplicate(self) -> None:
        conversation = self.make_conversation()
        user = self.send_message(conversation["id"])
        self.agent.failures = 1

        failed = self.client.post(f"/api/messages/{user['id']}/respond")
        self.assertEqual(failed.status_code, 502)
        detail = self.client.get(
            f"/api/conversations/{conversation['id']}"
        ).json()
        self.assertEqual(len(detail["messages"]), 1)
        self.assertEqual(detail["messages"][0]["id"], user["id"])
        self.assertEqual(detail["messages"][0]["status"], "failed")
        self.assertIn("模拟调用失败", detail["messages"][0]["error"])

        retried = self.client.post(f"/api/messages/{user['id']}/respond")
        self.assertEqual(retried.status_code, 200)
        detail = self.client.get(
            f"/api/conversations/{conversation['id']}"
        ).json()
        self.assertEqual(len(detail["messages"]), 2)
        users = [item for item in detail["messages"] if item["role"] == "user"]
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["status"], "complete")
        self.assertEqual(len(self.agent.calls), 2)

    def test_records_survive_app_recreation_and_pending_is_recovered(self) -> None:
        conversation = self.make_conversation()
        user = self.send_message(conversation["id"])
        self.assertEqual(
            self.client.post(f"/api/messages/{user['id']}/respond").status_code,
            200,
        )

        with TestClient(
            create_app(settings=self.settings, agent=FakeAgent())
        ) as second:
            detail = second.get(
                f"/api/conversations/{conversation['id']}"
            ).json()
            self.assertEqual(len(detail["messages"]), 2)
            self.assertEqual(
                detail["messages"][1]["content"], "这是助手的最终回答。"
            )
            listed = second.get("/api/conversations").json()["conversations"]
            self.assertEqual(listed[0]["id"], conversation["id"])

        pendingConversation = self.make_conversation()
        pending = self.send_message(
            pendingConversation["id"], content="这条还没有回复。", client_id="client-0002"
        )
        self.assertEqual(pending["status"], "pending")

        with TestClient(
            create_app(settings=self.settings, agent=FakeAgent())
        ) as third:
            recovered = third.get(
                f"/api/conversations/{pendingConversation['id']}"
            ).json()["messages"][0]
            self.assertEqual(recovered["id"], pending["id"])
            self.assertEqual(recovered["status"], "failed")
            self.assertIn("上一次回复未完成", recovered["error"])

    def test_profile_add_correct_confirm_delete(self) -> None:
        created = self.client.post(
            "/api/profile",
            json={
                "category": "兴趣与偏好",
                "content": "我喜欢把复杂的事讲清楚。",
                "source": "self_reported",
            },
        )
        self.assertEqual(created.status_code, 200, created.text)
        item = created.json()["item"]
        self.assertEqual(item["status"], "unconfirmed")
        self.assertIsNone(item["confirmed_at"])

        confirmed = self.client.post(f"/api/profile/{item['id']}/confirm").json()[
            "item"
        ]
        self.assertEqual(confirmed["status"], "confirmed")
        self.assertIsNotNone(confirmed["confirmed_at"])

        edited = self.client.patch(
            f"/api/profile/{item['id']}",
            json={"content": "我喜欢把复杂的事情讲清楚，也愿意写下来。"},
        ).json()["item"]
        self.assertEqual(edited["status"], "unconfirmed")
        self.assertIsNone(edited["confirmed_at"])

        deleted = self.client.delete(f"/api/profile/{item['id']}")
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(self.client.get("/api/profile").json()["items"], [])

    def test_pin_delete_restore_conversations_preserves_messages_and_other_records(self) -> None:
        first = self.make_conversation()
        user = self.send_message(first["id"])
        self.assertEqual(self.client.delete(f"/api/conversations/{first['id']}").status_code, 409)
        self.client.post(f"/api/messages/{user['id']}/respond")
        second = self.make_conversation()
        line = self.client.post("/api/profile", json={"category": "其他", "content": "保留的线索"}).json()["item"]
        plan = self.client.post("/api/plan/versions", json={"actions": "保留的草稿"}).json()["version"]
        path = f"/api/conversations/{first['id']}"
        self.assertEqual(self.client.patch(path, json={"pinned": True}).status_code, 200)
        listed = self.client.get("/api/conversations").json()["conversations"]
        self.assertEqual(listed[0]["id"], first["id"])
        self.assertTrue(listed[0]["pinned"])
        self.assertEqual(self.client.delete(path).status_code, 200)
        self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(self.client.post(f"/api/messages/{user['id']}/respond").status_code, 404)
        self.assertEqual(self.client.post(path + "/messages", json={"content": "不能续写", "client_id": "deleted-send"}).status_code, 404)
        self.assertEqual([c["id"] for c in self.client.get("/api/conversations").json()["conversations"]], [second["id"]])
        self.assertEqual(self.client.get("/api/conversations?deleted=true").json()["conversations"][0]["id"], first["id"])
        with TestClient(create_app(settings=self.settings, agent=FakeAgent())) as reopened:
            self.assertEqual(len(reopened.get("/api/conversations?deleted=true").json()["conversations"]), 1)
            self.assertEqual(reopened.post(path + "/restore").status_code, 200)
            restored = reopened.get(path).json()
            self.assertTrue(restored["conversation"]["pinned"])
            self.assertEqual(len(restored["messages"]), 2)
            self.assertEqual(reopened.patch(path, json={"pinned": False}).status_code, 200)
            self.assertFalse(reopened.get(path).json()["conversation"]["pinned"])
            self.assertEqual(reopened.get("/api/profile").json()["items"][0]["id"], line["id"])
            self.assertEqual(reopened.get("/api/plan").json()["draft"]["id"], plan["id"])

    def test_existing_database_gets_conversation_management_columns(self) -> None:
        from backend.database import init_db
        path = Path(self.tempdir.name) / "old.sqlite3"
        with closing(sqlite3.connect(path)) as conn:
            with conn:
                conn.execute("CREATE TABLE conversations (id TEXT PRIMARY KEY, title TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
                conn.execute("INSERT INTO conversations VALUES ('old', '原有对话', '2026-11-02', '2026-11-02')")
        init_db(path)
        init_db(path)
        with closing(sqlite3.connect(path)) as conn:
            row = conn.execute("SELECT title, pinned, deleted_at FROM conversations WHERE id = 'old'").fetchone()
        self.assertEqual(row, ("原有对话", 0, None))

    def test_agent_uses_current_confirmed_records_without_changing_chat_text(self) -> None:
        conversation = self.make_conversation()
        item = self.client.post("/api/profile", json={
            "category": "现实约束（时间/地点/预算）",
            "content": "每周可以用两小时探索", "source": "self_reported",
        }).json()["item"]
        self.client.post("/api/profile", json={
            "category": "兴趣与偏好", "content": "待核实兴趣不要发送",
            "source": "assistant_inferred",
        })
        self.client.post(f"/api/profile/{item['id']}/confirm")
        first = self.client.post("/api/plan/versions", json={
            "stage_goals": "先了解两种工作活动", "actions": "找一份职业访谈",
        }).json()["version"]
        self.client.post(f"/api/plan/versions/{first['id']}/confirm")
        second = self.client.post("/api/plan/versions", json={
            "stage_goals": "新规划尚未确认",
        }).json()["version"]

        user = self.send_message(conversation["id"], "接着我的规划聊聊。")
        self.assertEqual(self.client.post(f"/api/messages/{user['id']}/respond").status_code, 200)
        payload = json.loads(self.agent.calls[-1][1].split("\n", 1)[1])
        self.assertEqual(payload["user_message"], "接着我的规划聊聊。")
        records = payload["current_records"]
        self.assertEqual(len(records["confirmed_profile"]), 1)
        self.assertEqual(records["confirmed_profile"][0]["source"], "self_reported")
        self.assertEqual(records["confirmed_plan"]["version_no"], 1)
        self.assertNotIn("待核实兴趣", self.agent.calls[-1][1])
        self.assertNotIn("新规划尚未确认", self.agent.calls[-1][1])
        detail = self.client.get(f"/api/conversations/{conversation['id']}").json()
        self.assertEqual(detail["messages"][0]["content"], "接着我的规划聊聊。")

        # Correcting an item makes it unconfirmed; confirming a new plan replaces v1.
        self.client.patch(f"/api/profile/{item['id']}", json={"content": "时间暂不确定"})
        self.client.post(f"/api/plan/versions/{second['id']}/confirm")
        next_user = self.send_message(conversation["id"], "看一下新版。", "context-second")
        self.assertEqual(self.client.post(f"/api/messages/{next_user['id']}/respond").status_code, 200)
        updated = json.loads(self.agent.calls[-1][1].split("\n", 1)[1])["current_records"]
        self.assertEqual(updated["confirmed_profile"], [])
        self.assertEqual(updated["confirmed_plan"]["version_no"], 2)
        self.assertNotIn("每周可以用两小时", self.agent.calls[-1][1])
        self.assertNotIn("找一份职业访谈", self.agent.calls[-1][1])

    def test_plan_history_and_confirmed_versions(self) -> None:
        empty = self.client.get("/api/plan").json()
        self.assertIsNone(empty["confirmed"])
        self.assertIsNone(empty["draft"])

        first = self.client.post(
            "/api/plan/versions",
            json={
                "directions": "方向 A：先通过课程和小项目验证兴趣。",
                "gaps": "",
                "stage_goals": "",
                "actions": "",
                "change_note": "只写了方向",
            },
        )
        self.assertEqual(first.status_code, 200, first.text)
        version = first.json()["version"]
        self.assertEqual(version["version_no"], 1)
        self.assertEqual(version["status"], "draft")

        updated = self.client.put(
            f"/api/plan/versions/{version['id']}",
            json={
                "directions": "方向 A：先通过课程和小项目验证兴趣。",
                "gaps": "还不确定是否愿意长期投入。",
                "stage_goals": "",
                "actions": "两周内完成一次小项目。",
                "change_note": "补充差距和近期安排",
            },
        )
        self.assertEqual(updated.status_code, 200)

        confirmed = self.client.post(
            f"/api/plan/versions/{version['id']}/confirm"
        )
        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(confirmed.json()["version"]["status"], "confirmed")

        locked = self.client.put(
            f"/api/plan/versions/{version['id']}",
            json={"directions": "试图修改已确认版本"},
        )
        self.assertEqual(locked.status_code, 409)

        second = self.client.post(
            "/api/plan/versions",
            json={"actions": "再找一位学长聊聊实际工作内容。"},
        ).json()["version"]
        self.assertEqual(second["version_no"], 2)
        self.client.post(f"/api/plan/versions/{second['id']}/confirm")

        plan = self.client.get("/api/plan").json()
        self.assertEqual(plan["confirmed"]["id"], second["id"])
        self.assertEqual(plan["versions"][1]["id"], version["id"])
        self.assertEqual(plan["versions"][1]["status"], "superseded")
        self.assertIsNone(plan["draft"])

        empty_version = self.client.post("/api/plan/versions", json={})
        self.assertEqual(empty_version.status_code, 400)

    def test_unconfigured_agent_is_reported_without_fake_reply(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(
                db_path=Path(directory) / "offline.sqlite3",
                lowcode_url="",
                lowcode_api_key="",
                agent_timeout=10,
            )
            with TestClient(create_app(settings=settings)) as client:
                conversation = client.post("/api/conversations").json()[
                    "conversation"
                ]
                user = client.post(
                    f"/api/conversations/{conversation['id']}/messages",
                    json={"content": "我很迷茫。", "client_id": "offline-client"},
                ).json()["message"]
                response = client.post(f"/api/messages/{user['id']}/respond")
                self.assertEqual(response.status_code, 503)
                detail = client.get(
                    f"/api/conversations/{conversation['id']}"
                ).json()
                self.assertEqual(len(detail["messages"]), 1)
                self.assertEqual(detail["messages"][0]["status"], "failed")
                self.assertIn("尚未连接", detail["messages"][0]["error"])


if __name__ == "__main__":
    unittest.main()
