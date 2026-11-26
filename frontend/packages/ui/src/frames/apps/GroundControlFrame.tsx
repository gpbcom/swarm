import type { ReactNode } from "react";
import { useIntl } from "react-intl";

import { Button } from "../../controls";
import { GROUND_CONTROL_ITEMS, GROUND_CONTROL_LABELS, PARTS } from "../parts";
import { SideBar } from "../shell/SideBar";
import { StatusBar } from "../shell/StatusBar";
import { TitleBar } from "../shell/TitleBar";
import { Window } from "../shell/Window";

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
  const intl = useIntl();
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
                {GROUND_CONTROL_LABELS.hold.icon} {intl.formatMessage({ id: GROUND_CONTROL_LABELS.hold.messageId })}
              </Button>
              <Button variant="danger" onClick={onAbort}>
                {GROUND_CONTROL_LABELS.abort.icon} {intl.formatMessage({ id: GROUND_CONTROL_LABELS.abort.messageId })}
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
