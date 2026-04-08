import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { AttachmentPanel } from "../components/intake/attachment-panel";
import { ChatPanel } from "../components/intake/chat-panel";
import { StepHeader } from "../components/intake/step-header";
import { StyleSelector } from "../components/intake/style-selector";
import { SummaryPanel } from "../components/intake/summary-panel";
import { TemplateSelector } from "../components/intake/template-selector";
import { getDocument, getSession, sendMessage, updateSession, uploadAttachment } from "../lib/api";
import type { AttachmentPayload, DocumentPayload, SessionPayload } from "../lib/types";

export function SessionPage({
  initialState,
}: {
  initialState?: { status: string; queuePosition?: number };
}) {
  const { token = "" } = useParams();
  const [session, setSession] = useState<SessionPayload | null>(
    initialState
      ? ({
          token,
          status: initialState.status as SessionPayload["status"],
          current_stage: "template",
          selected_template: null,
          selected_style: null,
          summary: { payload: {} },
          document: { status: "pending" },
          queuePosition: initialState.queuePosition,
        } as SessionPayload)
      : null,
  );
  const [documentState, setDocumentState] = useState<DocumentPayload | null>(null);
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([
    {
      role: "assistant",
      content: "先从模板开始。你可以直接选一个，也可以跳过后继续梳理。",
    },
  ]);
  const [draft, setDraft] = useState("");
  const [attachments, setAttachments] = useState<Array<{ fileName: string; caption: string }>>([]);
  const [isSending, setIsSending] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!token || initialState?.status === "queued") {
      return;
    }

    let cancelled = false;

    async function load() {
      try {
        const payload = await getSession(token);
        if (!cancelled) {
          setSession(payload);
          setErrorMessage("");
        }
      } catch (_error) {
        if (!cancelled) {
          setErrorMessage("暂时无法读取当前进度，请稍后刷新重试。");
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
    if (!token || session?.status !== "generating_document") {
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

  if (session?.status === "queued") {
    return (
      <main className="px-4 py-6 text-white">
        <p>当前正在为其他用户整理网站需求，你已进入等待队列。</p>
        <p>你前面还有 {session.queuePosition} 人。</p>
      </main>
    );
  }

  if (!session) {
    return <main className="px-4 py-6 text-white">正在加载...</main>;
  }

  const currentStage = session.current_stage;

  async function handleTemplateSelect(value: string) {
    try {
      const payload = await updateSession(token, {
        selected_template: value === "跳过" ? null : value,
        current_stage: "style",
      });
      setSession((current) => ({ ...(current as SessionPayload), ...payload }));
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("模板更新失败，请稍后重试。");
    }
  }

  async function handleStyleSelect(value: string) {
    try {
      const payload = await updateSession(token, {
        selected_style: value === "跳过" ? null : value,
        current_stage: "positioning",
      });
      setSession((current) => ({ ...(current as SessionPayload), ...payload }));
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("风格更新失败，请稍后重试。");
    }
  }

  async function handleSend() {
    if (!draft.trim() || isSending) {
      return;
    }

    const userContent = draft.trim();
    setMessages((current) => [...current, { role: "user", content: userContent }]);
    setDraft("");
    setIsSending(true);

    try {
      const payload = await sendMessage(token, {
        content: userContent,
        stage_completed: currentStage !== "generate",
        generation_requested: currentStage === "generate",
      });
      const assistantContent = payload.assistant_reply ?? payload.message;
      if (assistantContent) {
        setMessages((current) => [
          ...current,
          { role: "assistant", content: assistantContent },
        ]);
      }
      setSession((current) => ({
        ...(current as SessionPayload),
        current_stage: payload.current_stage ?? current?.current_stage ?? "template",
        status: payload.session_status ?? current?.status ?? "draft",
        queuePosition: payload.queue_position ?? current?.queuePosition,
      }));
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("暂时无法继续整理需求，请稍后重试。");
    } finally {
      setIsSending(false);
    }
  }

  async function handleUpload(file: File) {
    try {
      const payload: AttachmentPayload = await uploadAttachment(token, file, "参考图片");
      setAttachments((current) => [
        ...current,
        { fileName: payload.file_name, caption: payload.caption },
      ]);
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("图片上传失败，请换一张图片后重试。");
    }
  }

  return (
    <main className="min-h-screen bg-[var(--color-bg)] text-white">
      <div className="mx-auto max-w-6xl px-4 py-4 sm:px-6">
        <StepHeader currentStage={session.current_stage} />
        {errorMessage ? (
          <div className="mt-4 rounded-[20px] border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/10 px-4 py-3 text-sm text-white/86">
            {errorMessage}
          </div>
        ) : null}
        <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="space-y-4">
            {session.current_stage === "template" && (
              <TemplateSelector
                onSelect={handleTemplateSelect}
                onSkip={() => void handleTemplateSelect("跳过")}
              />
            )}
            {session.current_stage !== "template" && (
              <StyleSelector
                onSelect={handleStyleSelect}
                onSkip={() => void handleStyleSelect("跳过")}
              />
            )}
            <ChatPanel
              draft={draft}
              isSending={isSending}
              messages={messages}
              onDraftChange={setDraft}
              onSend={() => void handleSend()}
            />
            <AttachmentPanel
              attachments={attachments}
              onUpload={(file) => void handleUpload(file)}
            />
          </div>
          <SummaryPanel
            documentState={documentState}
            session={session}
            summaryPayload={session.summary?.payload}
          />
        </div>
      </div>
    </main>
  );
}
