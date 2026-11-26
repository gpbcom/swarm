import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Button, Field, Tabs } from "../src/controls";

describe("Button", () => {
  it.each(["primary", "secondary", "danger"] as const)("renders the %s variant", (variant) => {
    render(<Button variant={variant}>Go</Button>);
    expect(screen.getByRole("button", { name: "Go" }).className).toBe(`button ${variant}`);
  });

  it("defaults its type to button", () => {
    render(<Button variant="primary">Go</Button>);
    expect(screen.getByRole("button").getAttribute("type")).toBe("button");
  });

  it("uses the type it is given", () => {
    render(
      <Button variant="primary" type="submit">
        Go
      </Button>,
    );
    expect(screen.getByRole("button").getAttribute("type")).toBe("submit");
  });

  it("calls onClick when clicked", async () => {
    const onClick = vi.fn();
    render(
      <Button variant="primary" onClick={onClick}>
        Go
      </Button>,
    );
    await userEvent.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("does not call onClick when disabled", async () => {
    const onClick = vi.fn();
    render(
      <Button variant="primary" onClick={onClick} disabled>
        Go
      </Button>,
    );
    await userEvent.click(screen.getByRole("button"));
    expect(onClick).not.toHaveBeenCalled();
  });
});

describe("Field", () => {
  it("renders a field with a label tied to its input", () => {
    const { container } = render(<Field id="name" label="Name" />);
    expect(container.querySelector("div.field")).not.toBeNull();
    const input = screen.getByLabelText("Name");
    expect(input.id).toBe("name");
    expect(input.className).toBe("input");
  });

  it("shows a hint and describes the input with it", () => {
    const { container } = render(<Field id="name" label="Name" hint="Your name" />);
    const hint = container.querySelector("p.hint");
    expect(hint?.textContent).toBe("Your name");
    expect(hint?.id).toBeTruthy();
    expect(screen.getByLabelText("Name").getAttribute("aria-describedby")).toBe(hint?.id);
  });

  it("shows an error as an alert and marks the input invalid", () => {
    render(<Field id="name" label="Name" error="Required" />);
    const alert = screen.getByRole("alert");
    expect(alert.tagName).toBe("P");
    expect(alert.className).toBe("error");
    expect(alert.textContent).toBe("Required");
    const input = screen.getByLabelText("Name");
    expect(input.className).toBe("input invalid");
    expect(input.getAttribute("aria-invalid")).toBe("true");
  });

  it("shows no hint when there is an error", () => {
    const { container } = render(<Field id="name" label="Name" hint="Your name" error="Required" />);
    expect(container.querySelector("p.hint")).toBeNull();
  });

  it("is not invalid without an error", () => {
    render(<Field id="name" label="Name" />);
    expect(screen.getByLabelText("Name").getAttribute("aria-invalid")).not.toBe("true");
  });

  it("calls onChange on typing", async () => {
    const onChange = vi.fn();
    render(<Field id="name" label="Name" value="" onChange={onChange} />);
    await userEvent.type(screen.getByLabelText("Name"), "a");
    expect(onChange).toHaveBeenCalled();
  });
});

describe("Tabs", () => {
  const tabs = [
    { value: "one", label: "One", content: "First content" },
    { value: "two", label: "Two", content: "Second content" },
  ];

  it("renders a list of tabs with a trigger for each", () => {
    const { container } = render(<Tabs tabs={tabs} defaultValue="one" />);
    expect(container.querySelector(".tabs")).not.toBeNull();
    expect(container.querySelectorAll(".tab")).toHaveLength(2);
  });

  it("marks the selected trigger active and shows only its content", () => {
    render(<Tabs tabs={tabs} defaultValue="one" />);
    const one = screen.getByRole("tab", { name: "One" });
    expect(one.className).toBe("tab active");
    expect(one.getAttribute("aria-selected")).toBe("true");
    expect(screen.getByRole("tab", { name: "Two" }).className).toBe("tab");
    expect(screen.getByText("First content")).toBeTruthy();
    expect(screen.queryByText("Second content")).toBeNull();
  });

  it("moves the active tab and the content when another trigger is clicked", async () => {
    render(<Tabs tabs={tabs} defaultValue="one" />);
    await userEvent.click(screen.getByRole("tab", { name: "Two" }));
    const two = screen.getByRole("tab", { name: "Two" });
    expect(two.className).toBe("tab active");
    expect(two.getAttribute("aria-selected")).toBe("true");
    expect(screen.getByRole("tab", { name: "One" }).className).toBe("tab");
    expect(screen.getByText("Second content")).toBeTruthy();
    expect(screen.queryByText("First content")).toBeNull();
  });
});
