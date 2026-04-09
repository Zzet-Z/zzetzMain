import type {
  AttachmentPayload,
  DocumentPayload,
  MessagePayload,
  SessionMessage,
  SessionPayload,
} from "./types";

const viteEnv = (import.meta as ImportMeta & { env?: Record<string, string> }).env;
const API_BASE = `${viteEnv?.VITE_API_BASE_URL ?? "http://127.0.0.1:5000"}/api`;

async function parseJson<T>(response: Response, errorMessage: string): Promise<T> {
  if (!response.ok) {
    throw new Error(errorMessage);
  }
  return (await response.json()) as T;
}

export async function getSession(token: string): Promise<SessionPayload> {
  const response = await fetch(`${API_BASE}/sessions/${token}`);
  const payload = await parseJson<SessionPayload>(response, "读取会话失败");
  return {
    ...payload,
    queuePosition: payload.queuePosition ?? payload.queue_position,
  };
}

export async function getSessionMessages(
  token: string,
  beforeId: number,
  limit = 50,
): Promise<SessionMessage[]> {
  const response = await fetch(
    `${API_BASE}/sessions/${token}/messages?before_id=${beforeId}&limit=${limit}`,
  );
  const payload = await parseJson<{ messages?: SessionMessage[] } | SessionMessage[]>(
    response,
    "加载历史消息失败",
  );

  return Array.isArray(payload) ? payload : (payload.messages ?? []);
}

export async function sendMessage(
  token: string,
  payload: Record<string, unknown>,
): Promise<MessagePayload> {
  const response = await fetch(`${API_BASE}/sessions/${token}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJson<MessagePayload>(response, "发送消息失败");
}

export async function uploadAttachment(
  token: string,
  file: File,
  caption: string,
): Promise<AttachmentPayload> {
  const form = new FormData();
  form.append("file", file);
  form.append("caption", caption);
  const response = await fetch(`${API_BASE}/sessions/${token}/attachments`, {
    method: "POST",
    body: form,
  });
  return parseJson<AttachmentPayload>(response, "上传附件失败");
}

export async function getDocument(token: string): Promise<DocumentPayload> {
  const response = await fetch(`${API_BASE}/sessions/${token}/document`);
  return parseJson<DocumentPayload>(response, "读取文档失败");
}
