import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { expect, test } from "vitest";
import { App } from "../app";

test("首页 CTA 点击后会展开 token 输入区", () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>,
  );

  fireEvent.click(screen.getAllByRole("button", { name: "开始梳理我的网站" })[0]);

  expect(screen.getByLabelText("访问 Token")).toBeInTheDocument();
});
