import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Dialog } from "../src/overlays";

describe("Dialog", () => {
  it("renders an overlay and a dialog named by its title when open", () => {
    render(
      <Dialog open onOpenChange={() => undefined} title="Confirm">
        Body
      </Dialog>,
    );
    const dialog = screen.getByRole("dialog", { name: "Confirm" });
    expect(dialog.className).toBe("dialog");
    const overlay = document.querySelector(".overlay");
    expect(overlay).not.toBeNull();
    expect(overlay?.parentElement).toBe(dialog.parentElement);
    expect(screen.getByText("Body")).toBeTruthy();
  });

  it("renders neither when closed", () => {
    render(
      <Dialog open={false} onOpenChange={() => undefined} title="Confirm">
        Body
      </Dialog>,
    );
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.querySelector(".overlay")).toBeNull();
  });

  it("calls onOpenChange with false on Escape", async () => {
    const onOpenChange = vi.fn();
    render(
      <Dialog open onOpenChange={onOpenChange} title="Confirm">
        Body
      </Dialog>,
    );
    await userEvent.keyboard("{Escape}");
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("renders its actions inside the dialog", () => {
    render(
      <Dialog open onOpenChange={() => undefined} title="Confirm" actions={<button type="button">Yes</button>}>
        Body
      </Dialog>,
    );
    const dialog = screen.getByRole("dialog", { name: "Confirm" });
    expect(dialog.contains(screen.getByRole("button", { name: "Yes" }))).toBe(true);
  });
});
