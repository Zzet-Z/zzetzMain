import type {
  AttachmentPayload,
  DocumentPayload,
  MessagePayload,
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

export async function createSession(): Promise<SessionPayload> {
  const response = await fetch(`${API_BASE}/sessions`, { method: "POST" });
  return parseJson<SessionPayload>(response, "创建会话失败");
}

export async function getSession(token: string): Promise<SessionPayload> {
  const response = await fetch(`${API_BASE}/sessions/${token}`);
  return parseJson<SessionPayload>(response, "读取会话失败");
}

export async function updateSession(
  token: string,
  payload: Record<string, unknown>,
): Promise<SessionPayload> {
  const response = await fetch(`${API_BASE}/sessions/${token}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJson<SessionPayload>(response, "更新会话失败");
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
