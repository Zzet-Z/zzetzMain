import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { SessionPage } from "../routes/session-page";

test("排队用户能看到等待文案", () => {
  render(<SessionPage initialState={{ status: "queued", queuePosition: 1 }} />);

  expect(screen.getByText(/当前正在为其他用户整理网站需求/)).toBeInTheDocument();
  expect(screen.getByText(/你前面还有 1 人/)).toBeInTheDocument();
});

test.each(["completed", "expired", "failed"] as const)(
  "%s 状态会禁用输入区",
  (status) => {
    render(<SessionPage initialState={{ status }} />);

    expect(screen.getByPlaceholderText("继续描述你的网站需求")).toBeDisabled();
    expect(screen.getByRole("button", { name: "发送" })).toBeDisabled();
  },
);
