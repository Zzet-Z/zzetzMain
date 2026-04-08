export function ChatPanel({
  messages,
  draft,
  onDraftChange,
  onSend,
  isSending,
}: {
  messages: Array<{ role: "user" | "assistant"; content: string }>;
  draft: string;
  onDraftChange: (value: string) => void;
  onSend: () => void;
  isSending: boolean;
}) {
  return (
    <section className="rounded-[24px] border border-white/10 bg-white/5 p-4">
      <h2 className="text-[21px] font-semibold text-white">需求对话</h2>
      <div className="mt-4 space-y-3">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className="rounded-[18px] bg-black/25 p-3">
            <p className="text-xs text-white/45">{message.role === "user" ? "你" : "助手"}</p>
            <p className="mt-1 text-sm leading-[1.7] text-white/86">{message.content}</p>
          </div>
        ))}
      </div>
      <textarea
        className="mt-4 min-h-28 w-full rounded-[20px] border border-white/10 bg-black/30 p-3 text-sm text-white outline-none placeholder:text-white/35"
        onChange={(event) => onDraftChange(event.target.value)}
        placeholder="用中文描述你的网站目标、内容和风格偏好"
        value={draft}
      />
      <button
        className="mt-3 rounded-full bg-white px-4 py-2 text-sm text-black disabled:opacity-60"
        disabled={isSending}
        onClick={onSend}
        type="button"
      >
        {isSending ? "发送中..." : "发送"}
      </button>
    </section>
  );
}
