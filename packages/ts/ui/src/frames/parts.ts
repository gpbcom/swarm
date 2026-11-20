export interface NavItem {
  id: string;
  icon: string;
  label: string;
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
  hold: "✋ Hold the Squad",
  abort: "🛑 Abort",
} as const;

export const GROUND_CONTROL_ITEMS = [
  { id: "flight", icon: "🛰️", label: "Flight" },
  { id: "preflight", icon: "📋", label: "Pre-flight" },
  { id: "squad", icon: "🛸", label: "Squad" },
  { id: "video", icon: "🎥", label: "Video" },
  { id: "debrief", icon: "📼", label: "Debrief" },
  { id: "settings", icon: "🔧", label: "Settings" },
] as const satisfies readonly NavItem[];

export const MISSION_STUDIO_ITEMS = [
  { id: "missions", icon: "🗺️", label: "Missions" },
  { id: "design", icon: "🖊️", label: "Design" },
  { id: "simulate", icon: "🕹️", label: "Simulate" },
  { id: "assistant", icon: "💬", label: "Assistant" },
] as const satisfies readonly NavItem[];

export const BACK_OFFICE_ITEMS = [
  { id: "fleet", icon: "🛸", label: "Fleet" },
  { id: "authorisations", icon: "📜", label: "Authorisations" },
  { id: "deliverables", icon: "📦", label: "Deliverables" },
  { id: "evidence", icon: "🔏", label: "Evidence" },
  { id: "people", icon: "👥", label: "People" },
  { id: "settings", icon: "🔧", label: "Settings" },
] as const satisfies readonly NavItem[];

export const CLIENT_PORTAL_ITEMS = [
  { id: "missions", icon: "🗺️", label: "Missions" },
  { id: "order", icon: "➕", label: "Order" },
  { id: "deliverables", icon: "📦", label: "Deliverables" },
  { id: "scorecards", icon: "🧾", label: "Scorecards" },
  { id: "alarms", icon: "🔔", label: "Alarms", siteAgentOnly: true },
] as const satisfies readonly ClientNavItem[];

export const SWARM_ADMINISTRATION_ITEMS = [
  { id: "operators", icon: "➕", label: "Operators" },
  { id: "people", icon: "👥", label: "People" },
  { id: "settings", icon: "🔧", label: "Settings" },
] as const satisfies readonly NavItem[];
