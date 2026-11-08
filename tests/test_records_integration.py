"""Record integration checks with isolated SQLite; no cloud calls."""
import json
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app import create_app
from backend.config import Settings
from backend.agent import AgentReply, _reply_events, _ProtocolError


class RecordIntegrationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name)/'app.sqlite3'
        self.calls = []
        class Agent:
            configured = True
            result = '回答'
            def reply(agent, session_id, message):
                self.calls.append((session_id, message))
                return AgentReply(text=agent.result)
        self.agent = Agent()
        self.settings = Settings(db_path=self.path, lowcode_url='', lowcode_api_key='')
        self.client = self.enterContext(TestClient(create_app(self.settings, self.agent)))

    def answer(self):
        c = self.client.post('/api/conversations').json()['conversation']
        u = self.client.post(f"/api/conversations/{c['id']}/messages", json={'content':'我是大一学生，每周2小时。','client_id':'record-test'}).json()['message']
        return self.client.post(f"/api/messages/{u['id']}/respond").json()['reply']

    def test_extract_is_preview_and_requires_user_quote(self):
        reply = self.answer()
        self.agent.result = json.dumps({'items':[{'category':'专业与年级','content':'大一学生','source':'self_reported','quote':'我是大一学生'}]}, ensure_ascii=False)
        result = self.client.post(f"/api/messages/{reply['id']}/extract", json={'kind':'profile'})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(self.client.get('/api/profile').json()['items'], [])
        self.assertNotEqual(self.calls[-1][0], reply.get('conversation_id'))
        self.agent.result = self.agent.result.replace('我是大一学生','我有三年经验')
        self.assertEqual(self.client.post(f"/api/messages/{reply['id']}/extract", json={'kind':'profile'}).status_code, 502)
        self.assertEqual(self.client.get('/api/profile').json()['items'], [])

    def test_plan_task_budget_confirmation_and_history(self):
        task = dict(title='整理名单',goal='体验信息整理',instructions='用虚构数据去重', minutes=30,evidence='去重结果',acceptance='无重复且原数据保留')
        body = dict(stage_goals='体验信息整理',actions='整理名单',task_items=[task],available_minutes=30)
        self.assertEqual(self.client.post('/api/plan/versions', json=body).status_code, 400)
        self.assertEqual(self.client.get('/api/plan').json()['versions'], [])
        body['available_minutes']=60
        r = self.client.post('/api/plan/versions',json=body)
        self.assertEqual(r.status_code,200,r.text)
        version=r.json()['version']
        self.assertIsNone(self.client.get('/api/plan').json()['confirmed'])
        self.client.post(f"/api/plan/versions/{version['id']}/confirm")
        from backend.context import build_query
        self.assertIn('去重结果',build_query(self.path,'开始学习'))
        body['task_items'][0]['minutes']=20
        new=self.client.post('/api/plan/versions',json=body).json()['version']
        self.client.post(f"/api/plan/versions/{new['id']}/confirm")
        plans=self.client.get('/api/plan').json()
        self.assertEqual(plans['confirmed']['task_items'][0]['minutes'],20)
        self.assertEqual(next(p for p in plans['versions'] if p['id']==version['id'])['task_items'][0]['minutes'],30)
        # Initialize again: additive migration preserves confirmed records.
        with TestClient(create_app(self.settings,self.agent)) as restarted:
            self.assertEqual(restarted.get('/api/plan').json()['confirmed']['id'],new['id'])

    def test_extraction_failure_preserves_chat(self):
        reply=self.answer(); self.agent.result='不是JSON'
        r=self.client.post(f"/api/messages/{reply['id']}/extract",json={'kind':'plan'})
        self.assertEqual(r.status_code,502)
        self.assertEqual(self.client.get('/api/plan').json()['versions'],[])

    def test_workflow_events_only_forward_end_and_final_output(self):
        events=[{'event':'message','data':{'node_type':'LLM','text':'内部草稿','reasoning_content':'不可展示'}},
                {'event':'message','data':{'node_type':'End','text':'最终'}},
                {'event':'workflow_finished','data':{'status':{'code':1},'outputs':{'responseContent':'最终回答'}}},
                {'event':'end'}]
        result=list(_reply_events(events))
        self.assertEqual([e['text'] for e in result if e['type']=='delta'],['最终'])
        self.assertEqual(result[-1]['reply'].text,'最终回答')
        events[2]['data']['status']['code']=500
        with self.assertRaises(_ProtocolError):list(_reply_events(events))
