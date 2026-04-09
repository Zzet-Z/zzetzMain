import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "../app";
import type { AdminTokenDetail, AdminTokenListItem, CreatedAdminTokenPayload } from "../lib/types";

let fetchMock: ReturnType<typeof vi.fn>;

const listItems: AdminTokenListItem[] = [];
const detailByToken = new Map<string, AdminTokenDetail>();

function mockAdminTokens(items: AdminTokenListItem[]) {
  listItems.splice(0, listItems.length, ...items);
}

function mockAdminDetail(detail: AdminTokenDetail) {
  detailByToken.set(detail.token, detail);
}

function renderAdminPage() {
  render(
    <MemoryRouter initialEntries={["/admin"]}>
      <App />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  listItems.splice(0, listItems.length);
  detailByToken.clear();

  fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);

    if (url.endsWith("/api/admin/tokens") && (!init?.method || init.method === "GET")) {
      return new Response(JSON.stringify({ items: listItems }), { status: 200 });
    }

    if (url.endsWith("/api/admin/tokens") && init?.method === "POST") {
      const body = JSON.parse(String(init.body ?? "{}")) as {
        admin_note?: string;
        previous_document_id?: number;
      };

      const created: AdminTokenListItem = {
        token: "fresh-token",
        status: "awaiting_user",
        admin_note: body.admin_note ?? null,
        message_count: 0,
        attachment_count: 0,
        document_status: null,
        last_activity_at: null,
        origin_session_token: null,
        next_session_token: null,
      };

      listItems.unshift(created);
      detailByToken.set("fresh-token", {
        ...created,
        previous_document_id: body.previous_document_id ?? null,
        previous_summary: "上一版摘要",
        document: { status: "pending", summary_text: "", prd_markdown: "" },
        attachments: [],
        summary_text: null,
        prd_markdown: null,
        last_error: null,
        completed_at: null,
        created_at: "2026-04-09T00:00:00Z",
        expires_at: null,
      });

      const createdPayload: CreatedAdminTokenPayload = {
        token: "fresh-token",
        status: "awaiting_user",
        admin_note: body.admin_note ?? null,
        previous_document_id: body.previous_document_id ?? null,
        origin_session_token: null,
        next_session_token: null,
        successor_token: null,
      };

      return new Response(JSON.stringify(createdPayload), { status: 201 });
    }

    const detailMatch = url.match(/\/api\/admin\/tokens\/([^/]+)$/);
    if (detailMatch && (!init?.method || init.method === "GET")) {
      const token = detailMatch[1];
      return new Response(JSON.stringify(detailByToken.get(token)), { status: 200 });
    }

    const revokeMatch = url.match(/\/api\/admin\/tokens\/([^/]+)\/revoke$/);
    if (revokeMatch && init?.method === "POST") {
      const token = revokeMatch[1];
      const existing = detailByToken.get(token);
      if (existing) {
        const revoked = { ...existing, status: "expired" as const };
        detailByToken.set(token, revoked);
        const index = listItems.findIndex((item) => item.token === token);
        if (index >= 0) {
          listItems[index] = { ...listItems[index], status: "expired" };
        }
        return new Response(JSON.stringify(revoked), { status: 200 });
      }
    }

    return new Response(JSON.stringify({}), { status: 404 });
  });

  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("管理员输入 Bearer token 后可以加载 token 列表", async () => {
  mockAdminTokens([
    {
      token: "invite-token",
      status: "awaiting_user",
      admin_note: "李医生主页",
      message_count: 2,
      attachment_count: 0,
      document_status: null,
      last_activity_at: "2026-04-09T10:00:00Z",
      origin_session_token: null,
      next_session_token: null,
    },
  ]);

  renderAdminPage();

  fireEvent.change(screen.getByLabelText("管理员 Token"), {
    target: { value: "admin-secret" },
  });
  fireEvent.click(screen.getByRole("button", { name: "进入后台" }));

  expect(await screen.findByText("李医生主页")).toBeInTheDocument();
  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:5000/api/admin/tokens",
      expect.objectContaining({
        headers: { Authorization: "Bearer admin-secret" },
      }),
    );
  });
});

