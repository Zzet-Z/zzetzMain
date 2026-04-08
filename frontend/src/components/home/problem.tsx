const painPoints = [
  {
    title: "你知道自己需要网站，但说不清要放什么",
    body: "常见情况是脑中有一些词，比如“高级”“专业”“看起来像我”，但这些词还不能直接变成页面需求。",
  },
  {
    title: "你担心和设计师、开发沟通时反复返工",
    body: "没有一份成型摘要时，任何讨论都容易停留在感受层面，最后不断推翻重来。",
  },
  {
    title: "你需要的是被引导，而不是空白文档",
    body: "这个工具会像产品经理一样逐步追问，帮你把模糊想法压缩成清晰决策。",
  },
];

export function Problem() {
  return (
    <section className="bg-[var(--color-surface-1)] px-6 py-16 text-[var(--color-ink)] sm:px-8 sm:py-24">
      <div className="mx-auto max-w-[980px] space-y-10">
        <div className="max-w-2xl space-y-4">
          <h2 className="text-[34px] font-semibold leading-[1.12] tracking-[-0.01em] sm:text-[44px]">
            你不需要先会写 PRD
          </h2>
          <p className="text-[17px] leading-[1.7] text-black/72">
            你只需要知道自己想被谁看见、希望别人感受到什么，以及网站最后要帮你完成什么。
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {painPoints.map((item) => (
            <article
              key={item.title}
              className="rounded-[18px] bg-white px-5 py-6 shadow-[0_10px_40px_rgba(0,0,0,0.08)]"
            >
              <h3 className="text-[21px] font-semibold leading-[1.25] text-[var(--color-ink)]">
                {item.title}
              </h3>
              <p className="mt-4 text-[15px] leading-[1.7] text-black/70">{item.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
