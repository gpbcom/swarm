import type { ReactNode } from "react";

import { PARTS, SWARM_ADMINISTRATION_ITEMS } from "./parts";
import { SideBar } from "./SideBar";
import { StatusBar } from "./StatusBar";
import { TitleBar } from "./TitleBar";
import { Window } from "./Window";

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
