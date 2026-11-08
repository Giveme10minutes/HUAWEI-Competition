import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import {
  ArrowUp,
  Plus,
  MoreHorizontal,
  Pin,
  Trash2,
  RotateCcw,
  Compass,
  Route,
  NotebookPen,
  MessageSquare,
  ChevronRight,
  Check,
  Pencil,
  Copy,
  PanelLeftClose,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { createAnswerReveal } from "@/lib/answer-reveal";
import { api, replyStream, blankPlan, planFields, planContent } from "@/lib/api";
import type {
  Conversation,
  Message as Msg,
  Profile,
  PlanContent,
  Plan,
  Plans,
  ClueProposal,
  TaskItem,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupTextarea,
  InputGroupAddon,
  InputGroupButton,
  InputGroupText,
} from "@/components/ui/input-group";
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuAction,
  SidebarInset,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  FieldGroup,
  Field,
  FieldLabel,
  FieldDescription,
} from "@/components/ui/field";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/components/ui/native-select";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import {
  Empty,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
  EmptyDescription,
  EmptyContent,
} from "@/components/ui/empty";
import { Spinner } from "@/components/ui/spinner";
import { Separator } from "@/components/ui/separator";
import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent,
} from "@/components/ui/collapsible";
import {
  MessageScrollerProvider,
  MessageScroller,
  MessageScrollerViewport,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerButton,
} from "@/components/ui/message-scroller";
import {
  Message,
  MessageContent,
  MessageHeader,
  MessageFooter,
} from "@/components/ui/message";
import { Bubble, BubbleContent } from "@/components/ui/bubble";

