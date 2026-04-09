import type {
  AdminTokenListResponse,
  AdminTokenDetail,
  AdminTokenListItem,
  AttachmentPayload,
  CreatedAdminTokenPayload,
  CreateAdminTokenPayload,
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

function createAdminHeaders(adminToken: string, withJson = false): HeadersInit {
  return {
    Authorization: `Bearer ${adminToken}`,
    ...(withJson ? { "Content-Type": "application/json" } : {}),
  };
}

export async function listAdminTokens(adminToken: string): Promise<AdminTokenListItem[]> {
  const response = await fetch(`${API_BASE}/admin/tokens`, {
    headers: createAdminHeaders(adminToken),
  });
  const payload = await parseJson<AdminTokenListResponse>(response, "读取 token 列表失败");
  return payload.items;
}

export async function createAdminToken(
  adminToken: string,
  payload: CreateAdminTokenPayload,
): Promise<CreatedAdminTokenPayload> {
  const response = await fetch(`${API_BASE}/admin/tokens`, {
    method: "POST",
    headers: createAdminHeaders(adminToken, true),
    body: JSON.stringify(payload),
  });
  return parseJson<CreatedAdminTokenPayload>(response, "签发 token 失败");
}

export async function getAdminTokenDetail(
  adminToken: string,
  token: string,
): Promise<AdminTokenDetail> {
  const response = await fetch(`${API_BASE}/admin/tokens/${token}`, {
    headers: createAdminHeaders(adminToken),
  });
  const payload = await parseJson<AdminTokenDetail>(response, "读取 token 详情失败");
  return {
    ...payload,
    document_status: payload.document?.status ?? payload.document_status ?? null,
    summary_text: payload.summary_text ?? payload.previous_summary ?? payload.document?.summary_text ?? null,
    prd_markdown: payload.prd_markdown ?? payload.document?.prd_markdown ?? null,
  };
}

export async function revokeAdminToken(
  adminToken: string,
  token: string,
): Promise<AdminTokenDetail> {
  const response = await fetch(`${API_BASE}/admin/tokens/${token}/revoke`, {
    method: "POST",
    headers: createAdminHeaders(adminToken),
  });
  const payload = await parseJson<AdminTokenDetail>(response, "撤销 token 失败");
  return {
    ...payload,
    document_status: payload.document?.status ?? payload.document_status ?? null,
    summary_text: payload.summary_text ?? payload.previous_summary ?? payload.document?.summary_text ?? null,
    prd_markdown: payload.prd_markdown ?? payload.document?.prd_markdown ?? null,
  };
}
