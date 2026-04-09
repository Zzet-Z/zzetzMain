export type ConversationIntent = "continue" | "ready_to_generate";

export type SessionStage =
  | "template"
  | "style"
  | "positioning"
  | "content"
  | "features"
  | "generate";

export type SessionStatus =
  | "draft"
  | "queued"
  | "active"
  | "in_progress"
  | "generating_document"
  | "completed"
  | "failed";

export interface SessionSummary {
  payload: Record<string, unknown>;
}

export interface SessionDocument {
  status: string;
  summary_text?: string;
  prd_markdown?: string;
}

export interface SessionPayload {
  token: string;
  status: SessionStatus;
  current_stage: SessionStage;
  selected_template: string | null;
  selected_style: string | null;
  summary?: SessionSummary;
  document?: SessionDocument;
  queuePosition?: number;
  locale?: string;
  conversation_intent?: ConversationIntent;
  successor_token?: string | null;
  has_more?: boolean;
  oldest_message_id?: number;
}

export interface MessagePayload {
  assistant_reply?: string;
  current_stage?: SessionStage;
  session_status?: SessionStatus;
  queue_position?: number;
  message?: string;
  poll_after_ms?: number;
  conversation_intent?: ConversationIntent;
}

export interface AttachmentPayload {
  file_name: string;
  caption: string;
  file_path?: string;
}

export interface DocumentPayload {
  status: string;
  summary_text: string;
  prd_markdown: string;
}