const categories = [
  "兴趣与偏好",
  "经历与做过的事",
  "专业与年级",
  "技能与能力（自述）",
  "现实约束（时间/地点/预算）",
  "目标与待探索问题",
  "其他",
];
const LAST = "career-explorer:last-conversation";
const prompts = [
  ["还没有方向", "从经历和兴趣里找线索", "我很迷茫，不知道以后想做什么。"],
  [
    "在几个方向间犹豫",
    "一起比较，找到关键差异",
    "我想比较几个方向，但不知道从哪开始。",
  ],
  [
    "已经有个目标",
    "看看差距，再安排下一步",
    "我有个大概想法，想知道还差什么。",
  ],
];
const time = (s: string) =>
  new Date(s).toLocaleString("zh-CN", {
    timeZone: "Asia/Shanghai",
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
function Markdown({ text }: { text: string }) {
  return (
    <div className="markdown">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
    </div>
  );
}
function NoData({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyTitle>{title}</EmptyTitle>
        <EmptyDescription>{children}</EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}
function PlanSections({ plan }: { plan: Plan }) {
  return (
    <div className="flex flex-col gap-6">
      {planFields
        .filter(([key]) => plan[key])
        .map(([key, label]) => (
          <section key={key}>
            <h3 className="section-title">{label}</h3>
            <p className="whitespace-pre-wrap leading-7">{plan[key]}</p>
          </section>
        ))}
      {!!plan.task_items.length && <section><h3 className="section-title">本版行动及验收</h3><div className="flex flex-col gap-3">{plan.task_items.map((t, i) => <div key={i}><p>{i + 1}. {t.title} · {t.minutes}分钟</p><p>目标：{t.goal}</p><p>{t.instructions}</p><p>成果：{t.evidence}</p><p>验收：{t.acceptance}</p></div>)}</div></section>}
    </div>
  );
}
function NavigationClose() {
  const { toggleSidebar } = useSidebar();
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="收起侧栏"
      onClick={toggleSidebar}
    >
      <PanelLeftClose />
    </Button>
  );
}

export default function App() {
  const [convs, setConvs] = useState<Conversation[]>([]),
    [deleted, setDeleted] = useState<Conversation[]>([]);
  const [active, setActive] = useState<string | null>(null),
    [title, setTitle] = useState("新的对话"),
    [messages, setMessages] = useState<Msg[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]),
    [plans, setPlans] = useState<Plans>({
      draft: null,
      confirmed: null,
      versions: [],
    });
  const [configured, setConfigured] = useState(true),
    [loaded, setLoaded] = useState(false),
    [busy, setBusy] = useState(false),
    [recordBusy, setRecordBusy] = useState(false);
  const [input, setInput] = useState(""),
    [stream, setStream] = useState(""),
    [replying, setReplying] = useState(false),
    [sheet, setSheet] = useState(false),
    [tab, setTab] = useState("profile");
  const [editor, setEditor] = useState<PlanContent>(blankPlan),
    [draftId, setDraftId] = useState<string | null>(null);
  const [profileEdit, setProfileEdit] = useState<Profile | null>(null),
    [addOpen, setAddOpen] = useState(false);
  const [profileForm, setProfileForm] = useState({
    category: categories[0],
    content: "",
    source: "self_reported",
  });
  const [proposals, setProposals] = useState<ClueProposal[]>([]);
  const [extracting, setExtracting] = useState<string | null>(null);
  const [confirmation, setConfirmation] = useState<{
    title: string;
    description: string;
    action: () => Promise<void>;
  } | null>(null);
  const lock = useRef(false),
    recordLock = useRef(false),
    textarea = useRef<HTMLTextAreaElement>(null);
  const remember = (id: string) => {
    try {
      localStorage.setItem(LAST, id);
    } catch {
      /* optional */
    }
  };
  const openPanel = (name: string) => {
    setTab(name);
    setSheet(true);
  };
  const fail = (e: unknown) =>
    toast.error(e instanceof Error ? e.message : "操作失败，请重试。");
  async function lists() {
    const [a, b] = await Promise.all([
      api<{ conversations: Conversation[] }>("/api/conversations"),
      api<{ conversations: Conversation[] }>("/api/conversations?deleted=true"),
    ]);
    setConvs(a.conversations);
    setDeleted(b.conversations);
  }
  async function loadProfiles() {
    const d = await api<{ items: Profile[] }>("/api/profile");
    setProfiles(d.items);
  }
  async function loadPlans(sync = false) {
    const d = await api<Plans>("/api/plan");
    setPlans(d);
    if (sync) {
      setEditor(d.draft || blankPlan());
      setDraftId(d.draft?.id || null);
    }
  }
  async function openConversation(id: string) {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    try {
      const d = await api<{ conversation: Conversation; messages: Msg[] }>(
        `/api/conversations/${id}`,
      );
      setActive(id);
      setTitle(d.conversation.title);
      setMessages(d.messages);
      remember(id);
    } catch (e) {
      fail(e);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  useEffect(() => {
    let live = true;
    async function init() {
      try {
        const results = await Promise.allSettled([
          api<{ agent_configured: boolean }>("/api/meta"),
          api<{ conversations: Conversation[] }>("/api/conversations"),
          loadProfiles(),
          loadPlans(true),
        ]);
        if (!live) return;
        if (results[0].status === "fulfilled")
          setConfigured(results[0].value.agent_configured);
        else setConfigured(false);
        if (results.some((r) => r.status === "rejected"))
          toast.error("部分记录未能读取，请刷新页面重试。");
        if (results[1].status === "fulfilled") {
          const list = results[1].value.conversations;
          setConvs(list);
          let remembered = "";
          try {
            remembered = localStorage.getItem(LAST) || "";
          } catch {
            /* optional */
          }
          const preferred = list.find((c) => c.id === remembered) || list[0];
          if (preferred) await openConversation(preferred.id);
        }
        await lists();
      } catch (e) {
        fail(e);
      } finally {
        if (live) setLoaded(true);
      }
    }
    void init();
    return () => {
      live = false;
    };
  }, []);
  async function record(action: () => Promise<void>) {
    if (recordLock.current) return;
    recordLock.current = true;
    setRecordBusy(true);
    try {
      await action();
    } catch (e) {
      fail(e);
    } finally {
      recordLock.current = false;
      setRecordBusy(false);
    }
  }
  function ask(
    title: string,
    description: string,
    action: () => Promise<void>,
  ) {
    setConfirmation({ title, description, action });
  }
  async function manage(c: Conversation, action: "pin" | "delete" | "restore") {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    try {
      const url = `/api/conversations/${c.id}`;
      await api(
        action === "restore" ? `${url}/restore` : url,
        action === "restore" ? "POST" : action === "pin" ? "PATCH" : "DELETE",
        action === "pin" ? { pinned: !c.pinned } : undefined,
      );
      if (action === "delete" && active === c.id) {
        setActive(null);
        setMessages([]);
        setTitle("新的对话");
        remember("");
      }
      await lists();
      toast.success(
        action === "restore"
          ? "对话已恢复"
          : action === "pin"
            ? "置顶状态已更新"
            : "对话已移到已删除，可随时恢复",
      );
    } catch (e) {
      fail(e);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  async function newConversation() {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    try {
      const d = await api<{ conversation: Conversation }>(
        "/api/conversations",
        "POST",
      );
      setActive(d.conversation.id);
      setTitle(d.conversation.title);
      setMessages([]);
      remember(d.conversation.id);
      await lists();
      textarea.current?.focus();
    } catch (e) {
      fail(e);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  async function requestReply(id: string, cid: string) {
    setReplying(true);
    setStream("");
    const reveal = createAnswerReveal(setStream);
    let received = "";
    try {
      const d = await replyStream(id, (text) => { received += text; reveal.update(received); });
      await reveal.finish(d.reply.content);
      setMessages((ms) => [
        ...ms
          .filter((m) => m.id !== d.reply.id)
          .map((m) => (m.id === id ? d.user_message : m)),
        d.reply,
      ]);
    } catch (e) {
      try {
        const d = await api<{ messages: Msg[] }>(`/api/conversations/${cid}`);
        setMessages(d.messages);
      } catch {
        /* preserve user message */
      }
      throw e;
    } finally {
      reveal.cancel();
      setStream("");
      setReplying(false);
      await lists().catch(() => {});
    }
  }
  async function send(event?: FormEvent) {
    event?.preventDefault();
    if (lock.current || !input.trim() || !loaded) return;
    const content = input.trim();
    lock.current = true;
    setBusy(true);
    let saved = false;
    try {
      let cid = active;
      if (!cid) {
        const d = await api<{ conversation: Conversation }>(
          "/api/conversations",
          "POST",
        );
        cid = d.conversation.id;
        setActive(cid);
        remember(cid);
      }
      const clientId = crypto.randomUUID();
      const d = await api<{ message: Msg }>(
        `/api/conversations/${cid}/messages`,
        "POST",
        { content, client_id: clientId },
      );
      saved = true;
      setInput("");
      setMessages((ms) => [...ms, d.message]);
      await lists().catch(() => {});
      await requestReply(d.message.id, cid);
    } catch (e) {
      fail(e);
      if (!saved) setInput(content);
    } finally {
      lock.current = false;
      setBusy(false);
      textarea.current?.focus();
    }
  }
  async function retry(m: Msg) {
    if (lock.current || !active) return;
    lock.current = true;
    setBusy(true);
    try {
      await requestReply(m.id, active);
    } catch (e) {
      fail(e);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  async function extract(m: Msg, kind: "profile" | "plan") {
    if (recordLock.current || busy) return;
    await record(async () => {
      setExtracting(m.id);
      try {
        if (kind === "profile") {
          const d = await api<{ items: ClueProposal[] }>(`/api/messages/${m.id}/extract`, "POST", { kind });
          setProposals(d.items);
          openPanel("profile");
          toast.success(d.items.length ? "已整理候选线索，请逐条审核" : "没有提取到有原话支持的新线索");
        } else {
          const d = await api<{ plan: PlanContent; warnings?: string[] }>(`/api/messages/${m.id}/extract`, "POST", { kind });
          setEditor(d.plan);
          setDraftId(null);
          openPanel("plan");
          if (d.warnings?.length) toast.warning(d.warnings.join("；"), { duration: 10000 });
          else toast.success("已放入编辑区，尚未保存或确认");
        }
      } finally { setExtracting(null); }
    });
  }
  function useTask(task: TaskItem, index: number, feedback = false) {
    if (busy) return;
    const version = plans.confirmed;
    if (!version) return;
    const text = `我想${feedback ? "反馈成果或讨论困难" : "开始学习并完成任务"}。当前已确认规划v${version.version_no}，第${index + 1}项：${task.title}。\n阶段关联：${task.goal}\n动作：${task.instructions}\n预计${task.minutes}分钟。成果：${task.evidence}\n原验收：${task.acceptance}\n${feedback ? "我的成果或困难：" : "请从适合我基础的第一小步开始，不直接给出整个练习答案。"}`;
    const apply = async () => { setInput(text); setSheet(false); setTimeout(() => textarea.current?.focus(), 0); };
    if (input.trim()) ask("替换尚未发送的输入？", "任务内容将放入输入框，确认后仍需手动发送。", apply);
    else void apply();
  }
  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    if (!profileForm.content.trim()) return;
    await record(async () => {
      await api(
        profileEdit ? `/api/profile/${profileEdit.id}` : "/api/profile",
        profileEdit ? "PATCH" : "POST",
        { ...profileForm, content: profileForm.content.trim() },
      );
      await loadProfiles();
      setProposals(ps => ps.filter(p => p.content !== profileForm.content.trim()));
      setProfileEdit(null);
      setProfileForm({
        category: categories[0],
        content: "",
        source: "self_reported",
      });
      setAddOpen(false);
      toast.success("线索已保存，请确认后用于对话");
    });
  }
  async function savePlan(confirm = false) {
    if (editor.task_items.some(t => !t.title.trim() || !t.goal.trim() || !t.instructions.trim() || !t.evidence.trim() || !t.acceptance.trim() || !Number.isInteger(t.minutes) || t.minutes < 1)) {
      toast.error("请补齐每项行动的名称、目标、动作、成果、验收和正整数分钟数");
      return;
    }
    if (editor.task_items.length && !editor.stage_goals.trim()) {
      toast.error("请填写行动关联的阶段目标");
      return;
    }
    if (!planFields.some(([k]) => editor[k].trim())) {
      toast.error("至少填写一项规划内容");
      return;
    }
    await record(async () => {
      const body = planContent(editor);
      const d = await api<{ version: Plan }>(
        draftId ? `/api/plan/versions/${draftId}` : "/api/plan/versions",
        draftId ? "PUT" : "POST",
        body,
      );
      setDraftId(d.version.id);
      if (confirm) {
        await api(`/api/plan/versions/${d.version.id}/confirm`, "POST");
        await loadPlans(true);
        toast.success(`已确认第 ${d.version.version_no} 版规划`);
      } else {
        await loadPlans();
        toast.success("草稿已保存，尚未确认");
      }
    });
  }
  const currentTitle = convs.find((c) => c.id === active)?.title || title;
  const empty = !messages.length && !replying;
  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <div className="brand-row">
            <div className="brand-icon">
              <Compass />
            </div>
            <div>
              <strong>职业探索助手</strong>
              <p>慢慢看清你的方向</p>
            </div>
            <NavigationClose />
          </div>
          <Button onClick={newConversation} disabled={busy || !loaded}>
            <Plus data-icon="inline-start" />
            开始新对话
          </Button>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton onClick={() => openPanel("profile")}>
                    <NotebookPen />
                    <span>个人线索</span>
                    <Badge variant="secondary">{profiles.length}</Badge>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton onClick={() => openPanel("tasks")}>
                    <Check /><span>学习行动</span>
                    <Badge variant="secondary">{plans.confirmed?.task_items.length || 0}</Badge>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton onClick={() => openPanel("plan")}>
                    <Route />
                    <span>我的职业规划</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
          <Separator />
          <SidebarGroup>
            <SidebarGroupLabel>最近对话</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {!loaded && (
                  <SidebarMenuItem>
                    <Spinner />
                    正在读取记录…
                  </SidebarMenuItem>
                )}
                {convs.map((c) => (
                  <SidebarMenuItem key={c.id}>
                    <SidebarMenuButton
                      isActive={active === c.id}
                      disabled={busy}
                      onClick={() => openConversation(c.id)}
                      tooltip={c.title}
                    >
                      <MessageSquare />
                      <span>
                        {c.pinned ? "置顶 · " : ""}
                        {c.title}
                      </span>
                    </SidebarMenuButton>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <SidebarMenuAction
                          disabled={busy}
                          aria-label={`管理对话：${c.title}`}
                        >
                          <MoreHorizontal />
                        </SidebarMenuAction>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start">
                        <DropdownMenuGroup>
                          <DropdownMenuItem onSelect={() => manage(c, "pin")}>
                            <Pin />
                            {c.pinned ? "取消置顶" : "置顶对话"}
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onSelect={() =>
                              ask(
                                "删除这段对话？",
                                "对话将移到已删除列表，可恢复。个人线索、规划与云端会话会保留。",
                                () => manage(c, "delete"),
                              )
                            }
                          >
                            <Trash2 />
                            删除对话
                          </DropdownMenuItem>
                        </DropdownMenuGroup>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </SidebarMenuItem>
                ))}
                {loaded && !convs.length && (
                  <p className="sidebar-hint">
                    第一次探索，从一句话开始。对话会自动保存在这里。
                  </p>
                )}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        <SidebarFooter>
          <Collapsible>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" className="w-full justify-start">
                <Trash2 data-icon="inline-start" />
                已删除的对话<Badge variant="secondary">{deleted.length}</Badge>
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="max-h-48 overflow-auto">
              {deleted.map((c) => (
                <div className="flex items-center gap-2 py-2" key={c.id}>
                  <span className="min-w-0 flex-1 truncate text-sm">
                    {c.title}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={busy}
                    onClick={() => manage(c, "restore")}
                  >
                    <RotateCcw data-icon="inline-start" />
                    恢复
                  </Button>
                </div>
              ))}
              {!deleted.length && (
                <p className="sidebar-hint">暂无已删除的对话</p>
              )}
            </CollapsibleContent>
          </Collapsible>
          <Separator />
          <p className="sidebar-hint">
            记录保存在本机。发送时，消息、已确认线索与当前规划会交给在线助手。
          </p>
        </SidebarFooter>
      </Sidebar>
      <SidebarInset className="h-dvh min-w-0 overflow-hidden">
        <header className="workspace-header">
          <div className="flex min-w-0 items-center gap-3">
            <SidebarTrigger aria-label="展开或收起对话列表" />
            <Separator orientation="vertical" className="h-5" />
            <h1 className="truncate">{active ? currentTitle : "探索对话"}</h1>
          </div>
          <Button variant="ghost" onClick={() => openPanel("plan")}>
            <Route data-icon="inline-start" />
            我的规划
          </Button>
        </header>
        {!configured && (
          <Alert className="mx-auto mt-3 max-w-3xl">
            <AlertTitle>在线助手尚未连接</AlertTitle>
            <AlertDescription>
              本机记录仍可使用，连接配置后可以重试消息。
            </AlertDescription>
          </Alert>
        )}
        <div className="flex min-h-0 flex-1 flex-col">
          <MessageScrollerProvider
            key={active || "new"}
            autoScroll
            defaultScrollPosition="end"
          >
            <MessageScroller>
              <MessageScrollerViewport>
                <MessageScrollerContent className="conversation-content">
                  {empty ? (
                    <MessageScrollerItem messageId="welcome">
                      <Empty className="welcome-state">
                        <EmptyHeader>
                          <EmptyMedia variant="icon">
                            <Compass />
                          </EmptyMedia>
                          <EmptyTitle>你的方向，从这里聊起。</EmptyTitle>
                          <EmptyDescription>
                            不必先想清楚未来。聊聊你的经历、犹豫，
                            <br />
                            或最近让你感兴趣的一件小事。
                          </EmptyDescription>
                        </EmptyHeader>
                        <EmptyContent className="suggestions">
                          {prompts.map(([label, description, prompt]) => (
                            <Button
                              key={label}
                              variant="outline"
                              disabled={busy || !loaded}
                              onClick={() => {
                                setInput(prompt);
                                textarea.current?.focus();
                              }}
                            >
                              <span>{label}</span>
                              <small>{description}</small>
                              <ChevronRight data-icon="inline-end" />
                            </Button>
                          ))}
                        </EmptyContent>
                      </Empty>
                    </MessageScrollerItem>
                  ) : (
                    messages.map((m) => (
                      <MessageScrollerItem
                        key={m.id}
                        messageId={m.id}
                        scrollAnchor={m.role === "user"}
                      >
                        <Message align={m.role === "user" ? "end" : "start"}>
                          <MessageContent>
                            <MessageHeader>
                              {m.role === "assistant" ? "职业探索助手" : "你"}
                            </MessageHeader>
                            <Bubble
                              align={m.role === "user" ? "end" : "start"}
                              variant={
                                m.role === "user" ? "secondary" : "ghost"
                              }
                            >
                              <BubbleContent>
                                {m.role === "assistant" ? (
                                  <Markdown text={m.content} />
                                ) : (
                                  <div className="whitespace-pre-wrap">
                                    {m.content}
                                  </div>
                                )}
                              </BubbleContent>
                            </Bubble>
                            <MessageFooter>
                              <span>{time(m.created_at)}</span>
                              {m.role === "assistant" && (
                                <>
                                <Button size="sm" variant="outline" disabled={busy || recordBusy} onClick={() => void extract(m, "profile")}>
                                  {extracting === m.id && <Spinner />}整理线索
                                </Button>
                                <Button size="sm" variant="outline" disabled={busy || recordBusy} onClick={() => {
                                  const run = async () => { await extract(m, "plan"); };
                                  if (planFields.some(([k]) => editor[k].trim()) || editor.task_items.length)
                                    ask("将回答整理为新规划草稿？", "会替换编辑区内容，已保存版本保持不变。", run);
                                  else void run();
                                }}>整理规划</Button>
                                <Button
                                  variant="ghost"
                                  size="icon-sm"
                                  aria-label="复制回答"
                                  onClick={() =>
                                    navigator.clipboard
                                      .writeText(m.content)
                                      .then(() => toast.success("回答已复制"))
                                      .catch(() =>
                                        toast.error("复制失败，请手动选择文字"),
                                      )
                                  }
                                >
                                  <Copy />
                                </Button>
                                </>
                              )}
                              {m.role === "user" &&
                                ["failed", "pending"].includes(m.status) &&
                                !replying && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    disabled={busy}
                                    onClick={() => retry(m)}
                                  >
                                    <RotateCcw data-icon="inline-start" />
                                    重试回复
                                  </Button>
                                )}
                            </MessageFooter>
                            {m.status === "failed" && (
                              <Alert variant="destructive">
                                <AlertTitle>回复失败</AlertTitle>
                                <AlertDescription>
                                  {m.error || "请重试这条消息。"}
                                </AlertDescription>
                              </Alert>
                            )}
                          </MessageContent>
                        </Message>
                      </MessageScrollerItem>
                    ))
                  )}
                  {replying && (
                    <MessageScrollerItem messageId="streaming">
                      <Message>
                        <MessageContent>
                          <MessageHeader>职业探索助手</MessageHeader>
                          <Bubble variant="ghost">
                            <BubbleContent>
                              {stream ? (
                                <Markdown text={stream} />
                              ) : (
                                <div className="flex items-center gap-2">
                                  <Spinner />
                                  正在整理回复…
                                </div>
                              )}
                            </BubbleContent>
                          </Bubble>
                          <MessageFooter>
                            正在生成，完成后自动保存
                          </MessageFooter>
                        </MessageContent>
                      </Message>
                    </MessageScrollerItem>
                  )}
                </MessageScrollerContent>
              </MessageScrollerViewport>
              <MessageScrollerButton aria-label="回到最新消息" />
            </MessageScroller>
          </MessageScrollerProvider>
          <form
            className={cn("composer-wrap", empty && "composer-welcome")}
            onSubmit={send}
          >
            <InputGroup className="prompt-input">
              <InputGroupTextarea
                ref={textarea}
                aria-label="发送给职业探索助手的消息"
                placeholder="说说你现在的想法…"
                value={input}
                maxLength={4000}
                rows={2}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (
                    e.key === "Enter" &&
                    !e.shiftKey &&
                    !e.nativeEvent.isComposing &&
                    e.keyCode !== 229
                  ) {
                    e.preventDefault();
                    void send();
                  }
                }}
              />
              <InputGroupAddon align="block-end">
                <InputGroupText>
                  {busy ? "助手正在回复…" : "Enter 发送 · Shift + Enter 换行"}
                </InputGroupText>
                <InputGroupButton
                  className="ml-auto"
                  size="icon-sm"
                  variant="default"
                  type="submit"
                  aria-label="发送消息"
                  disabled={busy || !loaded || !input.trim()}
                >
                  {busy ? <Spinner /> : <ArrowUp />}
                </InputGroupButton>
              </InputGroupAddon>
            </InputGroup>
            <p className="composer-note">
              从真实经历出发，建议与判断都可以继续核实。
            </p>
          </form>
        </div>
      </SidebarInset>
      <Sheet open={sheet} onOpenChange={setSheet}>
        <SheetContent className="records-sheet">
          <SheetHeader>
            <SheetTitle>我的探索记录</SheetTitle>
            <SheetDescription>
              整理已知线索，逐步形成属于你的规划。
            </SheetDescription>
          </SheetHeader>
          <Tabs value={tab} onValueChange={setTab} className="min-h-0 flex-1">
            <TabsList className="mx-6">
              <TabsTrigger value="profile">个人线索</TabsTrigger>
              <TabsTrigger value="plan">职业规划</TabsTrigger>
              <TabsTrigger value="tasks">学习行动</TabsTrigger>
            </TabsList>
            <TabsContent value="tasks" className="records-body">
              <h2>当前学习行动</h2>
              <p className="record-intro">来自已确认规划{plans.confirmed ? ` v${plans.confirmed.version_no}` : ""}。开始学习或反馈成果时，会把原任务要求带入对话。</p>
              {!plans.confirmed?.task_items.length && <NoData title="还没有已确认的行动">从助手回答整理规划，在规划编辑区补齐行动并确认后显示。</NoData>}
              {plans.confirmed?.task_items.map((task, i) => <Card key={`${plans.confirmed!.id}-${i}`}>
                <CardHeader><CardTitle>{i + 1}. {task.title}</CardTitle><CardDescription>{task.minutes} 分钟 · {task.goal}</CardDescription></CardHeader>
                <CardContent className="flex flex-col gap-3"><p className="whitespace-pre-wrap">{task.instructions}</p><p>提交成果：{task.evidence}</p><p>原验收：{task.acceptance}</p></CardContent>
                <CardFooter className="flex gap-2"><Button disabled={busy} onClick={() => useTask(task, i)}>开始学习</Button><Button variant="outline" disabled={busy} onClick={() => useTask(task, i, true)}>反馈成果或困难</Button></CardFooter>
              </Card>)}
            </TabsContent>
            <TabsContent value="profile" className="records-body">
              {!!proposals.length && <section className="flex flex-col gap-3" aria-label="候选线索">
                <h3>从对话整理的候选线索</h3><p className="text-sm text-muted-foreground">尚未保存。先对照原话审核，保存后仍需确认才用于对话。</p>
                {proposals.map((p, i) => <Card key={i} size="sm"><CardHeader><CardTitle>{p.category}</CardTitle><CardDescription>{p.source === "self_reported" ? "自述概括" : "助手推断，需核实"}</CardDescription></CardHeader><CardContent><p>{p.content}</p><p className="mt-2 text-muted-foreground">原话：{p.quote}</p></CardContent><CardFooter className="flex gap-2"><Button variant="outline" disabled={recordBusy} onClick={() => { setProfileEdit(null); setProfileForm({ category: p.category, content: p.content, source: p.source }); setAddOpen(true); }}>放入表单编辑</Button><Button variant="ghost" onClick={() => setProposals(ps => ps.filter((_, j) => j !== i))}>忽略</Button></CardFooter></Card>)}
              </section>}
              <div className="flex items-center justify-between gap-3">
                <h2>个人线索</h2>
                <Badge variant="secondary">
                  {profiles.filter((p) => p.status === "confirmed").length}{" "}
                  条已确认
                </Badge>
              </div>
              <p className="record-intro">
                线索确认后才用于对话；聊天中的推断不会自动写入。
              </p>
              <Collapsible open={addOpen} onOpenChange={setAddOpen}>
                <CollapsibleTrigger asChild>
                  <Button variant="outline">
                    <Plus data-icon="inline-start" />
                    {profileEdit ? "修改线索" : "添加一条线索"}
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="pt-5">
                  <form onSubmit={saveProfile}>
                    <FieldGroup>
                      <Field>
                        <FieldLabel htmlFor="profile-category">类别</FieldLabel>
                        <NativeSelect
                          id="profile-category"
                          value={profileForm.category}
                          onChange={(e) =>
                            setProfileForm((f) => ({
                              ...f,
                              category: e.target.value,
                            }))
                          }
                        >
                          {categories.map((c) => (
                            <NativeSelectOption key={c}>{c}</NativeSelectOption>
                          ))}
                        </NativeSelect>
                      </Field>
                      <Field>
                        <FieldLabel htmlFor="profile-content">内容</FieldLabel>
                        <Textarea
                          id="profile-content"
                          value={profileForm.content}
                          maxLength={2000}
                          required
                          rows={3}
                          placeholder="例如：我喜欢把复杂的事情讲清楚。"
                          onChange={(e) =>
                            setProfileForm((f) => ({
                              ...f,
                              content: e.target.value,
                            }))
                          }
                        />
                      </Field>
                      <Field>
                        <FieldLabel htmlFor="profile-source">来源</FieldLabel>
                        <NativeSelect
                          id="profile-source"
                          value={profileForm.source}
                          onChange={(e) =>
                            setProfileForm((f) => ({
                              ...f,
                              source: e.target.value,
                            }))
                          }
                        >
                          <NativeSelectOption value="self_reported">
                            我的自述
                          </NativeSelectOption>
                          <NativeSelectOption value="assistant_inferred">
                            助手推断（待核实）
                          </NativeSelectOption>
                        </NativeSelect>
                        <FieldDescription>
                          保留线索来源，修改后需重新确认。
                        </FieldDescription>
                      </Field>
                      <Field orientation="horizontal">
                        <Button type="submit" disabled={recordBusy}>
                          保存为待确认
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          onClick={() => {
                            setAddOpen(false);
                            setProfileEdit(null);
                            setProfileForm({
                              category: categories[0],
                              content: "",
                              source: "self_reported",
                            });
                          }}
                        >
                          取消
                        </Button>
                      </Field>
                    </FieldGroup>
                  </form>
                </CollapsibleContent>
              </Collapsible>
              <div className="flex flex-col gap-4 pt-6">
                {profiles.map((p) => (
                  <Card key={p.id}>
                    <CardHeader>
                      <CardTitle>{p.category}</CardTitle>
                      <CardDescription>
                        {p.source === "assistant_inferred"
                          ? "助手推断"
                          : "我的自述"}{" "}
                        · {p.status === "confirmed" ? "已确认" : "待确认"}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="whitespace-pre-wrap leading-7">
                        {p.content}
                      </p>
                    </CardContent>
                    <CardFooter className="flex-wrap gap-2">
                      {p.status !== "confirmed" && (
                        <Button
                          disabled={recordBusy}
                          size="sm"
                          onClick={() =>
                            record(async () => {
                              await api(`/api/profile/${p.id}/confirm`, "POST");
                              await loadProfiles();
                              toast.success("线索已确认");
                            })
                          }
                        >
                          <Check data-icon="inline-start" />
                          确认线索
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={recordBusy}
                        onClick={() => {
                          setProfileEdit(p);
                          setProfileForm({
                            category: p.category,
                            content: p.content,
                            source: p.source,
                          });
                          setAddOpen(true);
                        }}
                      >
                        <Pencil data-icon="inline-start" />
                        修改
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={recordBusy}
                        onClick={() =>
                          ask(
                            "删除这条线索？",
                            "删除后无法恢复，已保存的规划不受影响。",
                            () =>
                              record(async () => {
                                await api(`/api/profile/${p.id}`, "DELETE");
                                await loadProfiles();
                                if (profileEdit?.id === p.id) {
                                  setProfileEdit(null);
                                  setAddOpen(false);
                                }
                                toast.success("线索已删除");
                              }),
                          )
                        }
                      >
                        删除
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
              {!profiles.length && (
                <NoData title="还没有个人线索">
                  可以先聊聊，之后把重要的经历和想法记在这里。
                </NoData>
              )}
            </TabsContent>
            <TabsContent value="plan" className="records-body">
              <div className="flex items-center justify-between gap-3">
                <h2>职业规划</h2>
                <Badge variant="secondary">
                  {plans.draft
                    ? `v${plans.draft.version_no} 草稿`
                    : plans.confirmed
                      ? `v${plans.confirmed.version_no} 已确认`
                      : "尚未形成"}
                </Badge>
              </div>
              <p className="record-intro">
                方向依据、能力差距与近期行动，放在一起看。
              </p>
              <Card>
                <CardHeader>
                  <CardTitle>当前已确认的规划</CardTitle>
                  <CardDescription>
                    这一版会供助手在后续对话中参考。
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {plans.confirmed ? (
                    <PlanSections plan={plans.confirmed} />
                  ) : (
                    <p className="text-muted-foreground">
                      还没有已确认的规划，可以先保存一份草稿。
                    </p>
                  )}
                </CardContent>
                <CardFooter>
                  {plans.confirmed && !plans.draft && (
                    <Button
                      variant="outline"
                      disabled={recordBusy}
                      onClick={() => {
                        const action = async () => {
                          setEditor(plans.confirmed!);
                          setDraftId(null);
                        };
                        if (planFields.some(([k]) => editor[k].trim()))
                          ask(
                            "替换编辑区内容？",
                            "将使用已确认规划作为新草稿的基础，未保存的编辑内容会被替换。",
                            action,
                          );
                        else void action();
                      }}
                    >
                      在这一版基础上修改
                    </Button>
                  )}
                </CardFooter>
              </Card>
              <section className="flex flex-col gap-5 pt-8">
                <h3 className="section-title">
                  {draftId ? "继续编辑草稿" : "整理一份规划草稿"}
                </h3>
                <p className="text-sm leading-6 text-muted-foreground">
                  可从对话中整理或复制，只填已讨论的部分。草稿确认后才会用于对话，后续修改保留历史。
                </p>
                <FieldGroup>
                  {planFields.map(([key, label]) => (
                    <Field key={key}>
                      <FieldLabel htmlFor={`plan-${key}`}>{label}</FieldLabel>
                      <Textarea
                        id={`plan-${key}`}
                        rows={3}
                        maxLength={8000}
                        value={editor[key]}
                        onChange={(e) =>
                          setEditor((f) => ({ ...f, [key]: e.target.value }))
                        }
                        placeholder={`写下已讨论的${label}，也可以暂时留空。`}
                      />
                    </Field>
                  ))}
                  <p>行动预计合计 {editor.task_items.reduce((sum, t) => sum + t.minutes, 0)} 分钟（仅作参考）</p>
                  {editor.task_items.map((task, i) => <Card key={i}>
                    <CardHeader><CardTitle>行动 {i + 1}</CardTitle><CardDescription>将随本版规划保存；确认后出现在学习行动栏。</CardDescription></CardHeader>
                    <CardContent><FieldGroup>
                      {([['title', '名称'], ['goal', '关联阶段目标'], ['instructions', '具体动作'], ['evidence', '提交成果'], ['acceptance', '必交验收']] as const).map(([key, label]) => <Field key={key}><FieldLabel htmlFor={`task-${i}-${key}`}>{label}</FieldLabel><Textarea id={`task-${i}-${key}`} rows={2} value={task[key]} onChange={e => setEditor(f => ({ ...f, task_items: f.task_items.map((t, j) => j === i ? { ...t, [key]: e.target.value } : t) }))} /></Field>)}
                      <Field><FieldLabel htmlFor={`task-${i}-minutes`}>预计分钟</FieldLabel><Input id={`task-${i}-minutes`} type="number" min={1} value={task.minutes} onChange={e => setEditor(f => ({ ...f, task_items: f.task_items.map((t, j) => j === i ? { ...t, minutes: Number(e.target.value) } : t) }))} /></Field>
                    </FieldGroup></CardContent>
                    <CardFooter><Button variant="ghost" onClick={() => setEditor(f => ({ ...f, task_items: f.task_items.filter((_, j) => j !== i) }))}>移除这项行动</Button></CardFooter>
                  </Card>)}
                  <Button variant="outline" disabled={editor.task_items.length >= 20} onClick={() => setEditor(f => ({ ...f, task_items: [...f.task_items, { title: '', goal: '', instructions: '', minutes: 30, evidence: '', acceptance: '' }] }))}>添加学习行动</Button>
                  <Field>
                    <FieldLabel htmlFor="plan-note">
                      修改说明（可选）
                    </FieldLabel>
                    <Input
                      id="plan-note"
                      value={editor.change_note}
                      maxLength={500}
                      onChange={(e) =>
                        setEditor((f) => ({
                          ...f,
                          change_note: e.target.value,
                        }))
                      }
                    />
                  </Field>
                  <Field orientation="horizontal">
                    <Button
                      variant="outline"
                      disabled={recordBusy}
                      onClick={() => savePlan()}
                    >
                      保存草稿
                    </Button>
                    <Button
                      disabled={recordBusy}
                      onClick={() =>
                        ask(
                          "确认这一版规划？",
                          "确认后供助手参考。此前已确认版本将保留为历史，新修改不会覆盖历史。",
                          () => savePlan(true),
                        )
                      }
                    >
                      {recordBusy && <Spinner data-icon="inline-start" />}
                      确认这一版
                    </Button>
                  </Field>
                </FieldGroup>
              </section>
              <section className="flex flex-col gap-4 pt-10">
                <h3 className="section-title">历史版本</h3>
                {plans.versions.map((p) => (
                  <Collapsible key={p.id}>
                    <Card>
                      <CardHeader>
                        <CardTitle>
                          第 {p.version_no} 版{" "}
                          <Badge variant="outline">
                            {p.status === "confirmed"
                              ? "已确认"
                              : p.status === "draft"
                                ? "草稿"
                                : "历史版本"}
                          </Badge>
                        </CardTitle>
                        <CardDescription>
                          {time(p.updated_at)}
                          {p.change_note && ` · ${p.change_note}`}
                        </CardDescription>
                      </CardHeader>
                      <CardFooter>
                        <CollapsibleTrigger asChild>
                          <Button variant="ghost" size="sm">
                            查看内容
                            <ChevronRight data-icon="inline-end" />
                          </Button>
                        </CollapsibleTrigger>
                      </CardFooter>
                      <CollapsibleContent>
                        <CardContent>
                          <PlanSections plan={p} />
                        </CardContent>
                      </CollapsibleContent>
                    </Card>
                  </Collapsible>
                ))}
                {!plans.versions.length && (
                  <NoData title="还没有历史版本">
                    保存草稿后，可以在这里查看各版内容。
                  </NoData>
                )}
              </section>
            </TabsContent>
          </Tabs>
        </SheetContent>
      </Sheet>
      <AlertDialog
        open={!!confirmation}
        onOpenChange={(open) => {
          if (!open) setConfirmation(null);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{confirmation?.title}</AlertDialogTitle>
            <AlertDialogDescription>
              {confirmation?.description}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={() => void confirmation?.action()}>
              确认
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </SidebarProvider>
  );
}
