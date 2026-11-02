"""Offline tests for the local prototype backend.

These tests use a fake agent; they do not call AgentArts.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.agent import AgentError, AgentReply
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
