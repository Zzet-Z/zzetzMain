import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "../app";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/sessions/demo-token")) {
        return new Response(
          JSON.stringify({
            token: "demo-token",
            status: "active",
            current_stage: "template",
            selected_template: null,
            selected_style: null,
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("首页展示五段式内容和主 CTA", () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>,
  );

  expect(
    screen.getByRole("heading", { level: 1, name: "把你想要的网站，说出来。" }),
  ).toBeInTheDocument();
  expect(
    screen.getByText(/先通过真实中文对话，把你的定位、内容和功能想清楚。/),
  ).toBeInTheDocument();
  expect(screen.getAllByRole("button", { name: "开始梳理我的网站" })).toHaveLength(2);
  expect(screen.getByRole("heading", { level: 2, name: "你不需要先会写 PRD" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { level: 2, name: "三步，把模糊想法变成可执行方案" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { level: 2, name: "最后你会拿到什么" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { level: 2, name: "准备开始你的首页梳理了吗？" })).toBeInTheDocument();
});

test("输入 token 后可以跳转到聊天页", () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>,
  );

  fireEvent.click(screen.getAllByRole("button", { name: "开始梳理我的网站" })[0]);
  fireEvent.change(screen.getByLabelText("访问 Token"), { target: { value: "demo-token" } });
  fireEvent.click(screen.getByRole("button", { name: "进入对话" }));

  return waitFor(() => {
    expect(window.location.pathname).toBe("/session/demo-token");
  });
});

test("点击首页 CTA 后会展示 token 输入区且不进入永久 loading", () => {
  window.history.pushState({}, "", "/");

  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>,
  );

  fireEvent.click(screen.getAllByRole("button", { name: "开始梳理我的网站" })[0]);

  expect(screen.getByRole("heading", { level: 2, name: "输入管理员签发的访问 Token" })).toBeInTheDocument();
  expect(screen.getByLabelText("访问 Token")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "正在准备梳理页..." })).not.toBeInTheDocument();
});
