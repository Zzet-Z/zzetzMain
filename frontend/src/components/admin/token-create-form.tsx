import type { FormEvent } from "react";

import { Button } from "../ui/button";

interface TokenCreateFormProps {
  adminToken: string;
  adminNote: string;
  previousDocumentId: string;
  isLoading: boolean;
  isCreating: boolean;
  onAdminTokenChange: (value: string) => void;
  onAdminSubmit: () => void;
  onAdminNoteChange: (value: string) => void;
  onPreviousDocumentIdChange: (value: string) => void;
  onCreate: () => void;
}

export function TokenCreateForm({
  adminToken,
  adminNote,
  previousDocumentId,
  isLoading,
  isCreating,
  onAdminTokenChange,
  onAdminSubmit,
  onAdminNoteChange,
  onPreviousDocumentIdChange,
  onCreate,
}: TokenCreateFormProps) {
  function handleAdminSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onAdminSubmit();
  }

  function handleCreateSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onCreate();
  }

  return (
    <div className="space-y-4">
      <section className="rounded-[28px] border border-white/10 bg-white/[0.03] px-5 py-5 sm:px-6">
        <div className="space-y-2">
          <p className="text-[12px] uppercase tracking-[0.22em] text-white/42">管理员鉴权</p>
          <h2 className="text-[28px] font-semibold leading-[1.15] text-white">输入后台访问 Token</h2>
          <p className="text-[16px] leading-[1.7] text-white/62">
            使用 `Authorization: Bearer &lt;admin_token&gt;` 读取受控会话列表。
          </p>
        </div>
        <form className="mt-5 flex flex-col gap-3 sm:flex-row" onSubmit={handleAdminSubmit}>
          <div className="flex-1">
            <label className="sr-only" htmlFor="admin-token-input">
              管理员 Token
            </label>
            <input
              id="admin-token-input"
              className="h-12 w-full rounded-[16px] border border-white/10 bg-black/25 px-4 text-[16px] text-white outline-none placeholder:text-white/28 focus:border-[var(--color-accent)]"
              placeholder="请输入管理员 Token"
              value={adminToken}
              onChange={(event) => onAdminTokenChange(event.target.value)}
              autoComplete="off"
              spellCheck={false}
            />
          </div>
          <Button type="submit" disabled={!adminToken.trim() || isLoading}>
            进入后台
          </Button>
        </form>
      </section>

      <section className="rounded-[28px] border border-white/10 bg-[var(--color-surface-2)] px-5 py-5 sm:px-6">
        <div className="space-y-2">
          <p className="text-[12px] uppercase tracking-[0.22em] text-white/42">签发访客入口</p>
          <h2 className="text-[21px] font-semibold leading-[1.2] text-white">创建新的会话 Token</h2>
          <p className="text-[15px] leading-[1.7] text-white/60">
            可填写访客备注；如需基于旧文档继续修订，可补充来源文档 ID。
          </p>
        </div>
        <form className="mt-5 grid gap-3" onSubmit={handleCreateSubmit}>
          <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_220px]">
            <div>
              <label className="mb-2 block text-[14px] text-white/68" htmlFor="admin-note-input">
                访客备注
              </label>
              <input
                id="admin-note-input"
                className="h-12 w-full rounded-[16px] border border-white/10 bg-black/25 px-4 text-[16px] text-white outline-none placeholder:text-white/28 focus:border-[var(--color-accent)]"
                placeholder="例如：李医生主页改版"
                value={adminNote}
                onChange={(event) => onAdminNoteChange(event.target.value)}
              />
            </div>
            <div>
              <label
                className="mb-2 block text-[14px] text-white/68"
                htmlFor="previous-document-id-input"
              >
                来源文档 ID（可选）
              </label>
              <input
                id="previous-document-id-input"
                className="h-12 w-full rounded-[16px] border border-white/10 bg-black/25 px-4 text-[16px] text-white outline-none placeholder:text-white/28 focus:border-[var(--color-accent)]"
                inputMode="numeric"
                placeholder="例如 12"
                value={previousDocumentId}
                onChange={(event) => onPreviousDocumentIdChange(event.target.value)}
              />
            </div>
          </div>
          <div className="flex justify-start">
            <Button type="submit" disabled={!adminToken.trim() || isCreating}>
              签发新 Token
            </Button>
          </div>
        </form>
      </section>
    </div>
  );
}
