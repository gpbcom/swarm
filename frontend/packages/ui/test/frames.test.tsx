import { createElement } from "react";
import type { ReactElement } from "react";
import { render as renderBare, screen } from "@testing-library/react";
import type { RenderResult } from "@testing-library/react";
import { I18nProvider } from "@swarm/i18n";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  BackOfficeFrame,
  ClientPortalFrame,
  GroundControlFrame,
  MissionStudioFrame,
  SideBar,
  StatusBar,
  SwarmAdministrationFrame,
  TitleBar,
  Window,
} from "../src/frames";
import * as ui from "../src/index";

interface FrameCase {
  name: string;
  part: string;
  items: string[];
  lastId: string;
  build: (children: ReactElement, extra?: Record<string, unknown>) => ReactElement;
}

const FRAMES: FrameCase[] = [
  {
    name: "GroundControlFrame",
    part: "Ground control",
    items: ["🛰️ Flight", "📋 Pre-flight", "🛸 Squad", "🎥 Video", "📼 Debrief", "🔧 Settings"],
    lastId: "settings",
    build: (children, extra) => createElement(GroundControlFrame, { ...extra }, children),
  },
  {
    name: "MissionStudioFrame",
    part: "Mission studio",
    items: ["🗺️ Missions", "🖊️ Design", "🕹️ Simulate", "💬 Assistant"],
    lastId: "assistant",
    build: (children, extra) => createElement(MissionStudioFrame, { ...extra }, children),
  },
  {
    name: "BackOfficeFrame",
    part: "Back office",
    items: ["🛸 Fleet", "📜 Authorisations", "📦 Deliverables", "🔏 Evidence", "👥 People", "🔧 Settings"],
    lastId: "settings",
    build: (children, extra) => createElement(BackOfficeFrame, { ...extra }, children),
  },
  {
    name: "ClientPortalFrame",
    part: "Client portal",
    items: ["🗺️ Missions", "➕ Order", "📦 Deliverables", "🧾 Scorecards"],
    lastId: "scorecards",
    build: (children, extra) => createElement(ClientPortalFrame, { ...extra }, children),
  },
  {
    name: "SwarmAdministrationFrame",
    part: "Back office",
    items: ["➕ Operators", "👥 People", "🔧 Settings"],
    lastId: "settings",
    build: (children, extra) => createElement(SwarmAdministrationFrame, { ...extra }, children),
  },
];

function render(ui: ReactElement, language = "en"): RenderResult {
  return renderBare(<I18nProvider language={language}>{ui}</I18nProvider>);
}

function navLabels(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll("nav.sidebar .nav-item")).map((item) =>
    item.textContent.replace(/\s+/g, " ").trim(),
  );
}

function labelOf(item: string | undefined): string {
  return (item ?? "").split(" ").slice(1).join(" ");
}

describe("Window", () => {
  it("renders the title bar, the side bar with the content, then the status bar", () => {
    const { container } = render(
      <Window
        titleBar={<header className="titlebar">T</header>}
        sideBar={<nav className="sidebar">S</nav>}
        statusBar={<footer className="statusbar">F</footer>}
      >
        <p>Body</p>
      </Window>,
    );
    const root = container.querySelector("div.window");
    expect(root).not.toBeNull();
    const kids = Array.from(root?.children ?? []);
    expect(kids[0]?.matches("header.titlebar")).toBe(true);
    expect(kids[1]?.matches("div.layout")).toBe(true);
    expect(kids[2]?.matches("footer.statusbar")).toBe(true);
    const layout = kids[1];
    expect(layout?.children[0]?.matches("nav.sidebar")).toBe(true);
    expect(layout?.querySelector("main.content")?.textContent).toBe("Body");
  });
});

describe("TitleBar", () => {
  it("starts with the app name, then the part, then the context separated by dots", () => {
    const { container } = render(<TitleBar part="Ground control" context={["Mission A", "Armed"]} />);
    const bar = container.querySelector("header.titlebar");
    expect(bar).not.toBeNull();
    expect(bar?.querySelector("span.app")?.textContent).toBe("⚙️ Swarm");
    const text = (bar?.textContent ?? "").replace(/\s+/g, " ");
    expect(text).toContain("Ground control");
    expect(text).toContain("Mission A · Armed");
    expect(text.indexOf("⚙️ Swarm")).toBeLessThan(text.indexOf("Ground control"));
    expect(text.indexOf("Ground control")).toBeLessThan(text.indexOf("Mission A"));
  });

  it("shows the actions", () => {
    render(<TitleBar part="Back office" actions={<button>Act</button>} />);
    expect(screen.getByRole("button", { name: "Act" })).toBeTruthy();
  });
});

