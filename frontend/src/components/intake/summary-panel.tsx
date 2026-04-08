import type { DocumentPayload, SessionPayload } from "../../lib/types";

const STAGE_LABELS = {
  template: "模板",
  style: "风格",
  positioning: "定位",
  content: "内容",
  features: "功能",
  generate: "生成",
} as const;

const STATUS_LABELS = {
  draft: "待开始",
  queued: "排队中",
  active: "进行中",
  in_progress: "进行中",
  generating_document: "正在生成文档",
  completed: "已完成",
  failed: "处理失败",
} as const;

const DOCUMENT_STATUS_LABELS = {
  pending: "待生成",
  ready: "已生成",
  failed: "生成失败",
} as const;

export function SummaryPanel({
  session,
  summaryPayload,
  documentState,
}: {
  session: SessionPayload;
  summaryPayload: Record<string, unknown> | undefined;
  documentState: DocumentPayload | null;
}) {
  const documentStatusText =
    session.status === "generating_document"
      ? "正在生成 PRD"
      : DOCUMENT_STATUS_LABELS[documentState?.status as keyof typeof DOCUMENT_STATUS_LABELS] ??
        DOCUMENT_STATUS_LABELS[session.document?.status as keyof typeof DOCUMENT_STATUS_LABELS] ??
        documentState?.status ??
        session.document?.status ??
        "待生成";

  return (
    <aside className="rounded-[24px] border border-white/10 bg-white/5 p-4">
      <h2 className="text-[21px] font-semibold text-white">摘要</h2>
      <p className="mt-3 text-sm text-white/70">
        当前状态：{STATUS_LABELS[session.status] ?? session.status}
      </p>
      <p className="text-sm text-white/70">
        当前阶段：{STAGE_LABELS[session.current_stage] ?? session.current_stage}
      </p>
      <dl className="mt-4 space-y-3 text-sm text-white/80">
        <div>
          <dt className="text-white/45">网站类型</dt>
          <dd>{String(summaryPayload?.website_type ?? "未确定")}</dd>
        </div>
        <div>
          <dt className="text-white/45">视觉方向</dt>
          <dd>{String(summaryPayload?.visual_direction ?? "未确定")}</dd>
        </div>
        <div>
          <dt className="text-white/45">目标受众</dt>
          <dd>{String(summaryPayload?.audience ?? "未确定")}</dd>
        </div>
      </dl>
      <div className="mt-5 rounded-[18px] bg-black/25 p-4 text-sm text-white/78">
        <p>文档状态：{documentStatusText}</p>
        {documentState?.summary_text ? (
          <pre className="mt-3 whitespace-pre-wrap font-inherit text-white/72">
            {documentState.summary_text}
          </pre>
        ) : null}
      </div>
    </aside>
  );
}
