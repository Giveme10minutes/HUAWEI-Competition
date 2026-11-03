import { test, afterEach } from 'node:test'
import assert from 'node:assert/strict'
import { planContent, blankPlan, replyStream } from '../src/lib/api.ts'
const originalFetch=globalThis.fetch
afterEach(()=>{globalThis.fetch=originalFetch})
test('loaded draft/confirmed version can be edited without submitting version metadata',()=>{
 const version={...blankPlan(),directions:' 活动策划 ',change_note:' 修订 ',id:'old',version_no:3,status:'confirmed'}
 assert.deepEqual(planContent(version),{...blankPlan(),directions:'活动策划',change_note:'修订'})
 assert.equal(version.version_no,3)
})
function responseFor(frames){
 const bytes=new TextEncoder().encode(frames.map(data=>`data: ${JSON.stringify(data)}\n\n`).join(''))
 return new Response(new ReadableStream({start(c){for(let i=0;i<bytes.length;i+=7)c.enqueue(bytes.slice(i,i+7));c.close()}}))
}
test('fragmented UTF-8 SSE preserves deltas and uses complete answer as saved result',async()=>{
 const complete={user_message:{id:'u'},reply:{id:'a',content:'最终回答'}}
 globalThis.fetch=async()=>responseFor([{type:'delta',text:'你'},{type:'delta',text:'好'},{type:'complete',data:complete}])
 const deltas=[];assert.deepEqual(await replyStream('u',s=>deltas.push(s)),complete);assert.deepEqual(deltas,['你','好'])
})
test('interrupted SSE never returns a partial answer as complete',async()=>{
 globalThis.fetch=async()=>responseFor([{type:'delta',text:'半截回答'}])
 await assert.rejects(replyStream('u',()=>{}),/未收到完整回答/)
})
