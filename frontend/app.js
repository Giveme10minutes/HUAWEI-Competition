"use strict";

const LAST_CONVERSATION_KEY = "career-explorer:last-conversation";
const PLAN_FIELDS = [
  { key: "directions", id: "plan-directions" },
  { key: "gaps", id: "plan-gaps" },
  { key: "stage_goals", id: "plan-stage-goals" },
  { key: "actions", id: "plan-actions" },
];
const PLAN_SECTION_TITLES = {
  directions: "候选方向及依据",
  gaps: "差距与关键未知",
  stage_goals: "阶段目标",
  actions: "近期学习实践安排",
};
const STATUS_LABELS = {
  draft: "草稿",
  confirmed: "已确认",
  superseded: "历史版本",
};

const state = {
  meta: { agent_configured: false },
  conversations: [],
  deletedConversations: [],
  activeConversationId: null,
  conversationTitle: "新的对话",
  messages: [],
  profileItems: [],
  planData: null,
  busy: false,
  managingConversation: false,
  replyingMessageId: null,
  streamingText: "",
  streamFrame: null,
  editingProfileId: null,
  planEditorSource: null,
  planBusy: false,
  activeTab: "profile",
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(label, className, onClick) {
  const node = el("button", className, label);
  node.type = "button";
  node.addEventListener("click", onClick);
  return node;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

function inlineFormat(text) {
  return text
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function renderAssistantMarkdown(value) {
  const lines = escapeHtml(value).split(/\r?\n/);
  const output = [];
  let listTag = null;

  const closeList = () => {
    if (listTag) {
      output.push(`</${listTag}>`);
      listTag = null;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      continue;
    }
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    const bullet = line.match(/^[-*]\s+(.+)$/);
    const ordered = line.match(/^\d+[.、]\s*(.+)$/);
    const quote = line.match(/^&gt;\s?(.*)$/);

    if (heading) {
      closeList();
      output.push(`<h4>${inlineFormat(heading[2])}</h4>`);
    } else if (bullet) {
      if (listTag !== "ul") {
        closeList();
        output.push("<ul>");
        listTag = "ul";
      }
      output.push(`<li>${inlineFormat(bullet[1])}</li>`);
    } else if (ordered) {
      if (listTag !== "ol") {
        closeList();
        output.push("<ol>");
        listTag = "ol";
      }
      output.push(`<li>${inlineFormat(ordered[1])}</li>`);
    } else if (quote) {
      closeList();
      output.push(`<blockquote>${inlineFormat(quote[1])}</blockquote>`);
    } else {
      closeList();
      output.push(`<p>${inlineFormat(line)}</p>`);
    }
  }
  closeList();
  return output.join("");
}

const timeFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  month: "numeric",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

function formatTime(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return timeFormatter.format(date);
}

let toastTimer = null;

function toast(message, type = "info") {
  const node = $("#toast");
  node.textContent = message;
  node.className = `toast ${type}`;
  node.hidden = false;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    node.hidden = true;
  }, 4800);
}

function extractError(payload) {
  if (!payload) return "";
  const detail = payload.detail;
  if (typeof detail === "string") return detail;
  if (detail && typeof detail.message === "string") return detail.message;
  return "";
}

async function api(path, options = {}) {
  const method = options.method || "GET";
  const headers = { Accept: "application/json" };
  const request = { method, headers };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
    request.body = JSON.stringify(options.body);
  }

  let response;
  try {
    response = await fetch(path, request);
  } catch {
    throw new Error("网络连接失败，请确认本地服务仍在运行。");
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }
  if (!response.ok) {
    const message = extractError(payload) || `请求失败（${response.status}）。`;
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return payload;
}

function rememberConversation(id) {
  try {
    localStorage.setItem(LAST_CONVERSATION_KEY, id);
  } catch {
    /* localStorage may be unavailable; continuing is fine. */
  }
}

function rememberedConversation() {
  try {
    return localStorage.getItem(LAST_CONVERSATION_KEY);
  } catch {
    return null;
  }
}

function makeClientId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return `c-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
}

function resizeInput() {
  const input = $("#message-input");
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 150)}px`;
}

function scrollToBottom(force = true) {
  const scroller = $("#chat-scroll");
  if (force) {
    scroller.scrollTop = scroller.scrollHeight;
    return;
  }
  window.requestAnimationFrame(() => {
    scroller.scrollTop = scroller.scrollHeight;
  });
}

