import { useState } from "react";

import {
  createAdminToken,
  getAdminTokenDetail,
  listAdminTokens,
  revokeAdminToken,
} from "../lib/api";
import type { AdminTokenDetail, AdminTokenListItem } from "../lib/types";
import { TokenCreateForm } from "../components/admin/token-create-form";
import { TokenDetail } from "../components/admin/token-detail";
import { TokenList } from "../components/admin/token-list";

function upsertListItem(items: AdminTokenListItem[], detail: AdminTokenDetail): AdminTokenListItem[] {
  const nextItem: AdminTokenListItem = {
    token: detail.token,
    status: detail.status,
    admin_note: detail.admin_note,
    message_count: detail.message_count,
    attachment_count: detail.attachment_count,
    document_status: detail.document_status ?? detail.document?.status ?? null,
    last_activity_at: detail.last_activity_at,
    previous_document_id: detail.previous_document_id,
    origin_session_token: detail.origin_session_token,
    next_session_token: detail.next_session_token,
    successor_token: detail.successor_token,
  };

  const existingIndex = items.findIndex((item) => item.token === detail.token);
  if (existingIndex === -1) {
    return [nextItem, ...items];
  }

  return items.map((item, index) => (index === existingIndex ? nextItem : item));
}

export function AdminPage() {
  const [adminToken, setAdminToken] = useState("");
  const [adminNote, setAdminNote] = useState("");
  const [previousDocumentId, setPreviousDocumentId] = useState("");
  const [tokens, setTokens] = useState<AdminTokenListItem[]>([]);
  const [selectedToken, setSelectedToken] = useState<string | null>(null);
  const [detail, setDetail] = useState<AdminTokenDetail | null>(null);
  const [isLoadingList, setIsLoadingList] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isRevoking, setIsRevoking] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleLoad() {
    if (!adminToken.trim()) {
      return;
    }

    setIsLoadingList(true);
    try {
      const payload = await listAdminTokens(adminToken.trim());
      setTokens(payload);
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("读取 token 列表失败，请确认管理员 Token 是否正确。");
    } finally {
      setIsLoadingList(false);
    }
  }

  async function handleCreate() {
    if (!adminToken.trim() || isCreating) {
      return;
    }

    setIsCreating(true);
    try {
      const payload = await createAdminToken(adminToken.trim(), {
        ...(adminNote.trim() ? { admin_note: adminNote.trim() } : {}),
        ...(previousDocumentId.trim()
          ? { previous_document_id: Number(previousDocumentId.trim()) }
          : {}),
      });
      const detailPayload = await getAdminTokenDetail(adminToken.trim(), payload.token);

      setTokens((current) => upsertListItem(current, detailPayload));
      setSelectedToken(payload.token);
      setDetail(detailPayload);
      setAdminNote("");
      setPreviousDocumentId("");
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("签发 token 失败，请稍后再试。");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleSelect(token: string) {
    if (!adminToken.trim()) {
      return;
    }

    setSelectedToken(token);
    setIsLoadingDetail(true);
    try {
      const payload = await getAdminTokenDetail(adminToken.trim(), token);
      setDetail(payload);
      setTokens((current) => upsertListItem(current, payload));
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("读取 token 详情失败，请稍后重试。");
    } finally {
      setIsLoadingDetail(false);
    }
  }

  async function handleRevoke() {
    if (!adminToken.trim() || !detail || isRevoking) {
      return;
    }

    setIsRevoking(true);
    try {
      const payload = await revokeAdminToken(adminToken.trim(), detail.token);
      setDetail(payload);
      setTokens((current) => upsertListItem(current, payload));
      setErrorMessage("");
    } catch (_error) {
      setErrorMessage("撤销 token 失败，请稍后重试。");
    } finally {
      setIsRevoking(false);
    }
  }

  return (
    <main className="min-h-screen bg-[var(--color-bg)] text-white">
      <div className="mx-auto max-w-[1200px] px-4 py-6 sm:px-6">
        <div className="mb-5 rounded-[28px] border border-white/10 bg-black/45 px-5 py-5 backdrop-blur-xl sm:px-6">
          <p className="text-[12px] uppercase tracking-[0.24em] text-white/42">Admin Dashboard</p>
          <h1 className="mt-3 text-[34px] font-semibold leading-[1.08] text-white sm:text-[40px]">
            受控 Token 管理后台
          </h1>
          <p className="mt-3 max-w-3xl text-[16px] leading-[1.7] text-white/64">
            在同一页面完成管理员鉴权、Token 签发、状态巡检、修订链查看和撤销。
          </p>
          {errorMessage ? (
            <div className="mt-4 rounded-[20px] border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/10 px-4 py-3 text-[14px] text-white/84">
              {errorMessage}
            </div>
          ) : null}
        </div>

        <div className="grid gap-5 xl:grid-cols-[420px_minmax(0,1fr)]">
          <TokenCreateForm
            adminToken={adminToken}
            adminNote={adminNote}
            previousDocumentId={previousDocumentId}
            isLoading={isLoadingList}
            isCreating={isCreating}
            onAdminTokenChange={setAdminToken}
            onAdminSubmit={() => void handleLoad()}
            onAdminNoteChange={setAdminNote}
            onPreviousDocumentIdChange={setPreviousDocumentId}
            onCreate={() => void handleCreate()}
          />

          <div className="grid gap-5">
            <TokenList items={tokens} selectedToken={selectedToken} onSelect={(token) => void handleSelect(token)} />
            <TokenDetail
              detail={detail}
              isLoading={isLoadingDetail}
              isRevoking={isRevoking}
              onRevoke={() => void handleRevoke()}
            />
          </div>
        </div>
      </div>
    </main>
  );
}
