import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ChatPanel } from "../components/intake/chat-panel";
import {
  getDocument,
  getSession,
  getSessionMessages,
  sendMessage,
  uploadAttachment,
} from "../lib/api";
import type {
  AttachmentPayload,
  DocumentPayload,
  SessionAttachment,
  SessionMessage,
  SessionPayload,
  SessionStatus,
} from "../lib/types";

function createInitialSession(token: string, status: SessionStatus, queuePosition?: number): SessionPayload {
  return {
    token,
    status,
    messages: [],
    attachments: [],
    current_stage: "template",
    document: { status: "pending" },
    queuePosition,
    queue_position: queuePosition,
    has_more: false,
    oldest_message_id: null,
    successor_token: null,
  };
}

export function SessionPage({
  initialState,
}: {
  initialState?: { status: SessionStatus | "awaiting_user" | "expired"; queuePosition?: number };
}) {
  const navigate = useNavigate();
  const { token = "" } = useParams();
  const [session, setSession] = useState<SessionPayload | null>(
    initialState
      ? createInitialSession(
          token,
          initialState.status as SessionStatus,
          initialState.queuePosition,
        )
      : null,
  );
  const [documentState, setDocumentState] = useState<DocumentPayload | null>(null);
  const [messages, setMessages] = useState<SessionMessage[]>(session?.messages ?? []);
  const [attachments, setAttachments] = useState<SessionAttachment[]>(session?.attachments ?? []);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const sessionStatus = session?.status as string | undefined;

  const composerDisabled =
    sessionStatus === "completed" ||
    sessionStatus === "expired" ||
    sessionStatus === "failed" ||
    sessionStatus === "generating_document";

  useEffect(() => {
    setMessages(session?.messages ?? []);
    setAttachments(session?.attachments ?? []);
  }, [session?.attachments, session?.messages]);

  useEffect(() => {
    if (session?.status === "completed") {
      setShowCompletionModal(true);
    }
  }, [session?.status]);

  useEffect(() => {
    if (!token || initialState?.status === "queued") {
      return;
    }

    let cancelled = false;

    async function load() {
      try {
        const payload = await getSession(token);
        if (cancelled) {
          return;
        }

        setSession(payload);
        setMessages(payload.messages ?? []);
        setAttachments(payload.attachments ?? []);
        setErrorMessage("");
      } catch (_error) {
        if (!cancelled) {
          setErrorMessage("暂时无法读取当前会话，请稍后刷新重试。");
        }
      }
    }

    void load();
    const timer = window.setInterval(() => void load(), 3000);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [initialState?.status, token]);

  useEffect(() => {
    if (!token || (session?.status !== "generating_document" && session?.status !== "completed")) {
      return;
    }

    let cancelled = false;

    async function pollDocument() {
      try {
        const payload = await getDocument(token);
        if (!cancelled) {
          setDocumentState(payload);
        }
      } catch (_error) {
        if (!cancelled) {
          setErrorMessage("文档状态暂时不可用，请稍后重试。");
        }
      }
    }

    void pollDocument();
    const timer = window.setInterval(() => void pollDocument(), 5000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [session?.status, token]);

  async function handleSend() {
    if (!token || !draft.trim() || isSending || composerDisabled) {
      return;
    }

    const userContent = draft.trim();
    const optimisticUserMessage: SessionMessage = {
      id: Date.now(),
      role: "user",
      content: userContent,
      delivery_status: "final",
    };

    setMessages((current) => [...current, optimisticUserMessage]);
    setDraft("");
    setIsSending(true);

    try {
      const payload = await sendMessage(token, { content: userContent });
      const assistantContent = payload.assistant_message ?? payload.assistant_reply ?? payload.message;

      if (assistantContent) {
        setMessages((current) => [
          ...current,
          {
            id: Date.now() + 1,
            role: "assistant",
            content: assistantContent,
            delivery_status: "final",
          },
        ]);
      }

      setSession((current) =>
        current
          ? {
              ...current,
              status: payload.session_status ?? current.status,
              queuePosition: payload.queue_position ?? current.queuePosition,
              queue_position: payload.queue_position ?? current.queue_position,
              conversation_intent: payload.conversation_intent ?? current.conversation_intent,
              successor_token: payload.successor_token ?? current.successor_token,
            }
          : current,
      );
      setErrorMessage("");
    } catch (_error) {
      setMessages((current) => current.filter((message) => message.id !== optimisticUserMessage.id));
      setDraft(userContent);
      setErrorMessage("暂时无法继续整理需求，请稍后重试。");
    } finally {
      setIsSending(false);
    }
  }

  async function handleConfirmGenerate() {
    if (!token || isSending || composerDisabled) {
      return;
    }

    setIsSending(true);
    try {
      const payload = await sendMessage(token, {
        content: "请开始生成最终需求文档",
        confirm_generate: true,
      });
      const assistantContent = payload.assistant_message ?? payload.assistant_reply ?? payload.message;
      if (assistantContent) {
        setMessages((current) => [
          ...current,
          {
            id: Date.now(),
            role: "assistant",
            content: assistantContent,
            delivery_status: "final",
          },
        ]);
      }
      setSession((current) =>
        current
          ? {
              ...current,
              status: payload.session_status ?? current.status,
              conversation_intent: payload.conversation_intent ?? "continue",
            }
          : current,
      );
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("最终文档生成请求失败，请稍后重试。");
    } finally {
      setIsSending(false);
    }
  }

  async function handleUpload(file: File) {
    if (!token || composerDisabled) {
      return;
    }

    try {
      const payload: AttachmentPayload = await uploadAttachment(token, file, "参考图片");
      setAttachments((current) => [...current, payload]);
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("图片上传失败，请换一张图片后重试。");
    }
  }

  async function handleLoadMore() {
    if (!token || !session?.oldest_message_id || isLoadingMore) {
      return;
    }

    setIsLoadingMore(true);
    try {
      const olderMessages = await getSessionMessages(token, session.oldest_message_id);
      setMessages((current) => [...olderMessages, ...current]);
      setSession((current) =>
        current
          ? {
              ...current,
              has_more: olderMessages.length >= 50,
              oldest_message_id: olderMessages[0]?.id ?? current.oldest_message_id,
            }
          : current,
      );
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("加载历史消息失败，请稍后再试。");
    } finally {
      setIsLoadingMore(false);
    }
  }

  if (session?.status === "queued") {
    const queuePosition = session.queuePosition ?? session.queue_position ?? 0;
    return (
      <main className="px-4 py-6 text-white">
        <p>当前正在为其他用户整理网站需求，你已进入等待队列。</p>
        <p>你前面还有 {queuePosition} 人。</p>
      </main>
    );
  }

  if (!session) {
    return <main className="px-4 py-6 text-white">正在加载...</main>;
  }

  const helperText =
    sessionStatus === "generating_document"
      ? "系统正在整理最终需求文档，暂时不能继续输入。"
      : sessionStatus === "completed"
        ? "本轮整理已经完成，可以使用后续修订 token 继续修改。"
        : sessionStatus === "expired"
          ? "这个整理链接已经失效，请联系管理员获取新的入口。"
          : sessionStatus === "failed"
            ? session.last_error ?? "本轮整理失败，请联系管理员重新签发 token。"
            : undefined;

  return (
    <main className="min-h-screen bg-[var(--color-bg)] text-white">
      {showCompletionModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/72 px-4">
          <div className="w-full max-w-[420px] rounded-[28px] border border-white/10 bg-[var(--color-surface-1)] px-6 py-6 shadow-[0_24px_80px_rgba(0,0,0,0.36)]">
            <p className="text-[12px] uppercase tracking-[0.22em] text-white/40">需求已确认</p>
            <h2 className="mt-3 text-[28px] font-semibold leading-[1.15] text-white">
              您的网站将于3-24小时内上线
            </h2>
            <p className="mt-4 text-[15px] leading-[1.7] text-white/68">
              当前需求文档已经确认完成。点击确认后将返回首页，后续如需继续调整，请使用后续修订 Token。
            </p>
            <div className="mt-6 flex justify-end">
              <button
                className="rounded-full bg-white px-5 py-2.5 text-sm text-black"
                onClick={() => {
                  setShowCompletionModal(false);
                  navigate("/");
                }}
                type="button"
              >
                确认
              </button>
            </div>
          </div>
        </div>
      ) : null}

      <div className="mx-auto max-w-[980px] px-4 py-4 sm:px-6">
        <div className="mb-4 rounded-[24px] border border-white/10 bg-black/45 px-5 py-4 backdrop-blur-xl sm:px-6">
          <p className="text-[12px] uppercase tracking-[0.22em] text-white/40">Chat-First Session</p>
          <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-[21px] font-semibold leading-[1.2] text-white">受控需求对话</h2>
              <p className="mt-1 text-[14px] leading-[1.6] text-white/56">
                当前状态：{session.status}
              </p>
            </div>
            {session.successor_token ? (
              <p className="text-[14px] leading-[1.6] text-white/68">
                后续修订 Token：{session.successor_token}
              </p>
            ) : null}
          </div>
          {session.previous_summary ? (
            <div className="mt-4 rounded-[20px] border border-white/10 bg-white/5 px-4 py-3 text-[14px] leading-[1.7] text-white/74">
              上一版摘要：{session.previous_summary}
            </div>
          ) : null}
          {documentState?.summary_text ? (
            <div className="mt-4 rounded-[20px] border border-white/10 bg-white/5 px-4 py-3 text-[14px] leading-[1.7] text-white/74">
              {documentState.summary_text}
            </div>
          ) : null}
          {errorMessage ? (
            <div className="mt-4 rounded-[20px] border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/10 px-4 py-3 text-sm text-white/86">
              {errorMessage}
            </div>
          ) : null}
        </div>

        <ChatPanel
          attachments={attachments}
          composerDisabled={Boolean(composerDisabled)}
          conversationIntent={session.conversation_intent}
          draft={draft}
          hasMore={Boolean(session.has_more)}
          helperText={helperText}
          isLoadingMore={isLoadingMore}
          isSending={isSending}
          messages={messages}
          onConfirmGenerate={() => void handleConfirmGenerate()}
          onDraftChange={setDraft}
          onLoadMore={() => void handleLoadMore()}
          onSend={() => void handleSend()}
          onUpload={(file) => void handleUpload(file)}
        />
      </div>
    </main>
  );
}
