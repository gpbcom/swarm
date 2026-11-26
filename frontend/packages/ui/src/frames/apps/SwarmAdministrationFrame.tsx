import type { ReactNode } from "react";

import { PARTS, SWARM_ADMINISTRATION_ITEMS } from "../parts";
import { SideBar } from "../shell/SideBar";
import { StatusBar } from "../shell/StatusBar";
import { TitleBar } from "../shell/TitleBar";
import { Window } from "../shell/Window";

export interface SwarmAdministrationFrameProps {
  active?: string;
  statusItems?: readonly ReactNode[];
  onSelect?: (id: string) => void;
  children?: ReactNode;
}

export function SwarmAdministrationFrame({
  active = SWARM_ADMINISTRATION_ITEMS[0].id,
  statusItems,
  onSelect,
  children,
}: SwarmAdministrationFrameProps): ReactNode {
  return (
    <Window
      titleBar={<TitleBar part={PARTS.swarmAdministration.name} context={[PARTS.swarmAdministration.context]} />}
      sideBar={<SideBar items={SWARM_ADMINISTRATION_ITEMS} active={active} onSelect={onSelect} />}
      statusBar={<StatusBar items={statusItems} />}
    >
      {children}
    </Window>
  );
}
