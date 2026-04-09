import { AttachmentPanel } from "./attachment-panel";

import type { SessionAttachment, SessionMessage } from "../../lib/types";

interface ChatPanelProps {
  attachments: SessionAttachment[];
  composerDisabled: boolean;
  conversationIntent?: "continue" | "ready_to_generate";
  draft: string;
  hasMore: boolean;
  helperText?: string;
  isLoadingMore: boolean;
  isSending: boolean;
  messages: SessionMessage[];
  onConfirmGenerate: () => void;
  onDraftChange: (value: string) => void;
  onLoadMore: () => void;
  onSend: () => void;
  onUpload: (file: File) => void;
}

export function ChatPanel({
  attachments,
  composerDisabled,
  conversationIntent,
  draft,
  hasMore,
  helperText,
  isLoadingMore,
  isSending,
  messages,
  onConfirmGenerate,
  onDraftChange,
  onLoadMore,
  onSend,
  onUpload,
}: ChatPanelProps) {
  return (
    <section className="flex min-h-[calc(100vh-48px)] flex-col rounded-[28px] border border-white/10 bg-[var(--color-surface-1)]/88 shadow-[0_18px_50px_rgba(0,0,0,0.18)]">
      <div className="border-b border-white/10 px-5 py-4 sm:px-6">
        <p className="text-[12px] uppercase tracking-[0.24em] text-white/40">需求对话</p>
        <h1 className="mt-2 text-[28px] font-semibold leading-[1.15] tracking-[-0.01em] text-white sm:text-[34px]">
          继续梳理你的网站需求
        </h1>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-4 py-6 sm:px-6">
        {hasMore ? (
          <button
            className="mx-auto block rounded-full border border-white/12 px-4 py-2 text-sm text-white/76 disabled:opacity-50"
            disabled={isLoadingMore}
            onClick={onLoadMore}
            type="button"
          >
            {isLoadingMore ? "加载中..." : "加载更多消息"}
          </button>
        ) : null}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[82%] rounded-[24px] px-4 py-3 text-[15px] leading-[1.7] sm:max-w-[78%] ${
                message.role === "user"
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-white/6 text-white/88"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}

        {conversationIntent === "ready_to_generate" ? (
          <div className="flex justify-start">
            <button
              className="rounded-full bg-[var(--color-accent)] px-4 py-2 text-sm text-white disabled:opacity-50"
              disabled={composerDisabled || isSending}
              onClick={onConfirmGenerate}
              type="button"
            >
              开始生成最终需求文档
            </button>
          </div>
        ) : null}

        {isSending ? (
          <div className="flex justify-start">
            <div className="rounded-[24px] bg-white/6 px-4 py-3 text-[15px] text-white/88">
              思考中...
            </div>
          </div>
        ) : null}
      </div>

      <div className="border-t border-white/10 bg-black/55 px-4 py-4 backdrop-blur-xl sm:px-6">
        <AttachmentPanel attachments={attachments} disabled={composerDisabled} onUpload={onUpload} />
        <div className="mt-4">
          <label className="sr-only" htmlFor="session-composer">
            继续描述你的网站需求
          </label>
          <textarea
            id="session-composer"
            className="min-h-28 w-full rounded-[20px] border border-white/10 bg-black/30 p-4 text-[16px] leading-[1.6] text-white outline-none placeholder:text-white/28 disabled:cursor-not-allowed disabled:opacity-45"
            disabled={composerDisabled}
            onChange={(event) => onDraftChange(event.target.value)}
            placeholder="继续描述你的网站需求"
            value={draft}
          />
        </div>

        <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-[13px] leading-[1.6] text-white/48">
            {helperText ?? "直接用中文描述你的目标用户、内容重点、偏好风格和参考案例。"}
          </p>
          <button
            className="rounded-full bg-white px-5 py-2.5 text-sm text-black disabled:opacity-45"
            disabled={composerDisabled || isSending || !draft.trim()}
            onClick={onSend}
            type="button"
          >
            发送
          </button>
        </div>
      </div>
    </section>
  );
}
