const steps = [
  {
    index: "01",
    title: "选择方向",
    body: "先确定网站类型和风格，不必一次把全部内容想完。",
  },
  {
    index: "02",
    title: "梳理需求",
    body: "围绕定位、内容和功能逐步追问，边聊边形成结构化摘要。",
  },
  {
    index: "03",
    title: "获取结果",
    body: "生成中文摘要和中文 PRD，方便你继续找设计师或开发落地。",
  },
];

export function Process() {
  return (
    <section className="border-y border-white/10 px-6 py-16 sm:px-8 sm:py-24">
      <div className="mx-auto max-w-[980px] space-y-10">
        <div className="max-w-2xl space-y-4">
          <h2 className="text-[34px] font-semibold leading-[1.12] tracking-[-0.01em] text-white sm:text-[44px]">
            三步，把模糊想法变成可执行方案
          </h2>
          <p className="text-[17px] leading-[1.7] text-white/68">
            过程足够简单，输出足够具体。移动端也能顺畅完成。
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {steps.map((step) => (
            <article
              key={step.index}
              className="rounded-[20px] bg-[var(--color-surface-2)] px-5 py-6 text-white"
            >
              <p className="text-[12px] tracking-[0.24em] text-white/45">{step.index}</p>
              <h3 className="mt-4 text-[24px] font-normal leading-[1.2]">{step.title}</h3>
              <p className="mt-4 text-[15px] leading-[1.7] text-white/70">{step.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