function updateComposerState() {
  const input = $("#message-input");
  const send = $("#send-button");
  const newButton = $("#new-conversation");
  const hint = $("#composer-hint");
  send.disabled = state.busy || !input.value.trim();
  newButton.disabled = state.busy;
  for (const control of $$(".conversation-actions button, #deleted-conversation-list button")) control.disabled = state.busy;
  if (state.busy) {
    hint.textContent = state.managingConversation ? "正在更新对话…" : state.replyingMessageId
      ? "助手正在回复，请稍候…"
      : "正在发送…";
  } else {
    hint.textContent = "Enter 发送 · Shift + Enter 换行";
  }
}

function renderChatHeader() {
  $("#chat-title").textContent = state.activeConversationId
    ? state.conversationTitle
    : "新的对话";
  $("#chat-subtitle").textContent = state.activeConversationId
    ? "对话会自动保存在本机，可以稍后继续。"
    : "不用先填完整资料，想到什么就说什么。";
}

function renderAgentNotice() {
  const notice = $("#agent-notice");
  if (state.meta.agent_configured) {
    notice.hidden = true;
    notice.textContent = "";
    return;
  }
  notice.hidden = false;
  notice.textContent =
    "在线助手尚未连接；对话、线索和规划仍会保存在本机。连好本地配置后可以再试。";
}

function renderConversations() {
  const list = $("#conversation-list");
  list.innerHTML = "";
  for (const conversation of state.conversations) {
    const item = el("li");
    const node = el("button", "conversation-item");
    node.type = "button";
    if (conversation.id === state.activeConversationId) {
      node.classList.add("active");
    }
    node.append(
      el("span", "conv-title", `${conversation.pinned ? "置顶 · " : ""}${conversation.title || "新的对话"}`),
      el(
        "span",
        "conv-preview",
        conversation.last_preview || "还没有消息"
      )
    );
    node.addEventListener("click", () => openConversation(conversation.id));
    item.append(node);
    const actions = el("div", "conversation-actions");
    const pin = button(conversation.pinned ? "取消置顶" : "置顶", "btn tiny", () => manageConversation(conversation, "pin"));
    const remove = button("删除", "btn tiny", () => manageConversation(conversation, "delete"));
    pin.disabled = remove.disabled = state.busy;
    actions.append(pin, remove);
    item.append(actions);
    list.append(item);
  }
  $("#conversation-empty").hidden = state.conversations.length > 0;
  const trash = $("#deleted-conversation-list");
  trash.innerHTML = "";
  for (const conversation of state.deletedConversations) {
    const item = el("li", "deleted-conversation");
    item.append(el("span", "conv-title", conversation.title));
    const restore = button("恢复", "btn tiny", () => manageConversation(conversation, "restore"));
    restore.disabled = state.busy;
    item.append(restore);
    trash.append(item);
  }
  if (!state.deletedConversations.length) trash.append(el("li", "hint", "暂无已删除对话。"));
}

function confirmConversationDelete(title) {
  const dialog = $("#delete-conversation-dialog");
  $("#delete-conversation-description").textContent = `将“${title}”移到已删除对话？`;
  dialog.returnValue = "cancel";
  return new Promise((resolve) => {
    dialog.addEventListener("close", () => resolve(dialog.returnValue === "delete"), {once: true});
    dialog.showModal();
  });
}

async function manageConversation(conversation, action) {
  if (state.busy) return;
  if (action === "delete" && !await confirmConversationDelete(conversation.title)) return;
  if (state.busy) return;
  state.busy = true;
  state.managingConversation = true;
  updateComposerState();
  try {
    const url = `/api/conversations/${encodeURIComponent(conversation.id)}`;
    if (action === "pin") {
      await api(url, {method: "PATCH", body: {pinned: !conversation.pinned}});
    } else if (action === "restore") {
      await api(`${url}/restore`, {method: "POST"});
    } else {
      await api(url, {method: "DELETE"});
      if (state.activeConversationId === conversation.id) {
        state.activeConversationId = null;
        state.conversationTitle = "新的对话";
        state.messages = [];
        state.replyingMessageId = null;
        rememberConversation("");
        renderChatHeader();
        renderMessages();
        updateComposerState();
      }
    }
    await refreshConversations();
    toast(action === "pin" ? (conversation.pinned ? "已取消置顶。" : "已置顶。") : action === "restore" ? "对话已恢复。" : "对话已移到已删除列表，可以恢复。");
  } catch (error) {
    toast(error.message, "error");
  } finally {
    state.busy = false;
    state.managingConversation = false;
    renderConversations();
    updateComposerState();
  }
}

