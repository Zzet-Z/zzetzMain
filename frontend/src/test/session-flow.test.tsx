import "@testing-library/jest-dom/vitest";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "../app";

let fetchMock: ReturnType<typeof vi.fn>;
let postMessageDeferred: { resolve: (response: Response) => void } | null = null;
let createObjectUrlSpy: ReturnType<typeof vi.fn> | null = null;
let revokeObjectUrlSpy: ReturnType<typeof vi.fn> | null = null;

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
  vi.useRealTimers();
  postMessageDeferred = null;
  createObjectUrlSpy = vi.fn(() => "blob:generated-preview");
  revokeObjectUrlSpy = vi.fn();
  Object.defineProperty(window.URL, "createObjectURL", {
    configurable: true,
    value: createObjectUrlSpy,
  });
  Object.defineProperty(window.URL, "revokeObjectURL", {
    configurable: true,
    value: revokeObjectUrlSpy,
  });
  fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);

    if (url.includes("/sessions/demo-token/messages") && init?.method === "POST") {
      return new Promise<Response>((resolve) => {
        postMessageDeferred = { resolve };
      }) as Promise<Response>;
    }

    if (url.includes("/sessions/demo-token/attachments")) {
      return new Response(
        JSON.stringify({ file_name: "reference.png", caption: "参考图片", preview_url: "blob:preview-reference" }),
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
  vi.useRealTimers();
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
  let intervalCallback: (() => void) | null = null;
  const setIntervalSpy = vi.spyOn(window, "setInterval").mockImplementation(((callback) => {
    intervalCallback = () => {
      if (typeof callback === "function") {
        callback();
      }
    };
    return 1 as unknown as number;
  }) as typeof window.setInterval);
  const clearIntervalSpy = vi.spyOn(window, "clearInterval").mockImplementation(() => undefined);

  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  await act(async () => {
    await Promise.resolve();
  });

  const composer = screen.getByPlaceholderText("继续描述你的网站需求");
  fireEvent.change(composer, { target: { value: "我想做一个个人网站" } });
  fireEvent.click(screen.getByRole("button", { name: "发送" }));

  expect(screen.getByText("思考中...")).toBeInTheDocument();
  expect(screen.getByText("我想做一个个人网站")).toBeInTheDocument();

  await act(async () => {
    intervalCallback?.();
    await Promise.resolve();
  });

  expect(screen.getByText("我想做一个个人网站")).toBeInTheDocument();

  await act(async () => {
    postMessageDeferred?.resolve(
      new Response(
        JSON.stringify({
          session_status: "awaiting_user",
          assistant_message: "我建议你先明确网站主要目标。",
          conversation_intent: "continue",
          typing_started: true,
        }),
        { status: 201 },
      ),
    );
    await Promise.resolve();
  });

  expect(screen.getByText("我建议你先明确网站主要目标。")).toBeInTheDocument();

  expect(fetchMock).toHaveBeenCalledWith(
    "http://127.0.0.1:5000/api/sessions/demo-token/messages",
    expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ content: "我想做一个个人网站" }),
    }),
  );

  setIntervalSpy.mockRestore();
  clearIntervalSpy.mockRestore();
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

test("需求页上传图片后会展示缩略图", async () => {
  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  const input = await screen.findByLabelText("上传参考图片");
  const file = new File(["png"], "reference.png", { type: "image/png" });

  fireEvent.change(input, { target: { files: [file] } });

  expect(await screen.findByRole("img", { name: "reference.png 缩略图" })).toBeInTheDocument();
});

test("上传失败时会展示后端返回的中文错误原因", async () => {
  fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);

    if (url.includes("/sessions/demo-token/attachments")) {
      return new Response(
        JSON.stringify({ message: "只支持 PNG、JPEG、WEBP 图片" }),
        { status: 400 },
      );
    }

    if (url.includes("/sessions/demo-token")) {
      return new Response(JSON.stringify(buildSessionResponse()), { status: 200 });
    }

    return new Response(JSON.stringify({}), { status: 200 });
  });

  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  const input = await screen.findByLabelText("上传参考图片");
  const file = new File(["pdf"], "bad.pdf", { type: "application/pdf" });

  fireEvent.change(input, { target: { files: [file] } });

  expect(await screen.findByText("只支持 PNG、JPEG、WEBP 图片")).toBeInTheDocument();
});

test("轮询不会立即清掉上传失败错误", async () => {
  let intervalCallback: (() => void) | null = null;
  const setIntervalSpy = vi.spyOn(window, "setInterval").mockImplementation(((callback) => {
    intervalCallback = () => {
      if (typeof callback === "function") {
        callback();
      }
    };
    return 1 as unknown as number;
  }) as typeof window.setInterval);
  const clearIntervalSpy = vi.spyOn(window, "clearInterval").mockImplementation(() => undefined);

  fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);

    if (url.includes("/sessions/demo-token/attachments")) {
      return new Response(
        JSON.stringify({ message: "只支持 PNG、JPEG、WEBP 图片" }),
        { status: 400 },
      );
    }

    if (url.includes("/sessions/demo-token")) {
      return new Response(JSON.stringify(buildSessionResponse()), { status: 200 });
    }

    return new Response(JSON.stringify({}), { status: 200 });
  });

  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  const input = await screen.findByLabelText("上传参考图片");
  const file = new File(["pdf"], "bad.pdf", { type: "application/pdf" });

  fireEvent.change(input, { target: { files: [file] } });

  expect(await screen.findByText("只支持 PNG、JPEG、WEBP 图片")).toBeInTheDocument();

  await act(async () => {
    intervalCallback?.();
    await Promise.resolve();
  });

  expect(screen.getByText("只支持 PNG、JPEG、WEBP 图片")).toBeInTheDocument();

  setIntervalSpy.mockRestore();
  clearIntervalSpy.mockRestore();
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
