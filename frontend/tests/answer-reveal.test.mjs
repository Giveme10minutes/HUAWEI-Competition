import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createAnswerReveal } from '../src/lib/answer-reveal.ts';

test('buffered complete answer is progressively revealed before completion', async () => {
  const seen=[];
  const reveal=createAnswerReveal(text=>seen.push(text));
  const answer='这是一段足够长的回答，需要分多次显示，不能一次弹出。';
  await reveal.finish(answer);
  assert.ok(seen.length>1);
  assert.ok(seen[0].length<answer.length);
  assert.equal(seen.at(-1),answer);
  assert.ok(seen.every((s,i)=>!i || s.startsWith(seen[i-1])));
  reveal.cancel();
});
test('final summary replaces streamed draft and preserves Unicode characters', async () => {
  const seen=[];
  const reveal=createAnswerReveal(text=>seen.push(text));
  reveal.update('草稿内容');
  await reveal.finish('最终答案😀不会重复结尾。');
  assert.equal(seen.at(-1),'最终答案😀不会重复结尾。');
  assert.ok(seen.every(s=>!/[\uD800-\uDBFF]$/.test(s)));
  reveal.cancel();
});
test('cancelling queued output stops late UI updates', async () => {
  const seen=[];
  const reveal=createAnswerReveal(text=>seen.push(text));
  const pending=reveal.finish('不应在取消后展示');
  reveal.cancel();
  await pending;
  assert.deepEqual(seen,[]);
});