function renderMessages() {
  const container = $("#messages");
  container.innerHTML = "";
  $("#welcome").hidden =
    state.messages.length > 0 || Boolean(state.replyingMessageId);
  for (const message of state.messages) {
    container.append(buildMessage(message));
  }
  if (state.replyingMessageId) {
    const article = el("article", `msg msg-assistant ${state.streamingText ? "streaming" : "typing"}`);
    const body = el("div", "msg-body");
    const bubble = el("div", "bubble reply-preview");
    if (state.streamingText) {
      bubble.innerHTML = renderAssistantMarkdown(state.streamingText);
    } else bubble.append(
      document.createTextNode("正在回复"),
      el("span", "typing-dot"),
      el("span", "typing-dot"),
      el("span", "typing-dot")
    );
    body.append(bubble);
    if (state.streamingText) body.append(el("div", "msg-meta", "正在生成，尚未保存完整回答…"));
    article.append(body);
    container.append(article);
  }
  renderChatHeader();
}

function updateStreamPreview(text) {
  state.streamingText += text;
  if (state.streamFrame !== null) return;
  state.streamFrame = window.requestAnimationFrame(() => {
    state.streamFrame = null;
    if (!state.replyingMessageId) return;
    const bubble = $("#messages .reply-preview");
    if (!bubble) return;
    const scroller = $("#chat-scroll");
    const follow = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 80;
    bubble.closest(".msg").classList.remove("typing");
    bubble.closest(".msg").classList.add("streaming");
    bubble.innerHTML = renderAssistantMarkdown(state.streamingText);
    if (follow) scroller.scrollTop = scroller.scrollHeight;
  });
}

function clearStreamPreview() {
  if (state.streamFrame !== null) window.cancelAnimationFrame(state.streamFrame);
  state.streamFrame = null;
  state.streamingText = "";
}

function buildMessage(message) {
  const article = el("article", `msg msg-${message.role}`);
  const body = el("div", "msg-body");
  const bubble = el("div", "bubble");

  if (message.role === "assistant") {
    bubble.innerHTML = renderAssistantMarkdown(message.content || "");
    body.append(bubble);
    body.append(
      el("div", "msg-meta", `助手 · ${formatTime(message.created_at)}`)
    );
    article.append(body);
    return article;
  }

  bubble.textContent = message.content;
  body.append(bubble);

  if (message.status === "failed") {
    const meta = el("div", "msg-meta msg-status-failed", "回复失败");
    body.append(meta);
    const errorBox = el("div", "msg-error");
    errorBox.append(
      document.createTextNode(message.error || "没有收到回复，请重试。")
    );
    const retry = button("重试", "btn tiny", () => retryMessage(message.id));
    retry.disabled = state.busy;
    errorBox.append(retry);
    body.append(errorBox);
  } else if (message.status === "pending") {
    const meta = el("div", "msg-meta");
    if (state.replyingMessageId === message.id) {
      meta.textContent = "助手正在回复…";
    } else {
      meta.textContent = "回复未完成";
      const retry = button("重试", "btn tiny", () => retryMessage(message.id));
      retry.disabled = state.busy;
      meta.append(" · ", retry);
    }
    body.append(meta);
  } else if (message.status === "sending") {
    body.append(el("div", "msg-meta", "发送中…"));
  } else {
    body.append(
      el("div", "msg-meta", formatTime(message.created_at))
    );
  }

  article.append(body);
  return article;
}

function replaceMessage(id, updated) {
  const index = state.messages.findIndex((message) => message.id === id);
  if (index >= 0) {
    state.messages[index] = updated;
  } else {
    state.messages.push(updated);
  }
}

async function refreshConversations() {
  try {
    const [data, deleted] = await Promise.all([api("/api/conversations"), api("/api/conversations?deleted=true")]);
    state.conversations = data.conversations;
    state.deletedConversations = deleted.conversations;
    renderConversations();
    const current = state.conversations.find(
      (conversation) => conversation.id === state.activeConversationId
    );
    if (current && current.title && current.title !== state.conversationTitle) {
      state.conversationTitle = current.title;
      renderChatHeader();
    }
  } catch {
    /* list refresh is helpful but not essential */
  }
}

