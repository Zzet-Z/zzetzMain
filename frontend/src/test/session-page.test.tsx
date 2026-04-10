import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "../app";

function buildSessionResponse(overrides: Record<string, unknown> = {}) {
  return {
    token: "demo-token",
    status: "awaiting_user",
    messages: [
      {
        id: 1,
        role: "assistant",
        content: "欢迎使用。",
        delivery_status: "system",
      },
    ],
    attachments: [
      {
        id: 7,
        file_name: "reference.png",
        caption: "参考图",
        preview_url: "blob:historical-preview",
      },
    ],
    has_more: false,
    oldest_message_id: 1,
    ...overrides,
  };
}

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/sessions/demo-token")) {
        return new Response(JSON.stringify(buildSessionResponse()), { status: 200 });
      }
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("聊天页只展示消息流、输入区和附件入口", async () => {
  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  expect(await screen.findByText("欢迎使用。")).toBeInTheDocument();

  expect(screen.queryByText("模板")).not.toBeInTheDocument();
  expect(screen.queryByText("风格")).not.toBeInTheDocument();
  expect(screen.queryByText("需求摘要")).not.toBeInTheDocument();
  expect(screen.getByPlaceholderText("继续描述你的网站需求")).toBeInTheDocument();
  expect(screen.getByLabelText("上传参考图片")).toBeInTheDocument();
});

test("历史附件带有 preview_url 时会展示缩略图", async () => {
  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  expect(await screen.findByRole("img", { name: "reference.png 缩略图" })).toBeInTheDocument();
  expect(screen.getByText("reference.png")).toBeInTheDocument();
});

test("当会话进入 ready_to_generate 时展示确认按钮", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/sessions/demo-token")) {
        return new Response(
          JSON.stringify(
            buildSessionResponse({
              conversation_intent: "ready_to_generate",
              messages: [
                {
                  id: 1,
                  role: "assistant",
                  content: "我现在可以整理最终需求文档。",
                  delivery_status: "final",
                },
              ],
            }),
          ),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );

  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    await screen.findByRole("button", { name: "开始生成最终需求文档" }),
  ).toBeInTheDocument();
});

test("completed 会话会禁用输入区并展示 successor token", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/sessions/demo-token")) {
        return new Response(
          JSON.stringify(
            buildSessionResponse({
              status: "completed",
              successor_token: "next-token",
              messages: [
                {
                  id: 1,
                  role: "assistant",
                  content: "最终需求文档已经整理完成。",
                  delivery_status: "final",
                },
              ],
            }),
          ),
          { status: 200 },
        );
      }
      if (url.includes("/sessions/demo-token/document")) {
        return new Response(
          JSON.stringify({
            status: "ready",
            summary_text: "网站类型：个人作品页",
            prd_markdown: "# 网站需求 PRD",
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );

  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  const composer = await screen.findByPlaceholderText("继续描述你的网站需求");
  await waitFor(() => {
    expect(composer).toBeDisabled();
  });
  expect(screen.getByText(/next-token/)).toBeInTheDocument();
});

test("completed 会话会弹出上线提示，确认后返回首页", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/sessions/demo-token")) {
        return new Response(
          JSON.stringify(
            buildSessionResponse({
              status: "completed",
              successor_token: "next-token",
              messages: [
                {
                  id: 1,
                  role: "assistant",
                  content: "最终需求文档已经整理完成。",
                  delivery_status: "final",
                },
              ],
            }),
          ),
          { status: 200 },
        );
      }
      if (url.includes("/sessions/demo-token/document")) {
        return new Response(
          JSON.stringify({
            status: "ready",
            summary_text: "网站类型：个人作品页",
            prd_markdown: "# 网站需求 PRD",
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );

  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  expect(await screen.findByText("您的网站将于3-24小时内上线")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "确认" }));

  await waitFor(() => {
    expect(screen.getByRole("heading", { name: "把你想要的网站，说出来。" })).toBeInTheDocument();
  });
});

test("首次加载会话失败时展示错误提示而不是永久停留在加载态", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/sessions/demo-token")) {
        return new Response(JSON.stringify({ message: "读取会话失败" }), { status: 500 });
      }
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );

  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  expect(await screen.findByText("暂时无法读取当前会话，请稍后刷新重试。")).toBeInTheDocument();
  expect(screen.queryByText("正在加载...")).not.toBeInTheDocument();
});
