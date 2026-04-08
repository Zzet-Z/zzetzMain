import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "../app";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/sessions")) {
        return new Response(JSON.stringify({ token: "demo-token" }), { status: 201 });
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
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
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

test("首页 CTA 点击后进入 loading 状态", async () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  fireEvent.click(screen.getAllByRole("button", { name: "开始梳理我的网站" })[0]);

  expect(await screen.findAllByRole("button", { name: "正在准备梳理页..." })).toHaveLength(2);
});