async function openConversation(id, options = {}) {
  if (!options.initial && state.busy) {
    toast("助手正在回复，请稍候再切换对话。");
    return;
  }
  try {
    const data = await api(`/api/conversations/${encodeURIComponent(id)}`);
    state.activeConversationId = id;
    state.conversationTitle = data.conversation.title;
    state.messages = data.messages;
    state.replyingMessageId = null;
    rememberConversation(id);
    renderConversations();
    renderMessages();
    scrollToBottom(true);
    updateComposerState();
  } catch (error) {
    toast(error.message, "error");
  }
}

async function createConversation() {
  const data = await api("/api/conversations", { method: "POST" });
  state.conversations.push({
    ...data.conversation,
    message_count: 0,
    last_preview: "",
  });
  state.activeConversationId = data.conversation.id;
  state.conversationTitle = data.conversation.title;
  state.messages = [];
  state.replyingMessageId = null;
  rememberConversation(data.conversation.id);
  state.conversations.sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.updated_at.localeCompare(a.updated_at));
  renderConversations();
  renderMessages();
  updateComposerState();
  return data.conversation;
}

async function handleNewConversation() {
  if (state.busy) {
    toast("助手正在回复，请稍候再新建对话。");
    return;
  }
  try {
    await createConversation();
    $("#message-input").focus();
  } catch (error) {
    toast(error.message, "error");
  }
}

async function handleSend(event) {
  event.preventDefault();
  if (state.busy) return;
  const input = $("#message-input");
  const content = input.value.trim();
  if (!content) {
    input.focus();
    return;
  }

  state.busy = true;
  updateComposerState();
  let savedMessage = null;
  let localId = null;

  try {
    if (!state.activeConversationId) {
      await createConversation();
    }
    const conversationId = state.activeConversationId;
    const clientId = makeClientId();
    localId = `local-${clientId}`;
    state.messages.push({
      id: localId,
      role: "user",
      content,
      status: "sending",
      error: null,
      created_at: new Date().toISOString(),
    });
    input.value = "";
    resizeInput();
    renderMessages();
    scrollToBottom(true);
    updateComposerState();

    const result = await api(
      `/api/conversations/${encodeURIComponent(conversationId)}/messages`,
      {
        method: "POST",
        body: { content, client_id: clientId },
      }
    );
    savedMessage = result.message;
    replaceMessage(localId, savedMessage);
    renderMessages();
    scrollToBottom(true);
    await refreshConversations();
    await requestReply(savedMessage.id, conversationId);
  } catch (error) {
    if (!savedMessage) {
      if (localId) {
        state.messages = state.messages.filter(
          (message) => message.id !== localId
        );
      }
      if (!input.value.trim()) {
        input.value = content;
        resizeInput();
      }
      toast(error.message, "error");
    } else {
      toast(error.message, "error");
    }
    renderMessages();
  } finally {
    state.busy = false;
    state.replyingMessageId = null;
    updateComposerState();
    renderMessages();
    input.focus();
  }
}

async function requestReply(userMessageId, conversationId) {
  state.replyingMessageId = userMessageId;
  state.streamingText = "";
  const current = state.messages.find(
    (message) => message.id === userMessageId
  );
  if (current) {
    current.status = "pending";
    current.error = null;
  }
  renderMessages();
  scrollToBottom(false);
  updateComposerState();

  try {
    const data = await readReplyStream(userMessageId, updateStreamPreview);
    clearStreamPreview();
    state.replyingMessageId = null;
    if (state.activeConversationId === conversationId) {
      replaceMessage(userMessageId, data.user_message);
      if (!state.messages.some((message) => message.id === data.reply.id)) {
        state.messages.push(data.reply);
      }
      renderMessages();
      scrollToBottom(true);
    }
    await refreshConversations();
  } catch (error) {
    clearStreamPreview();
    if (state.activeConversationId === conversationId) {
      await reloadConversationMessages(conversationId);
    }
    toast(error.message, "error");
  } finally {
    clearStreamPreview();
    state.replyingMessageId = null;
    if (state.activeConversationId === conversationId) {
      renderMessages();
      updateComposerState();
    }
  }
}