describe("SideBar", () => {
  const items = [
    { id: "one", icon: "1️⃣", messageId: "nav.flight" },
    { id: "two", icon: "2️⃣", messageId: "nav.squad" },
  ];

  it("renders one nav item per item with its icon and label", () => {
    const { container } = render(<SideBar items={items} active="one" />);
    expect(container.querySelector("nav.sidebar")).not.toBeNull();
    const rendered = container.querySelectorAll(".nav-item");
    expect(rendered.length).toBe(2);
    expect(rendered[1]?.textContent).toContain("2️⃣");
    expect(rendered[1]?.textContent).toContain("Squad");
  });

  it("marks only the active item", () => {
    const { container } = render(<SideBar items={items} active="two" />);
    const rendered = container.querySelectorAll(".nav-item");
    expect(rendered[0]?.className).not.toContain("active");
    expect(rendered[1]?.className).toBe("nav-item active");
    expect(rendered[1]?.getAttribute("aria-current")).toBe("page");
    expect(rendered[0]?.getAttribute("aria-current")).toBeNull();
  });

  it("calls onSelect with the id of the clicked item", async () => {
    const onSelect = vi.fn();
    const { container } = render(<SideBar items={items} active="one" onSelect={onSelect} />);
    await userEvent.click(container.querySelectorAll(".nav-item")[1] as HTMLElement);
    expect(onSelect).toHaveBeenCalledWith("two");
  });
});

describe("French", () => {
  it("shows the side bar items and the Hold and Abort buttons in French", () => {
    const { container } = render(<GroundControlFrame />, "fr");
    expect(navLabels(container)).toEqual([
      "🛰️ Vol",
      "📋 Pré-vol",
      "🛸 Escadrille",
      "🎥 Vidéo",
      "📼 Débriefing",
      "🔧 Paramètres",
    ]);
    const buttons = Array.from(container.querySelectorAll("header.titlebar button")).map((b) => b.textContent);
    expect(buttons).toEqual(["✋ Mettre l'escadrille en attente", "🛑 Interrompre"]);
    expect(container.querySelector("header.titlebar")?.textContent).toContain("Ground control");
  });
});

describe("StatusBar", () => {
  it("renders the items separated by dots", () => {
    const { container } = render(<StatusBar items={["Link up", "Battery 80%"]} />);
    const bar = container.querySelector("footer.statusbar");
    expect(bar).not.toBeNull();
    expect((bar?.textContent ?? "").replace(/\s+/g, " ")).toContain("Link up · Battery 80%");
  });
});

describe.each(FRAMES)("$name", (frame) => {
  it("shows the app name and the part name in the title bar", () => {
    const { container } = render(frame.build(<p>x</p>));
    const bar = container.querySelector("header.titlebar");
    expect(bar?.querySelector("span.app")?.textContent).toBe("⚙️ Swarm");
    expect(bar?.textContent).toContain(frame.part);
  });

  it("lists the side bar items in order", () => {
    const { container } = render(frame.build(<p>x</p>));
    expect(navLabels(container)).toEqual(frame.items);
  });

  it("activates the first item by default", () => {
    const { container } = render(frame.build(<p>x</p>));
    const active = container.querySelectorAll(".nav-item.active");
    expect(active.length).toBe(1);
    expect(active[0]?.getAttribute("aria-current")).toBe("page");
    expect(active[0]?.textContent).toContain(labelOf(frame.items[0]));
  });

  it("activates the item chosen by the active prop", () => {
    const { container } = render(frame.build(<p>x</p>, { active: frame.lastId }));
    const active = container.querySelectorAll(".nav-item.active");
    expect(active.length).toBe(1);
    expect(active[0]?.textContent).toContain(labelOf(frame.items[frame.items.length - 1]));
  });

  it("renders the children inside the content", () => {
    const { container } = render(frame.build(<p>Child text</p>));
    expect(container.querySelector("main.content")?.textContent).toContain("Child text");
  });

  it("renders the status items in the status bar", () => {
    const { container } = render(frame.build(<p>x</p>, { statusItems: ["Alpha", "Beta"] }));
    const text = (container.querySelector("footer.statusbar")?.textContent ?? "").replace(/\s+/g, " ");
    expect(text).toContain("Alpha · Beta");
  });
});

