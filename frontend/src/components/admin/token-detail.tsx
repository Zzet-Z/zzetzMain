import { Button } from "../ui/button";
import type { AdminTokenDetail } from "../../lib/types";

interface TokenDetailProps {
  detail: AdminTokenDetail | null;
  isLoading: boolean;
  isRevoking: boolean;
  onRevoke: () => void;
}

function DetailRow({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div className="rounded-[18px] border border-white/8 bg-black/20 px-4 py-3">
      <p className="text-[12px] uppercase tracking-[0.16em] text-white/36">{label}</p>
      <p className="mt-1 text-[15px] leading-[1.7] text-white/78">{value ?? "无"}</p>
    </div>
  );
}

export function TokenDetail({ detail, isLoading, isRevoking, onRevoke }: TokenDetailProps) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-[var(--color-surface-2)] px-5 py-5 sm:px-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-[12px] uppercase tracking-[0.22em] text-white/42">Token 详情</p>
          <h2 className="mt-2 text-[21px] font-semibold leading-[1.2] text-white">
            {detail?.token ?? "尚未选择 Token"}
          </h2>
          <p className="mt-2 text-[15px] leading-[1.7] text-white/60">
            {isLoading
              ? "正在读取详细信息。"
              : detail
                ? "查看摘要、修订链与失败信息，并在必要时手动撤销。"
                : "从左侧列表选择一条记录后，这里会显示完整详情。"}
          </p>
        </div>
        {detail ? (
          <Button
            variant="secondary"
            className="border-white/20 text-white hover:border-white/40"
            disabled={isRevoking || detail.status === "expired"}
            onClick={onRevoke}
          >
            撤销 Token
          </Button>
        ) : null}
      </div>

      {detail ? (
        <div className="mt-5 space-y-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <DetailRow label="状态" value={detail.status} />
            <DetailRow label="备注" value={detail.admin_note} />
            <DetailRow label="文档状态" value={detail.document_status} />
            <DetailRow label="后续修订 Token" value={detail.next_session_token} />
            <DetailRow label="来源会话" value={detail.origin_session_token} />
            <DetailRow label="来源文档 ID" value={detail.previous_document_id} />
          </div>

          <div className="rounded-[22px] border border-white/10 bg-white/[0.03] px-4 py-4">
            <p className="text-[12px] uppercase tracking-[0.18em] text-white/36">摘要</p>
            <p className="mt-3 whitespace-pre-wrap text-[15px] leading-[1.8] text-white/74">
              {detail.summary_text || "暂无摘要。"}
            </p>
          </div>

          {detail.last_error ? (
            <div className="rounded-[22px] border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/10 px-4 py-4">
              <p className="text-[12px] uppercase tracking-[0.18em] text-white/40">失败原因</p>
              <p className="mt-3 text-[15px] leading-[1.8] text-white/82">{detail.last_error}</p>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
