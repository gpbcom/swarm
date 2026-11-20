import type { ReactNode } from "react";

import { Button } from "../controls";
import { GROUND_CONTROL_ITEMS, GROUND_CONTROL_LABELS, PARTS } from "./parts";
import { SideBar } from "./SideBar";
import { StatusBar } from "./StatusBar";
import { TitleBar } from "./TitleBar";
import { Window } from "./Window";

export interface GroundControlFrameProps {
  active?: string;
  missionName?: string;
  missionState?: string;
  statusItems?: readonly ReactNode[];
  onSelect?: (id: string) => void;
  onHold?: () => void;
  onAbort?: () => void;
  children?: ReactNode;
}

export function GroundControlFrame({
  active = GROUND_CONTROL_ITEMS[0].id,
  missionName,
  missionState,
  statusItems,
  onSelect,
  onHold,
  onAbort,
  children,
}: GroundControlFrameProps): ReactNode {
  const context = [missionName, missionState].filter((entry): entry is string => entry !== undefined);
  return (
    <Window
      titleBar={
        <TitleBar
          part={PARTS.groundControl.name}
          context={context}
          actions={
            <>
              <Button variant="secondary" onClick={onHold}>
                {GROUND_CONTROL_LABELS.hold}
              </Button>
              <Button variant="danger" onClick={onAbort}>
                {GROUND_CONTROL_LABELS.abort}
              </Button>
            </>
          }
        />
      }
      sideBar={<SideBar items={GROUND_CONTROL_ITEMS} active={active} onSelect={onSelect} />}
      statusBar={<StatusBar items={statusItems} />}
    >
      {children}
    </Window>
  );
}