describe("GroundControlFrame", () => {
  it("always shows Hold and Abort in the title bar and calls their handlers", async () => {
    const onHold = vi.fn();
    const onAbort = vi.fn();
    const { container } = render(<GroundControlFrame onHold={onHold} onAbort={onAbort} />);
    const bar = container.querySelector("header.titlebar");
    const hold = bar?.querySelector("button.button.secondary");
    const abort = bar?.querySelector("button.button.danger");
    if (!hold || !abort) {
      throw new Error("The title bar has no Hold or Abort button.");
    }
    expect(hold.textContent).toBe("✋ Hold the Squad");
    expect(abort.textContent).toBe("🛑 Abort");
    await userEvent.click(hold);
    await userEvent.click(abort);
    expect(onHold).toHaveBeenCalledTimes(1);
    expect(onAbort).toHaveBeenCalledTimes(1);
  });

  it("shows the mission name and state in the title bar", () => {
    const { container } = render(<GroundControlFrame missionName="Survey 7" missionState="Flying" />);
    const text = container.querySelector("header.titlebar")?.textContent ?? "";
    expect(text).toContain("Survey 7");
    expect(text).toContain("Flying");
  });
});

describe("MissionStudioFrame", () => {
  it("shows the mission name and state in the title bar", () => {
    const { container } = render(<MissionStudioFrame missionName="Survey 7" missionState="Draft" />);
    const text = container.querySelector("header.titlebar")?.textContent ?? "";
    expect(text).toContain("Survey 7");
    expect(text).toContain("Draft");
  });
});

describe("BackOfficeFrame", () => {
  it("shows the operator name in the title bar", () => {
    const { container } = render(<BackOfficeFrame operatorName="Acme Drones" />);
    expect(container.querySelector("header.titlebar")?.textContent).toContain("Acme Drones");
  });
});

describe("ClientPortalFrame", () => {
  it("shows the client name in the title bar", () => {
    const { container } = render(<ClientPortalFrame clientName="Farm Co" />);
    expect(container.querySelector("header.titlebar")?.textContent).toContain("Farm Co");
  });

  it("adds Alarms last when the user is a site agent", () => {
    const { container } = render(<ClientPortalFrame isSiteAgent />);
    expect(navLabels(container)).toEqual([
      "🗺️ Missions",
      "➕ Order",
      "📦 Deliverables",
      "🧾 Scorecards",
      "🔔 Alarms",
    ]);
  });

  it("leaves Alarms out when the user is not a site agent", () => {
    const { container } = render(<ClientPortalFrame isSiteAgent={false} />);
    expect(navLabels(container)).not.toContain("🔔 Alarms");
  });
});

describe("SwarmAdministrationFrame", () => {
  it("shows the Back office part with the Swarm administration context", () => {
    const { container } = render(<SwarmAdministrationFrame />);
    const text = container.querySelector("header.titlebar")?.textContent ?? "";
    expect(text).toContain("Back office");
    expect(text).toContain("Swarm administration");
  });
});

describe("index", () => {
  const NAMES = [
    "Window",
    "TitleBar",
    "SideBar",
    "StatusBar",
    "GroundControlFrame",
    "MissionStudioFrame",
    "BackOfficeFrame",
    "ClientPortalFrame",
    "SwarmAdministrationFrame",
    "Row",
    "Stack",
    "Grid2",
    "Spacer",
    "Muted",
    "Mono",
    "Button",
    "Field",
    "Tabs",
    "Dialog",
    "Badge",
    "Banner",
    "Toast",
    "ToastProvider",
    "Progress",
    "Checklist",
    "EmptyState",
    "Card",
    "Table",
    "List",
    "ListItem",
    "Split",
    "Panel",
    "Kpis",
    "Kpi",
    "Conversation",
    "Message",
  ];

  it.each(NAMES)("re-exports %s", (name) => {
    expect(Object.keys(ui)).toContain(name);
  });
});
