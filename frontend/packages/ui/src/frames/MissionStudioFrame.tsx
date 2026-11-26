import type { ReactNode } from "react";

import { MISSION_STUDIO_ITEMS, PARTS } from "./parts";
import { SideBar } from "./SideBar";
import { StatusBar } from "./StatusBar";
import { TitleBar } from "./TitleBar";
import { Window } from "./Window";

export interface MissionStudioFrameProps {
  active?: string;
  missionName?: string;
  missionState?: string;
  statusItems?: readonly ReactNode[];
  onSelect?: (id: string) => void;
  children?: ReactNode;
}

export function MissionStudioFrame({
  active = MISSION_STUDIO_ITEMS[0].id,
  missionName,
  missionState,
  statusItems,
  onSelect,
  children,
}: MissionStudioFrameProps): ReactNode {
  const context = [missionName, missionState].filter((entry): entry is string => entry !== undefined);
  return (
    <Window
      titleBar={<TitleBar part={PARTS.missionStudio.name} context={context} />}
      sideBar={<SideBar items={MISSION_STUDIO_ITEMS} active={active} onSelect={onSelect} />}
      statusBar={<StatusBar items={statusItems} />}
    >
      {children}
    </Window>
  );
}
