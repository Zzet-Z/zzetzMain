import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "../app";

let fetchMock: ReturnType<typeof vi.fn>;

function buildSessionResponse(overrides: Record<string, unknown> = {}) {
  return {
    token: "demo-token",
    status: "awaiting_user",
    messages: [
      {
        id: 101,
        role: "assistant",
        content: "欢迎使用。",
        delivery_status: "system",
      },
    ],
    has_more: false,
    oldest_message_id: 101,
    ...overrides,
  };
}

beforeEach(() => {
  fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);

    if (url.includes("/sessions/demo-token/messages") && init?.method === "POST") {
      return new Response(
        JSON.stringify({
          session_status: "awaiting_user",
          assistant_message: "我建议你先明确网站主要目标。",
          conversation_intent: "continue",
          typing_started: true,
        }),
        { status: 201 },
      );
    }

    if (url.includes("/sessions/demo-token/attachments")) {
      return new Response(
        JSON.stringify({ file_name: "reference.png", caption: "参考图片" }),
        { status: 201 },
      );
    }

    if (url.includes("/sessions/demo-token/messages?before_id=101&limit=50")) {
      return new Response(
        JSON.stringify([
          {
            id: 100,
            role: "assistant",
            content: "更早的一条消息",
            delivery_status: "final",
          },
        ]),
        { status: 200 },
      );
    }

    if (url.includes("/sessions/demo-token")) {
      return new Response(
        JSON.stringify(
          buildSessionResponse({
            has_more: true,
          }),
        ),
        { status: 200 },
      );
    }

    return new Response(JSON.stringify({}), { status: 200 });
  });

  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("输入 token 后可以跳转到聊天页", async () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  fireEvent.click(screen.getAllByRole("button", { name: "开始梳理我的网站" })[0]);
  fireEvent.change(screen.getByLabelText("访问 Token"), {
    target: { value: "demo-token" },
  });
  fireEvent.click(screen.getByRole("button", { name: "进入对话" }));

  expect(await screen.findByText("欢迎使用。")).toBeInTheDocument();
});

test("发送消息后先显示 typing，再显示 assistant 回复", async () => {
  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  const composer = await screen.findByPlaceholderText("继续描述你的网站需求");
  fireEvent.change(composer, { target: { value: "我想做一个个人网站" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));

  expect(screen.getByText("...")).toBeInTheDocument();
  expect(await screen.findByText("我建议你先明确网站主要目标。")).toBeInTheDocument();

  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:5000/api/sessions/demo-token/messages",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ content: "我想做一个个人网站" }),
      }),
    );
  });
});

test("点击确认按钮后会发送 confirm_generate", async () => {
  fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);

    if (url.includes("/sessions/demo-token/messages") && init?.method === "POST") {
      return new Response(
        JSON.stringify({
          session_status: "generating_document",
          assistant_message: "正在整理最终需求文档。",
          conversation_intent: "continue",
        }),
        { status: 202 },
      );
    }

    if (url.includes("/sessions/demo-token")) {
      return new Response(
        JSON.stringify(
          buildSessionResponse({
            conversation_intent: "ready_to_generate",
            messages: [
              {
                id: 101,
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
  });

  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  fireEvent.click(
    await screen.findByRole("button", { name: "开始生成最终需求文档" }),
  );

  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:5000/api/sessions/demo-token/messages",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          content: "请开始生成最终需求文档",
          confirm_generate: true,
        }),
      }),
    );
  });
});

test("需求页选择图片后会调用上传并展示文件名", async () => {
  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  const input = await screen.findByLabelText("上传参考图片");
  const file = new File(["png"], "reference.png", { type: "image/png" });

  fireEvent.change(input, { target: { files: [file] } });

  expect(await screen.findByText(/reference\.png/)).toBeInTheDocument();
});

test("有更多历史消息时可以点击加载更多", async () => {
  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  fireEvent.click(await screen.findByRole("button", { name: "加载更多消息" }));

  expect(await screen.findByText("更早的一条消息")).toBeInTheDocument();

  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:5000/api/sessions/demo-token/messages?before_id=101&limit=50",
    );
  });
});