test("管理员可以创建新 token 并追加到列表", async () => {
  mockAdminTokens([]);

  renderAdminPage();

  fireEvent.change(screen.getByLabelText("管理员 Token"), {
    target: { value: "admin-secret" },
  });
  fireEvent.click(screen.getByRole("button", { name: "进入后台" }));
  fireEvent.change(screen.getByLabelText("访客备注"), {
    target: { value: "品牌顾问官网" },
  });
  fireEvent.change(screen.getByLabelText("来源文档 ID（可选）"), {
    target: { value: "12" },
  });
  fireEvent.click(screen.getByRole("button", { name: "签发新 Token" }));

  expect(await screen.findByRole("button", { name: "查看 fresh-token" })).toBeInTheDocument();
  expect(screen.getAllByText("品牌顾问官网").length).toBeGreaterThan(0);
  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:5000/api/admin/tokens",
      expect.objectContaining({
        method: "POST",
        headers: {
          Authorization: "Bearer admin-secret",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          admin_note: "品牌顾问官网",
          previous_document_id: 12,
        }),
      }),
    );
  });
});

test("管理员点击列表项后可以查看 token 详情", async () => {
  mockAdminTokens([
    {
      token: "invite-token",
      status: "completed",
      admin_note: "已完成站点",
      message_count: 6,
      attachment_count: 1,
      document_status: "ready",
      last_activity_at: "2026-04-09T10:00:00Z",
      origin_session_token: null,
      next_session_token: "next-token",
    },
  ]);
  mockAdminDetail({
    token: "invite-token",
    status: "completed",
    admin_note: "已完成站点",
    message_count: 6,
    attachment_count: 1,
    document_status: "ready",
    last_activity_at: "2026-04-09T10:00:00Z",
    origin_session_token: null,
    next_session_token: "next-token",
    previous_document_id: 9,
    previous_summary: "这是上一轮整理后的摘要。",
    attachments: [
      {
        id: 7,
        file_name: "reference.png",
        caption: "首页参考图",
        preview_url: "/api/sessions/invite-token/attachments/7/preview",
      },
    ],
    document: { status: "ready", summary_text: "这是上一轮整理后的摘要。", prd_markdown: "# 最终文档" },
    summary_text: "这是上一轮整理后的摘要。",
    prd_markdown: "# 最终文档",
    last_error: null,
    completed_at: "2026-04-09T10:05:00Z",
    created_at: "2026-04-09T09:00:00Z",
    expires_at: null,
  });

  renderAdminPage();

  fireEvent.change(screen.getByLabelText("管理员 Token"), {
    target: { value: "admin-secret" },
  });
  fireEvent.click(screen.getByRole("button", { name: "进入后台" }));
  fireEvent.click(await screen.findByRole("button", { name: "查看 invite-token" }));

  expect(await screen.findByText("这是上一轮整理后的摘要。")).toBeInTheDocument();
  expect(screen.getByText("next-token")).toBeInTheDocument();
  expect(screen.getByText("消息数")).toBeInTheDocument();
  expect(screen.getByText("附件数")).toBeInTheDocument();
  expect(screen.getByText("reference.png")).toBeInTheDocument();
  expect(screen.getByText("# 最终文档")).toBeInTheDocument();
});

test("管理员可以撤销 token", async () => {
  mockAdminTokens([
    {
      token: "invite-token",
      status: "awaiting_user",
      admin_note: "待撤销",
      message_count: 1,
      attachment_count: 0,
      document_status: null,
      last_activity_at: null,
      origin_session_token: null,
      next_session_token: null,
    },
  ]);
  mockAdminDetail({
    token: "invite-token",
    status: "awaiting_user",
    admin_note: "待撤销",
    message_count: 1,
    attachment_count: 0,
    document_status: null,
    last_activity_at: null,
    origin_session_token: null,
    next_session_token: null,
    previous_document_id: null,
    previous_summary: null,
    attachments: [],
    document: { status: "pending", summary_text: "", prd_markdown: "" },
    summary_text: null,
    prd_markdown: null,
    last_error: null,
    completed_at: null,
    created_at: "2026-04-09T09:00:00Z",
    expires_at: null,
  });

  renderAdminPage();

  fireEvent.change(screen.getByLabelText("管理员 Token"), {
    target: { value: "admin-secret" },
  });
  fireEvent.click(screen.getByRole("button", { name: "进入后台" }));
  fireEvent.click(await screen.findByRole("button", { name: "查看 invite-token" }));
  fireEvent.click(await screen.findByRole("button", { name: "撤销 Token" }));

  expect(await screen.findByText("expired")).toBeInTheDocument();
  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:5000/api/admin/tokens/invite-token/revoke",
      expect.objectContaining({
        method: "POST",
        headers: { Authorization: "Bearer admin-secret" },
      }),
    );
  });
});
