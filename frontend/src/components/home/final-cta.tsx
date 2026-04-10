import { Button } from "../ui/button";

export function FinalCta({
  loading,
  onStart,
}: {
  loading: boolean;
  onStart: () => void;
}) {
  return (
    <section className="px-6 py-16 sm:px-8 sm:py-24">
      <div className="mx-auto max-w-[980px] rounded-[32px] border border-white/10 bg-[linear-gradient(180deg,rgba(39,39,41,0.96),rgba(24,24,26,0.96))] px-6 py-8 sm:px-10 sm:py-12">
        <div className="max-w-2xl space-y-5">
          <h2 className="text-[34px] font-semibold leading-[1.12] tracking-[-0.01em] text-white sm:text-[44px]">
            准备开始你的首页梳理了吗？
          </h2>
          <p className="text-[17px] leading-[1.7] text-white/68">
            不用一次说完整，只要先说出你想做的网站，我们会一步一步把它整理成可执行方案。
          </p>
          <Button loading={loading} onClick={onStart}>
            开始梳理我的网站
          </Button>
        </div>
      </div>
    </section>
  );
}