async function readReplyStream(messageId, onDelta) {
  const response = await fetch(`/api/messages/${encodeURIComponent(messageId)}/stream`, {method: "POST"});
  if (!response.ok || !response.body) throw new Error("无法读取回复，请稍后重试。");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let complete = null;
  try {
    while (true) {
      const {value, done} = await reader.read();
      buffer += decoder.decode(value, {stream: !done});
      let boundary;
      while ((boundary = buffer.indexOf("\n\n")) >= 0) {
        const frame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const data = frame.split("\n").filter(line => line.startsWith("data:")).map(line => line.slice(5).trimStart()).join("\n");
        if (!data) continue;
        const event = JSON.parse(data);
        if (event.type === "error") throw new Error(event.message || "回复中断，请重试。");
        if (event.type === "delta" && typeof event.text === "string") onDelta(event.text);
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

async function reloadConversationMessages(conversationId) {
  try {
    const data = await api(
      `/api/conversations/${encodeURIComponent(conversationId)}`
    );
    state.messages = data.messages;
    state.conversationTitle = data.conversation.title;
    renderChatHeader();
    renderMessages();
    scrollToBottom(false);
  } catch {
    /* keep whatever is on screen */
  }
}

async function retryMessage(messageId) {
  if (state.busy || !state.activeConversationId) return;
  state.busy = true;
  updateComposerState();
  try {
    await requestReply(messageId, state.activeConversationId);
  } finally {
    state.busy = false;
    state.replyingMessageId = null;
    updateComposerState();
    renderMessages();
  }
}

function badge(text, extra = "") {
  return el("span", `badge ${extra}`.trim(), text);
}

function renderProfile() {
  const items = state.profileItems;
  const pending = items.filter((item) => item.status === "unconfirmed").length;
  const confirmed = items.length - pending;
  $("#profile-count").textContent = items.length
    ? `${pending} 待确认 · ${confirmed} 已确认`
    : "";
  $("#profile-empty").hidden = items.length > 0;

  const list = $("#profile-list");
  list.innerHTML = "";
  for (const item of items) {
    list.append(buildProfileCard(item));
  }
}

function buildProfileCard(item) {
  const card = el("div", "profile-item");
  const top = el("div", "profile-item-top");
  top.append(badge(item.category));
  top.append(
    badge(
      item.source === "assistant_inferred" ? "助手推断" : "我的自述",
      item.source === "assistant_inferred" ? "inferred" : ""
    )
  );
  top.append(
    badge(
      item.status === "confirmed" ? "已确认" : "待确认",
      item.status === "confirmed" ? "confirmed" : "unconfirmed"
    )
  );
  card.append(top);

  if (state.editingProfileId === item.id) {
    card.append(buildProfileEditForm(item));
    return card;
  }

  card.append(el("p", "profile-content", item.content));

  if (item.status === "unconfirmed") {
    card.append(
      el(
        "p",
        "item-hint",
        item.source === "assistant_inferred"
          ? "这是助手提出的推断，尚未由你确认；确认前不会作为档案。"
          : "确认后才会作为已确认的线索。"
      )
    );
  } else if (item.source === "assistant_inferred") {
    card.append(el("p", "item-hint", "最初由助手提出，已由你确认。"));
  } else {
    card.append(el("p", "item-hint", "已确认的线索；修改后需要重新确认。"));
  }

  const actions = el("div", "item-actions");
  if (item.status === "unconfirmed") {
    actions.append(
      button("确认", "btn tiny primary", () => confirmProfileItem(item.id))
    );
  }
  actions.append(
    button("修改", "btn tiny", () => {
      state.editingProfileId = item.id;
      renderProfile();
    })
  );
  actions.append(
    button("删除", "btn tiny danger", () => deleteProfileItem(item.id))
  );
  card.append(actions);
  return card;
}

function buildSelect(options, value) {
  const select = el("select");
  for (const option of options) {
    const node = el("option", "", option);
    node.value = option;
    if (option === value) node.selected = true;
    select.append(node);
  }
  select.value = value;
  return select;
}

function buildProfileEditForm(item) {
  const form = el("form", "profile-edit");
  form.append(el("label", "", "类别"));
  const category = buildSelect(
    [
      "兴趣与偏好",
      "经历与做过的事",
      "专业与年级",
      "技能与能力（自述）",
      "现实约束（时间/地点/预算）",
      "目标与待探索问题",
      "其他",
    ],
    item.category
  );
  form.append(category);

  form.append(el("label", "", "内容"));
  const content = el("textarea");
  content.rows = 3;
  content.maxLength = 2000;
  content.value = item.content;
  form.append(content);

  form.append(el("label", "", "来源"));
  const source = buildSelect(
    ["self_reported", "assistant_inferred"],
    item.source
  );
  source.options[0].textContent = "我的自述";
  source.options[1].textContent = "助手推断（待核实）";
  form.append(source);

  const actions = el("div", "form-actions");
  const save = button("保存修改", "btn primary tiny", () => {
    form.requestSubmit();
  });
  const cancel = button("取消", "btn tiny", () => {
    state.editingProfileId = null;
    renderProfile();
  });
  actions.append(save, cancel);
  form.append(actions);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    saveProfileEdit(item.id, {
      category: category.value,
      content: content.value.trim(),
      source: source.value,
    });
  });
  return form;
}

async function loadProfile() {
  const data = await api("/api/profile");
  state.profileItems = data.items;
  renderProfile();
}

async function handleProfileAdd(event) {
  event.preventDefault();
  const contentField = $("#profile-content");
  const content = contentField.value.trim();
  if (!content) {
    toast("请先写下线索内容。", "error");
    contentField.focus();
    return;
  }
  const submit = $("#profile-form button[type='submit']");
  submit.disabled = true;
  try {
    await api("/api/profile", {
      method: "POST",
      body: {
        category: $("#profile-category").value,
        content,
        source: $("#profile-source").value,
      },
    });
    contentField.value = "";
    await loadProfile();
    toast("已添加，请在卡片上确认。", "success");
  } catch (error) {
    toast(error.message, "error");
  } finally {
    submit.disabled = false;
  }
}

async function confirmProfileItem(id) {
  try {
    await api(`/api/profile/${encodeURIComponent(id)}/confirm`, {
      method: "POST",
    });
    await loadProfile();
    toast("已确认这条线索。", "success");
  } catch (error) {
    toast(error.message, "error");
  }
}

async function saveProfileEdit(id, fields) {
  if (!fields.content) {
    toast("线索内容不能为空。", "error");
    return;
  }
  try {
    await api(`/api/profile/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: fields,
    });
    state.editingProfileId = null;
    await loadProfile();
    toast("已修改，请重新确认。", "success");
  } catch (error) {
    toast(error.message, "error");
  }
}

async function deleteProfileItem(id) {
  if (!window.confirm("删除这条线索？删除后无法恢复。")) return;
  try {
    await api(`/api/profile/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (state.editingProfileId === id) state.editingProfileId = null;
    await loadProfile();
    toast("已删除这条线索。", "success");
  } catch (error) {
    toast(error.message, "error");
  }
}

function planSections(version) {
  const fragment = document.createDocumentFragment();
  let hasContent = false;
  for (const field of PLAN_FIELDS) {
    const value = (version[field.key] || "").trim();
    if (!value) continue;
    hasContent = true;
    const section = el("div", "plan-section");
    section.append(el("h4", "", PLAN_SECTION_TITLES[field.key]));
    section.append(el("p", "", value));
    fragment.append(section);
  }
  if (!hasContent) {
    fragment.append(el("p", "empty-box", "这一版还没有填写内容。"));
  }
  return fragment;
}

function renderPlan() {
  const data = state.planData;
  const confirmed = data ? data.confirmed : null;
  const draft = data ? data.draft : null;
  const versions = data ? data.versions : [];

  const status = $("#plan-status");
  if (draft) {
    // A draft is the thing the user is working on, so surface it before the
    // last confirmed version (which stays visible in the card below).
    status.textContent = `第 ${draft.version_no} 版草稿待确认`;
  } else if (confirmed) {
    status.textContent = `第 ${confirmed.version_no} 版已确认`;
  } else {
    status.textContent = "还没有规划";
  }

  const box = $("#plan-confirmed");
  box.innerHTML = "";
  box.append(el("h3", "", "当前已确认的规划"));
  if (confirmed) {
    box.append(
      el(
        "p",
        "item-hint",
        `第 ${confirmed.version_no} 版 · 确认于 ${formatTime(confirmed.confirmed_at)}`
      )
    );
    box.append(planSections(confirmed));
    if (!draft) {
      const base = button("在此基础上修改", "btn tiny", useConfirmedAsBase);
      const actions = el("div", "form-actions");
      actions.append(base);
      box.append(actions);
    } else {
      box.append(
        el("p", "item-hint", "当前还有一份草稿，确认后会替换为新的已确认版本。")
      );
    }
  } else {
    box.append(el("p", "empty-box", "还没有已确认的规划。"));
  }

  const history = $("#plan-history");
  history.innerHTML = "";
  for (const version of versions) {
    history.append(buildHistoryItem(version));
  }
  $("#plan-history-empty").hidden = versions.length > 0;
}

function buildHistoryItem(version) {
  const item = el("div", "history-item");
  const head = el("div", "history-head");
  const title = el("span", "", `第 ${version.version_no} 版`);
  const status = badge(
    STATUS_LABELS[version.status] || version.status,
    version.status === "confirmed"
      ? "confirmed"
      : version.status === "draft"
        ? "unconfirmed"
        : ""
  );
  head.append(title, status);
  item.append(head);

  const details = el("details");
  const summary = el("summary", "", "查看内容");
  details.append(summary);
  details.append(planSections(version));
  item.append(details);

  const note = el("p", "history-note");
  const time =
    version.status === "confirmed"
      ? `确认于 ${formatTime(version.confirmed_at)}`
      : `更新于 ${formatTime(version.updated_at)}`;
  note.textContent = version.change_note
    ? `${time} · 修改说明：${version.change_note}`
    : time;
  item.append(note);
  return item;
}

function fillPlanEditor(version, source) {
  for (const field of PLAN_FIELDS) {
    $(`#${field.id}`).value = version ? version[field.key] || "" : "";
  }
  $("#plan-note").value = version ? version.change_note || "" : "";
  state.planEditorSource = source;
}

function setPlanHint(text) {
  $("#plan-editor-hint").textContent = text;
}

function syncPlanEditor() {
  const draft = state.planData ? state.planData.draft : null;
  if (draft) {
    fillPlanEditor(draft, { type: "draft", id: draft.id });
    setPlanHint(`正在编辑第 ${draft.version_no} 版草稿，尚未确认。`);
  } else {
    fillPlanEditor(null, null);
    setPlanHint("可以只写一部分；保存后仍是草稿，确认后才会成为当前规划。");
  }
}

function planEditorHasText() {
  return PLAN_FIELDS.some((field) => $(`#${field.id}`).value.trim());
}

function collectPlanContent() {
  const body = {};
  for (const field of PLAN_FIELDS) {
    body[field.key] = $(`#${field.id}`).value.trim();
  }
  body.change_note = $("#plan-note").value.trim();
  return body;
}

function hasAnyPlanText(body) {
  return PLAN_FIELDS.some((field) => body[field.key]);
}

function useConfirmedAsBase() {
  const confirmed = state.planData ? state.planData.confirmed : null;
  if (!confirmed) return;
  if (
    planEditorHasText() &&
    !window.confirm("编辑区已有内容，要用已确认版本替换吗？")
  ) {
    return;
  }
  fillPlanEditor(confirmed, null);
  setPlanHint("正在已确认版本基础上编辑；保存会生成新的草稿，确认后成为新版本。");
  switchTab("plan");
  $("#plan-directions").focus();
}

async function loadPlan() {
  const data = await api("/api/plan");
  state.planData = data;
  renderPlan();
}

async function savePlan(options = {}) {
  const body = collectPlanContent();
  if (!hasAnyPlanText(body)) {
    toast("至少填写一项规划内容再保存。", "error");
    return null;
  }
  try {
    const source = state.planEditorSource;
    const result =
      source && source.type === "draft"
        ? await api(`/api/plan/versions/${encodeURIComponent(source.id)}`, {
            method: "PUT",
            body,
          })
        : await api("/api/plan/versions", { method: "POST", body });
    state.planEditorSource = { type: "draft", id: result.version.id };
    fillPlanEditor(result.version, state.planEditorSource);
    setPlanHint(`第 ${result.version.version_no} 版草稿已保存，尚未确认。`);
    try {
      await loadPlan();
    } catch {
      /* the draft itself is saved; the list can refresh later */
    }
    if (!options.quiet) {
      toast("草稿已保存。", "success");
    }
    return result.version;
  } catch (error) {
    toast(error.message, "error");
    if (error.status === 409) {
      try {
        await loadPlan();
        syncPlanEditor();
      } catch {
        /* keep the editor as is */
      }
    }
    return null;
  }
}

async function confirmPlan() {
  const body = collectPlanContent();
  if (!hasAnyPlanText(body)) {
    toast("至少填写一项规划内容再确认。", "error");
    return;
  }
  if (
    !window.confirm(
      "确认后，这一版会成为当前规划；以后修改会保留历史版本。\n\n确认这一版吗？"
    )
  ) {
    return;
  }
  const saved = await savePlan({ quiet: true });
  if (!saved) return;
  try {
    const result = await api(
      `/api/plan/versions/${encodeURIComponent(saved.id)}/confirm`,
      { method: "POST" }
    );
    await loadPlan();
    fillPlanEditor(null, null);
    setPlanHint("这一版已确认。修改上方编辑区可以继续形成新的草稿。");
    toast(`已确认第 ${result.version.version_no} 版规划。`, "success");
  } catch (error) {
    toast(error.message, "error");
  }
}

async function withPlanBusy(task) {
  if (state.planBusy) return;
  state.planBusy = true;
  $("#plan-save").disabled = true;
  $("#plan-confirm").disabled = true;
  try {
    await task();
  } finally {
    state.planBusy = false;
    $("#plan-save").disabled = false;
    $("#plan-confirm").disabled = false;
  }
}

function switchTab(name) {
  state.activeTab = name;
  for (const tab of $$(".tab")) {
    const active = tab.dataset.tab === name;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  }
  $("#profile-panel").hidden = name !== "profile";
  $("#plan-panel").hidden = name !== "plan";
}

function bindEvents() {
  $("#toggle-history").addEventListener("click", (event) => {
    const open = $(".sidebar").classList.toggle("history-open");
    event.currentTarget.setAttribute("aria-expanded", String(open));
  });
  for (const trigger of $$("[data-open-panel]")) {
    trigger.addEventListener("click", () => {
      switchTab(trigger.dataset.openPanel);
      $("#context-dialog").showModal();
    });
  }
  $("#close-context").addEventListener("click", () => $("#context-dialog").close());
  $("#context-dialog").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) {
      const rect = event.currentTarget.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) event.currentTarget.close();
    }
  });
  $("#composer").addEventListener("submit", handleSend);
  $("#message-input").addEventListener("input", () => {
    resizeInput();
    updateComposerState();
  });
  $("#message-input").addEventListener("keydown", (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.isComposing &&
      event.keyCode !== 229
    ) {
      event.preventDefault();
      $("#composer").requestSubmit();
    }
  });
  $("#new-conversation").addEventListener("click", handleNewConversation);
  for (const chip of $$(".chip")) {
    chip.addEventListener("click", () => {
      const input = $("#message-input");
      input.value = chip.dataset.prompt || chip.textContent.trim();
      resizeInput();
      updateComposerState();
      input.focus();
    });
  }
  for (const tab of $$(".tab")) {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
  }
  $("#profile-form").addEventListener("submit", handleProfileAdd);
  $("#plan-save").addEventListener("click", () =>
    withPlanBusy(() => savePlan())
  );
  $("#plan-confirm").addEventListener("click", () =>
    withPlanBusy(confirmPlan)
  );
}

