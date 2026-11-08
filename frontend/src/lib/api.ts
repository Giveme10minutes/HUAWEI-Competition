export type Conversation = {
  id: string;
  title: string;
  pinned: boolean;
  last_preview?: string;
  updated_at: string;
};
export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: string;
  error?: string;
  created_at: string;
};
export type Profile = {
  id: string;
  category: string;
  content: string;
  source: string;
  status: string;
};
export const planFields = [
  ["directions", "候选方向及依据"],
  ["gaps", "差距与关键未知"],
  ["stage_goals", "阶段目标"],
  ["actions", "近期学习实践安排"],
] as const;
export type TaskItem = {
  title: string; goal: string; instructions: string; minutes: number;
  evidence: string; acceptance: string;
};
export type ClueProposal = { category: string; content: string; source: string; quote: string };
export type PlanContent = Record<(typeof planFields)[number][0], string> & {
  change_note: string;
  task_items: TaskItem[];
  available_minutes: number | null;
};
export type Plan = PlanContent & {
  id: string;
  version_no: number;
  status: string;
  updated_at: string;
};
export type Plans = {
  draft: Plan | null;
  confirmed: Plan | null;
  versions: Plan[];
};
export const blankPlan = (): PlanContent => ({
  directions: "",
  gaps: "",
  stage_goals: "",
  actions: "",
  change_note: "",
  task_items: [],
  available_minutes: null,
});
// Only editable fields enter a write request; persisted versions also carry numeric metadata.
export function planContent(value: PlanContent): PlanContent {
  return {
    ...Object.fromEntries([...planFields.map(([key]) => key), "change_note"].map(key => [key, (value[key as keyof PlanContent] as string).trim()])),
    task_items: value.task_items.map(t => ({ ...t })),
    available_minutes: value.available_minutes,
  } as PlanContent;
}
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const r = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const data = await r.json().catch(() => null);
  if (!r.ok)
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : `请求失败（${r.status}），请稍后重试。`,
    );
  return data;
}
export async function replyStream(id: string, onDelta: (text: string) => void) {
  const response = await fetch(
    `/api/messages/${encodeURIComponent(id)}/stream`,
    { method: "POST" },
  );
  if (!response.ok || !response.body)
    throw new Error("无法读取回复，请稍后重试。");
  const reader = response.body.getReader(),
    decoder = new TextDecoder();
  let buffer = "",
    complete: { user_message: Message; reply: Message } | null = null;
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      let boundary: number;
      while ((boundary = buffer.indexOf("\n\n")) >= 0) {
        const frame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const raw = frame
          .split("\n")
          .filter((l) => l.startsWith("data:"))
          .map((l) => l.slice(5).trimStart())
          .join("\n");
        if (!raw) continue;
        const event = JSON.parse(raw);
        if (event.type === "error")
          throw new Error(event.message || "回复中断，请重试。");
        if (event.type === "delta" && typeof event.text === "string")
          onDelta(event.text);
        if (event.type === "complete") complete = event.data;
      }
      if (done) break;
    }
    if (!complete) throw new Error("回复连接中断，未收到完整回答；请重试。");
    return complete;
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}
