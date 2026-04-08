import { useState } from "react";

import { Button } from "../ui/button";

export function Hero() {
  const [loading, setLoading] = useState(false);

  function handleStart() {
    setLoading(true);
    window.setTimeout(() => setLoading(false), 900);
  }

  return (
    <section className="border-b border-white/10 px-6 pb-16 pt-12 sm:px-8 sm:pb-24 sm:pt-20">
      <div className="mx-auto flex max-w-[980px] flex-col gap-8">
        <p className="text-[12px] uppercase tracking-[0.24em] text-white/56">
          中文网站需求梳理
        </p>
        <div className="max-w-3xl space-y-5">
          <h1 className="max-w-[12ch] text-[44px] font-semibold leading-[1.08] tracking-[-0.02em] text-white sm:text-[64px]">
            把你想要的网站，说出来。
          </h1>
          <p className="max-w-2xl text-[17px] leading-[1.7] text-white/72 sm:text-[21px] sm:leading-[1.5]">
            先通过真实中文对话，把你的定位、内容和功能想清楚。
            不需要你先会写 PRD，也不用一上来就决定页面结构。
          </p>
        </div>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <Button loading={loading} onClick={handleStart}>
            开始梳理我的网站
          </Button>
          <p className="text-[14px] leading-[1.45] text-white/52">
            结果会输出中文摘要与可直接交付设计/开发的 PRD。
          </p>
        </div>
      </div>
    </section>
  );
}
