import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { SessionPage } from "../routes/session-page";

test("排队用户能看到等待文案", () => {
  render(<SessionPage initialState={{ status: "queued", queuePosition: 1 }} />);

  expect(screen.getByText(/当前正在为其他用户整理网站需求/)).toBeInTheDocument();
  expect(screen.getByText(/你前面还有 1 人/)).toBeInTheDocument();
});
