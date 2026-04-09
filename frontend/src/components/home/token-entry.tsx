import type { FormEvent } from "react";

import { Button } from "../ui/button";

interface TokenEntryProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export function TokenEntry({ value, onChange, onSubmit }: TokenEntryProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <section className="mx-auto mt-8 max-w-[980px] px-6 sm:px-8">
      <div className="rounded-[28px] border border-white/10 bg-[var(--color-surface-2)] px-5 py-6 shadow-[0_18px_50px_rgba(0,0,0,0.18)] sm:px-8 sm:py-8">
        <div className="max-w-2xl space-y-3">
          <p className="text-[12px] uppercase tracking-[0.24em] text-white/45">
            受控访问
          </p>
          <h2 className="text-[28px] font-semibold leading-[1.15] tracking-[-0.01em] text-white sm:text-[34px]">
            输入管理员签发的访问 Token
          </h2>
          <p className="text-[16px] leading-[1.7] text-white/68 sm:text-[17px]">
            你拿到 token 后再进入对话页。不会在首页匿名创建 session。
          </p>
        </div>
        <form className="mt-6 flex flex-col gap-3 sm:flex-row" onSubmit={handleSubmit}>
          <div className="flex-1">
            <label className="sr-only" htmlFor="home-token-input">
              访问 Token
            </label>
            <input
              id="home-token-input"
              className="h-12 w-full rounded-[16px] border border-white/10 bg-black/25 px-4 text-[16px] text-white outline-none placeholder:text-white/30 focus:border-[var(--color-accent)]"
              placeholder="请输入访问 Token"
              autoComplete="off"
              spellCheck={false}
              value={value}
              onChange={(event) => onChange(event.target.value)}
            />
          </div>
          <Button type="submit">进入对话</Button>
        </form>
      </div>
    </section>
  );
}
