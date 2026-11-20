import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Card, Conversation, Kpi, Kpis, List, ListItem, Message, Panel, Split, Table } from "../src/data";

describe("data components", () => {
  describe("Card", () => {
    it("renders a section card with a heading when it has a title", () => {
      const { container } = render(<Card title="Fleet">Body</Card>);
      expect(container.querySelector("section.card")).not.toBeNull();
      expect(container.querySelector("section.card h2")?.textContent).toBe("Fleet");
    });

    it("renders no heading without a title", () => {
      const { container } = render(<Card>Body</Card>);
      expect(container.querySelector("section.card")?.textContent).toBe("Body");
      expect(container.querySelector("h2")).toBeNull();
    });
  });

  describe("Table", () => {
    it("renders one th per column and one tr per row in the body", () => {
      const { container } = render(
        <Table
          columns={["Name", "State"]}
          rows={[
            ["A", "Ready"],
            ["B", "Down"],
            ["C", "Ready"],
          ]}
        />,
      );
      expect(container.querySelector("table.table")).not.toBeNull();
      expect(container.querySelectorAll("th")).toHaveLength(2);
      expect(container.querySelectorAll("tbody tr")).toHaveLength(3);
    });
  });

  describe("List", () => {
    it("renders a ul list holding li list items", () => {
      const { container } = render(
        <List>
          <ListItem>One</ListItem>
        </List>,
      );
      expect(container.querySelector("ul.list")).not.toBeNull();
      expect(container.querySelector("ul.list li.list-item")?.textContent).toBe("One");
    });
  });

  describe("Split and Panel", () => {
    it("renders a split holding panels", () => {
      const { container } = render(
        <Split>
          <Panel>Left</Panel>
        </Split>,
      );
      expect(container.querySelector("div.split")).not.toBeNull();
      expect(container.querySelector("div.split div.panel")?.textContent).toBe("Left");
    });
  });

  describe("Kpis", () => {
    it("renders kpis holding a kpi with its value and label", () => {
      const { container } = render(
        <Kpis>
          <Kpi value="12" label="Drones" />
        </Kpis>,
      );
      expect(container.querySelector("div.kpis")).not.toBeNull();
      expect(container.querySelector("div.kpi .value")?.textContent).toBe("12");
      expect(container.querySelector("div.kpi .label")?.textContent).toBe("Drones");
    });
  });

  describe("Conversation", () => {
    it.each(["person", "agent"] as const)("renders a message from the %s", (from) => {
      const { container } = render(
        <Conversation>
          <Message from={from}>Hello</Message>
        </Conversation>,
      );
      expect(container.querySelector("div.conversation")).not.toBeNull();
      expect(container.querySelector(`div.conversation div.message.${from}`)?.textContent).toBe("Hello");
    });
  });
});
