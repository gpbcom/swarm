import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge, Banner, Checklist, EmptyState, Progress, Toast, ToastProvider } from "../src/feedback";

const BADGE_KINDS = ["persona", "entity", "system", "success", "failure", "decision", "action"] as const;
const BANNER_ROLES = [
  ["success", "status"],
  ["failure", "alert"],
  ["decision", "alert"],
  ["system", "status"],
] as const;
const PROGRESS_CASES = [
  [0, null],
  [34, "p30"],
  [35, "p40"],
  [100, "p100"],
] as const;

describe("feedback components", () => {
  describe("Badge", () => {
    it.each(BADGE_KINDS)("renders a %s badge with a hidden icon and its label", (kind) => {
      const { container } = render(<Badge kind={kind} icon="*" label="Word" />);
      const badge = container.querySelector(`span.badge.${kind}`);
      expect(badge).not.toBeNull();
      expect(badge?.querySelector('[aria-hidden="true"]')?.textContent).toBe("*");
      expect(badge?.textContent).toContain("Word");
    });
  });

  describe("Banner", () => {
    it.each(BANNER_ROLES)("renders a %s banner with the role %s", (kind, role) => {
      const { container } = render(
        <Banner kind={kind} icon="!">
          Message
        </Banner>,
      );
      const banner = container.querySelector(`div.banner.${kind}`);
      expect(banner).not.toBeNull();
      expect(banner?.getAttribute("role")).toBe(role);
      expect(banner?.textContent).toContain("Message");
    });
  });

  describe("Toast", () => {
    it.each(["success", "failure"] as const)("shows an open %s toast with its icon and message", (kind) => {
      render(
        <ToastProvider>
          <Toast kind={kind} icon="#" message="Saved" open={true} onOpenChange={() => undefined} />
        </ToastProvider>,
      );
      const toast = document.querySelector(`.toast.${kind}`);
      expect(toast).not.toBeNull();
      expect(toast?.textContent).toContain("#");
      expect(toast?.textContent).toContain("Saved");
    });

    it("shows nothing when it is closed", () => {
      render(
        <ToastProvider>
          <Toast kind="success" icon="#" message="Saved" open={false} onOpenChange={() => undefined} />
        </ToastProvider>,
      );
      expect(document.querySelector(".toast")).toBeNull();
    });
  });

  describe("Progress", () => {
    it.each(PROGRESS_CASES)("renders the value %i with the indicator class %s", (value, indicator) => {
      render(<Progress value={value} label="Upload" />);
      const bar = screen.getByRole("progressbar");
      expect(bar.getAttribute("aria-valuenow")).toBe(String(value));
      expect(bar.classList.contains("progress")).toBe(true);
      const span = bar.querySelector("span");
      expect(span).not.toBeNull();
      const pClasses = Array.from(span?.classList ?? []).filter((name) => /^p\d+$/.test(name));
      expect(pClasses).toEqual(indicator === null ? [] : [indicator]);
    });

    it("adds the kind to the class when one is given", () => {
      render(<Progress value={50} label="Upload" kind="success" />);
      expect(screen.getByRole("progressbar").classList.contains("success")).toBe(true);
    });
  });

  describe("Checklist", () => {
    it("renders one prefixed item per status", () => {
      const { container } = render(
        <Checklist
          items={[
            { label: "Battery", status: "ok" },
            { label: "Link", status: "fail" },
            { label: "GPS", status: "pending" },
          ]}
        />,
      );
      const list = container.querySelector("ul.checklist");
      expect(list).not.toBeNull();
      expect(list?.querySelectorAll("li.check")).toHaveLength(3);
      expect(list?.querySelector("li.check.ok")?.textContent).toContain("✅");
      expect(list?.querySelector("li.check.fail")?.textContent).toContain("❌");
      expect(list?.querySelector("li.check.pending")?.textContent).toContain("⏳");
      expect(list?.querySelector("li.check.ok")?.textContent).toContain("Battery");
    });
  });

  describe("EmptyState", () => {
    it("renders the icon, the message and the action", () => {
      const { container } = render(<EmptyState icon="o" message="Nothing here" action={<button>Add</button>} />);
      const empty = container.querySelector("div.empty");
      expect(empty).not.toBeNull();
      expect(empty?.textContent).toContain("o");
      expect(empty?.textContent).toContain("Nothing here");
      expect(screen.getByRole("button").textContent).toBe("Add");
    });
  });
});
