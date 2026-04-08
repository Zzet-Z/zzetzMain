import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "../app";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/sessions")) {
        return new Response(JSON.stringify({ token: "demo-token" }), { status: 201 });
      }
      if (url.includes("/sessions/demo-token/messages")) {
        return new Response(
          JSON.stringify({
            assistant_reply: "请继续告诉我你的网站主要给谁看。",
            current_stage: "positioning",
            session_status: "active",
            poll_after_ms: 3000,
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
      if (url.includes("/sessions/demo-token") && init?.method === "PATCH") {
        const body = JSON.parse(String(init.body ?? "{}"));
        return new Response(
          JSON.stringify({
            token: "demo-token",
            status: "draft",
            current_stage: body.current_stage ?? "template",
            selected_template: body.selected_template ?? null,
            selected_style: body.selected_style ?? null,
            summary: { payload: {} },
            document: { status: "pending" },
          }),
          { status: 200 },
        );
      }
      if (url.includes("/sessions/demo-token")) {
        return new Response(
          JSON.stringify({
            token: "demo-token",
            status: "draft",
            current_stage: "template",
            selected_template: null,
            selected_style: null,
            summary: { payload: {} },
            document: { status: "pending" },
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

test("首页点击开始后进入需求页", async () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  fireEvent.click(screen.getAllByRole("button", { name: "开始梳理我的网站" })[0]);

  expect(await screen.findByText("模板")).toBeInTheDocument();
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

  expect(await screen.findByText(/reference\.png - 参考图片/)).toBeInTheDocument();
});
