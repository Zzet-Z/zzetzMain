const TEMPLATE_OPTIONS = [
  "个人作品页",
  "个人简历页",
  "个人品牌页",
  "服务介绍页",
  "公司介绍页",
  "预约/咨询型主页",
];

export function TemplateSelector({
  onSelect,
  onSkip,
}: {
  onSelect: (value: string) => void;
  onSkip: () => void;
}) {
  return (
    <section
      aria-labelledby="template-selector-title"
      className="rounded-[24px] border border-white/10 bg-white/5 p-4"
    >
      <h2
        className="text-[21px] font-semibold text-white"
        id="template-selector-title"
      >
        网站模板
      </h2>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {TEMPLATE_OPTIONS.map((option) => (
          <button
            key={option}
            className="rounded-[20px] border border-white/10 bg-black/20 px-4 py-4 text-left text-[15px] text-white/86 transition hover:border-white/30"
            onClick={() => onSelect(option)}
            type="button"
          >
            {option}
          </button>
        ))}
      </div>
      <button
        className="mt-3 rounded-full border border-white/20 px-4 py-2 text-sm text-white/80"
        onClick={onSkip}
        type="button"
      >
        跳过
      </button>
    </section>
  );
}
