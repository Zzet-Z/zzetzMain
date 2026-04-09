import type { AdminTokenListItem } from "../../lib/types";

interface TokenListProps {
  items: AdminTokenListItem[];
  selectedToken?: string | null;
  onSelect: (token: string) => void;
}

function formatCount(value?: number) {
  return typeof value === "number" ? value : 0;
}

export function TokenList({ items, selectedToken, onSelect }: TokenListProps) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-white/[0.03] px-5 py-5 sm:px-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[12px] uppercase tracking-[0.22em] text-white/42">Token 列表</p>
          <h2 className="mt-2 text-[21px] font-semibold leading-[1.2] text-white">
            当前受控会话
          </h2>
        </div>
        <p className="text-[14px] text-white/52">共 {items.length} 条</p>
      </div>

      {items.length === 0 ? (
        <p className="mt-5 rounded-[20px] border border-dashed border-white/10 px-4 py-6 text-[15px] leading-[1.7] text-white/48">
          还没有可展示的 token。先输入管理员 Token，再签发一个新的入口。
        </p>
      ) : (
        <div className="mt-5 space-y-3">
          {items.map((item) => {
            const isSelected = item.token === selectedToken;

            return (
              <div
                key={item.token}
                className={`rounded-[22px] border px-4 py-4 transition ${
                  isSelected
                    ? "border-[var(--color-accent)]/60 bg-[var(--color-accent)]/10"
                    : "border-white/10 bg-black/20"
                }`}
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="space-y-2">
                    <p className="text-[17px] font-semibold leading-[1.35] text-white">{item.token}</p>
                    <p className="text-[15px] leading-[1.65] text-white/64">
                      {item.admin_note || "未填写备注"}
                    </p>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-[13px] text-white/46">
                      <span>状态：{item.status}</span>
                      <span>消息：{formatCount(item.message_count)}</span>
                      <span>附件：{formatCount(item.attachment_count)}</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="inline-flex min-h-11 items-center justify-center rounded-full border border-[var(--color-link-bright)]/50 px-4 text-[14px] text-[var(--color-link-bright)] transition hover:border-[var(--color-link-bright)]"
                    onClick={() => onSelect(item.token)}
                  >
                    查看 {item.token}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
