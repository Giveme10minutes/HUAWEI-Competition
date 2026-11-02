"""Synthetic protocol regression tests; no cloud calls or real credentials."""
import io
import json
import unittest
from unittest.mock import patch
from email.message import Message

from scripts.test_lowcode_agent import ProbeError, collect_reply, invoke, sse_events, validate_url


def stream(*events):
    return io.BytesIO(''.join('data: ' + json.dumps(e, ensure_ascii=False) + '\n\n'
                            for e in events).encode())


class LowcodeProtocolTests(unittest.TestCase):
    def test_final_summary_replaces_deltas_and_filters_internal_payloads(self):
        data = stream({'event': 'message', 'content': '草稿', 'reasoning_content': '不应显示'},
                      {'event': 'plugin_end', 'content': {'secret': '不应显示'}},
                      {'event': 'summary_response', 'content': '最终回答'},
                      {'event': 'statistic_data', 'latency': {'overall': 3, 'model': 2, 'secret': '隐藏'}},
                      {'event': 'end'})
        self.assertEqual(collect_reply(sse_events(data)), ('最终回答', {'overall': 3, 'model': 2}))

    def test_deltas_without_summary(self):
        self.assertEqual(collect_reply(sse_events(stream(
            {'event': 'message', 'content': '你'}, {'event': 'message', 'content': '好'},
            {'event': 'end'})))[0], '你好')

    def test_sse_multiline_and_comments(self):
        data = io.BytesIO(b': heartbeat\r\nevent: message\r\ndata: {"event":"message",\r\ndata: "content":"ok"}\r\n\r\ndata: {"event":"end"}\r\n\r\n')
        self.assertEqual(collect_reply(sse_events(data))[0], 'ok')

    def test_failure_after_partial_output_does_not_report_success(self):
        with self.assertRaises(ProbeError) as caught:
            collect_reply(sse_events(stream({'event': 'message', 'content': '部分'},
                                           {'event': 'error', 'data': {'message': 'sensitive-raw-error'}},
                                           {'event': 'end'})))
        self.assertNotIn('sensitive-raw-error', str(caught.exception))

    def test_eof_before_end_is_failure(self):
        with self.assertRaises(ProbeError):
            collect_reply(sse_events(stream({'event': 'summary_response', 'content': '尚未结束'})))

    def test_reasoning_only_is_not_a_reply(self):
        with self.assertRaises(ProbeError):
            collect_reply(sse_events(stream({'event': 'message', 'reasoning_content': '不保存'},
                                           {'event': 'end'})))

    def test_invalid_frames(self):
        for raw in (b'data: invalid\n\n', b'data: []\n\n', b'data: \xff\n\n'):
            with self.subTest(raw=raw), self.assertRaises(ProbeError):
                list(sse_events(io.BytesIO(raw)))

    def test_refuses_insecure_or_credential_bearing_urls(self):
        for url in ('http://example.test/runtimes/demo/invocations',
                    'https://name:secret@example.test/runtimes/demo/invocations',
                    'https://example.test/runtimes/demo/invocations?key=secret',
                    'https://example.test/runtimes/demo/ws'):
            with self.subTest(url=url), self.assertRaises(ProbeError):
                validate_url(url)

    def test_request_matches_single_agent_protocol_without_retry(self):
        response = stream({'event': 'summary_response', 'content': 'ok'}, {'event': 'end'})
        response.status = 200
        response.headers = Message()
        response.headers['Content-Type'] = 'text/event-stream; charset=utf-8'
        with patch('scripts.test_lowcode_agent.build_opener') as opener:
            opener.return_value.open.return_value = response
            self.assertEqual(invoke('https://example.test/runtimes/demo/invocations',
                                    'synthetic-key', 'session-1', '你好')[0], 'ok')
            opener.return_value.open.assert_called_once()
            req = opener.return_value.open.call_args.args[0]
            self.assertEqual(json.loads(req.data), {'query': '你好', 'inputs': {}})
            self.assertEqual(req.get_header('Authorization'), 'Bearer synthetic-key')

    def test_redirect_does_not_forward_credentials(self):
        from scripts.test_lowcode_agent import NoRedirect
        with self.assertRaises(ProbeError):
            NoRedirect().redirect_request(None, None, 302, '', {}, 'https://another.test')


if __name__ == '__main__':
    unittest.main()
