export function OutputPreview() {
  return (
    <section className="bg-[var(--color-surface-1)] px-6 py-16 text-[var(--color-ink)] sm:px-8 sm:py-24">
      <div className="mx-auto max-w-[980px] space-y-10">
        <div className="max-w-2xl space-y-4">
          <h2 className="text-[34px] font-semibold leading-[1.12] tracking-[-0.01em] sm:text-[44px]">
            最后你会拿到什么
          </h2>
          <p className="text-[17px] leading-[1.7] text-black/72">
            一份适合自己回看、一份适合继续协作。先把想法说清楚，再决定如何做出来。
          </p>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <article className="rounded-[24px] bg-white px-6 py-6 shadow-[0_10px_40px_rgba(0,0,0,0.08)]">
            <p className="text-[12px] tracking-[0.24em] text-black/45">结构化摘要</p>
            <h3 className="mt-4 text-[24px] font-semibold leading-[1.2]">一眼看清网站应该长什么样</h3>
            <ul className="mt-5 space-y-3 text-[15px] leading-[1.7] text-black/72">
              <li>网站类型：个人作品页</li>
              <li>视觉方向：极简高级，留白多，深色背景</li>
              <li>重点模块：作品精选、关于我、合作方式、联系方式</li>
            </ul>
          </article>
          <article className="rounded-[24px] bg-[var(--color-surface-2)] px-6 py-6 text-white shadow-[0_18px_50px_rgba(0,0,0,0.2)]">
            <p className="text-[12px] tracking-[0.24em] text-white/45">中文 PRD</p>
            <h3 className="mt-4 text-[24px] font-semibold leading-[1.2]">方便继续交付设计与开发</h3>
            <p className="mt-5 text-[15px] leading-[1.8] text-white/70">
              包含项目目标、目标受众、页面结构、内容模块、功能需求、排除项与参考附件说明。
            </p>
            <div className="mt-6 rounded-[16px] border border-white/10 bg-black/25 p-4 text-[14px] leading-[1.7] text-white/72">
              <p># 项目目标</p>
              <p>展示作品并获取合作咨询。</p>
              <p className="mt-3">## 页面结构</p>
              <p>首页 / 作品详情 / 关于 / 联系方式</p>
            </div>
          </article>
        </div>
      </div>
    </section>
  );
}
