export interface NavItem {
  id: string;
  icon: string;
  messageId: string;
}

export interface ClientNavItem extends NavItem {
  siteAgentOnly?: boolean;
}

export const APP_NAME = "⚙️ Swarm";

export const PARTS = {
  groundControl: { name: "Ground control" },
  missionStudio: { name: "Mission studio" },
  backOffice: { name: "Back office" },
  clientPortal: { name: "Client portal" },
  swarmAdministration: { name: "Back office", context: "Swarm administration" },
} as const;

export const GROUND_CONTROL_LABELS = {
  hold: { icon: "✋", messageId: "action.hold" },
  abort: { icon: "🛑", messageId: "action.abort" },
} as const;

export const GROUND_CONTROL_ITEMS = [
  { id: "flight", icon: "🛰️", messageId: "nav.flight" },
  { id: "preflight", icon: "📋", messageId: "nav.preflight" },
  { id: "squad", icon: "🛸", messageId: "nav.squad" },
  { id: "video", icon: "🎥", messageId: "nav.video" },
  { id: "debrief", icon: "📼", messageId: "nav.debrief" },
  { id: "settings", icon: "🔧", messageId: "nav.settings" },
] as const satisfies readonly NavItem[];

export const MISSION_STUDIO_ITEMS = [
  { id: "missions", icon: "🗺️", messageId: "nav.missions" },
  { id: "design", icon: "🖊️", messageId: "nav.design" },
  { id: "simulate", icon: "🕹️", messageId: "nav.simulate" },
  { id: "assistant", icon: "💬", messageId: "nav.assistant" },
] as const satisfies readonly NavItem[];

export const BACK_OFFICE_ITEMS = [
  { id: "fleet", icon: "🛸", messageId: "nav.fleet" },
  { id: "authorisations", icon: "📜", messageId: "nav.authorisations" },
  { id: "deliverables", icon: "📦", messageId: "nav.deliverables" },
  { id: "evidence", icon: "🔏", messageId: "nav.evidence" },
  { id: "people", icon: "👥", messageId: "nav.people" },
  { id: "settings", icon: "🔧", messageId: "nav.settings" },
] as const satisfies readonly NavItem[];

export const CLIENT_PORTAL_ITEMS = [
  { id: "missions", icon: "🗺️", messageId: "nav.missions" },
  { id: "order", icon: "➕", messageId: "nav.order" },
  { id: "deliverables", icon: "📦", messageId: "nav.deliverables" },
  { id: "scorecards", icon: "🧾", messageId: "nav.scorecards" },
  { id: "alarms", icon: "🔔", messageId: "nav.alarms", siteAgentOnly: true },
] as const satisfies readonly ClientNavItem[];

export const SWARM_ADMINISTRATION_ITEMS = [
  { id: "operators", icon: "➕", messageId: "nav.operators" },
  { id: "people", icon: "👥", messageId: "nav.people" },
  { id: "settings", icon: "🔧", messageId: "nav.settings" },
] as const satisfies readonly NavItem[];
