import type { ReactNode } from "react";

import { BACK_OFFICE_ITEMS, PARTS } from "./parts";
import { SideBar } from "./SideBar";
import { StatusBar } from "./StatusBar";
import { TitleBar } from "./TitleBar";
import { Window } from "./Window";

export interface BackOfficeFrameProps {
  active?: string;
  operatorName?: string;
  statusItems?: readonly ReactNode[];
  onSelect?: (id: string) => void;
  children?: ReactNode;
}

export function BackOfficeFrame({
  active = BACK_OFFICE_ITEMS[0].id,
  operatorName,
  statusItems,
  onSelect,
  children,
}: BackOfficeFrameProps): ReactNode {
  const context = operatorName === undefined ? [] : [operatorName];
  return (
    <Window
      titleBar={<TitleBar part={PARTS.backOffice.name} context={context} />}
      sideBar={<SideBar items={BACK_OFFICE_ITEMS} active={active} onSelect={onSelect} />}
      statusBar={<StatusBar items={statusItems} />}
    >
      {children}
    </Window>
  );
}
