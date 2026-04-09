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

export interface SessionMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  delivery_status: string;
  created_at?: string;
}

export interface SessionAttachment {
  id?: number;
  file_name: string;
  caption: string;
  mime_type?: string;
  created_at?: string;
}

export interface SessionDocument {
  status: string;
  summary_text?: string;
  prd_markdown?: string;
}

export interface SessionPayload {
  token: string;
  status: SessionStatus;
  messages: SessionMessage[];
  attachments?: SessionAttachment[];
  current_stage: SessionStage;
  selected_template?: string | null;
  selected_style?: string | null;
  summary?: { payload: Record<string, unknown> };
  document?: SessionDocument;
  previous_summary?: string | null;
  queuePosition?: number;
  queue_position?: number;
  conversation_intent?: ConversationIntent;
  successor_token?: string | null;
  has_more?: boolean;
  oldest_message_id?: number | null;
  last_error?: string | null;
  completed_at?: string | null;
}

export interface MessagePayload {
  assistant_reply?: string;
  assistant_message?: string;
  session_status?: SessionStatus;
  queue_position?: number;
  message?: string;
  poll_after_ms?: number;
  conversation_intent?: ConversationIntent;
  typing_started?: boolean;
  successor_token?: string | null;
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
