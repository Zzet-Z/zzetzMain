import "@testing-library/jest-dom/vitest";
import { render, screen, waitFor } from "@testing-library/react";
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

test("需求页展示步骤条与跳过入口", async () => {
  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  await waitFor(() => {
    expect(screen.getByText("模板")).toBeInTheDocument();
  });

  expect(screen.getByText("风格")).toBeInTheDocument();
  expect(screen.getAllByRole("button", { name: "跳过" }).length).toBeGreaterThan(0);
});
