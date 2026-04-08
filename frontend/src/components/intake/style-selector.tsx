const STYLE_OPTIONS = ["极简高级", "现代专业", "强视觉作品集", "温和可信", "前卫未来感"];

export function StyleSelector({
  onSelect,
  onSkip,
}: {
  onSelect: (value: string) => void;
  onSkip: () => void;
}) {
  return (
    <section
      aria-labelledby="style-selector-title"
      className="rounded-[24px] border border-white/10 bg-white/5 p-4"
    >
      <h2
        className="text-[21px] font-semibold text-white"
        id="style-selector-title"
      >
        视觉风格
      </h2>
      <div className="mt-3 grid gap-3">
        {STYLE_OPTIONS.map((option) => (
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
