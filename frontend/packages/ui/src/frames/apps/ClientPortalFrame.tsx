import type { ReactNode } from "react";

import { CLIENT_PORTAL_ITEMS, PARTS } from "../parts";
import type { ClientNavItem } from "../parts";
import { SideBar } from "../shell/SideBar";
import { StatusBar } from "../shell/StatusBar";
import { TitleBar } from "../shell/TitleBar";
import { Window } from "../shell/Window";

export interface ClientPortalFrameProps {
  active?: string;
  clientName?: string;
  isSiteAgent?: boolean;
  statusItems?: readonly ReactNode[];
  onSelect?: (id: string) => void;
  children?: ReactNode;
}

export function ClientPortalFrame({
  active = CLIENT_PORTAL_ITEMS[0].id,
  clientName,
  isSiteAgent = false,
  statusItems,
  onSelect,
  children,
}: ClientPortalFrameProps): ReactNode {
  const context = clientName === undefined ? [] : [clientName];
  const items = CLIENT_PORTAL_ITEMS.filter(
    (item: ClientNavItem) => isSiteAgent || item.siteAgentOnly !== true,
  );
  return (
    <Window
      titleBar={<TitleBar part={PARTS.clientPortal.name} context={context} />}
      sideBar={<SideBar items={items} active={active} onSelect={onSelect} />}
      statusBar={<StatusBar items={statusItems} />}
    >
      {children}
    </Window>
  );
}
