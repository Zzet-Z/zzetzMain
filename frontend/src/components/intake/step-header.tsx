import type { SessionStage } from "../../lib/types";

const STAGES: Array<{ key: SessionStage; label: string }> = [
  { key: "template", label: "模板" },
  { key: "style", label: "风格" },
  { key: "positioning", label: "定位" },
  { key: "content", label: "内容" },
  { key: "features", label: "功能" },
  { key: "generate", label: "生成" },
];

export function StepHeader({ currentStage }: { currentStage: SessionStage }) {
  return (
    <header className="sticky top-3 z-10 rounded-[24px] border border-white/10 bg-black/70 px-4 py-3 backdrop-blur">
      <ol className="flex gap-2 overflow-x-auto text-sm text-white/80">
        {STAGES.map((stage) => (
          <li
            key={stage.key}
            className={`whitespace-nowrap rounded-full px-3 py-1 ${
              currentStage === stage.key
                ? "bg-[var(--color-accent)] text-white"
                : "bg-white/5 text-white/60"
            }`}
          >
            {stage.label}
          </li>
        ))}
      </ol>
      <p className="mt-2 text-xs text-white/50">当前阶段：{STAGES.find((stage) => stage.key === currentStage)?.label}</p>
    </header>
  );
}