async function init() {
  bindEvents();
  resizeInput();
  updateComposerState();

  const [metaResult, conversationsResult, profileResult, planResult] =
    await Promise.allSettled([
      api("/api/meta"),
      api("/api/conversations"),
      api("/api/profile"),
      api("/api/plan"),
    ]);

  if (metaResult.status === "fulfilled") {
    state.meta = metaResult.value;
  } else {
    state.meta = { agent_configured: false };
    toast("无法读取服务状态，请确认本地服务仍在运行。", "error");
  }
  renderAgentNotice();

  if (conversationsResult.status === "fulfilled") {
    state.conversations = conversationsResult.value.conversations;
  } else {
    toast("读取对话列表失败。", "error");
  }
  renderConversations();

  if (profileResult.status === "fulfilled") {
    state.profileItems = profileResult.value.items;
  } else {
    toast("读取个人线索失败。", "error");
  }
  renderProfile();

  if (planResult.status === "fulfilled") {
    state.planData = planResult.value;
    renderPlan();
    syncPlanEditor();
  } else {
    toast("读取职业规划失败。", "error");
    setPlanHint("填写后可以保存草稿。");
  }

  if (state.conversations.length) {
    const remembered = rememberedConversation();
    const preferred =
      state.conversations.find(
        (conversation) => conversation.id === remembered
      ) || state.conversations[0];
    await openConversation(preferred.id, { initial: true });
  } else {
    renderMessages();
  }

  updateComposerState();
  await refreshConversations();
  $("#message-input").focus();
}

document.addEventListener("DOMContentLoaded", init);
