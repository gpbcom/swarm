import { Fragment } from "react";
import type { ReactNode } from "react";

import { Spacer } from "../../layout";
import { APP_NAME } from "../parts";

export interface TitleBarProps {
  part: string;
  context?: readonly ReactNode[] | undefined;
  actions?: ReactNode | undefined;
}

export function TitleBar({ part, context = [], actions }: TitleBarProps): ReactNode {
  const trail = [part, ...context];
  return (
    <header className="titlebar">
      <span className="app">{APP_NAME}</span>
      {trail.map((entry, index) => (
        <Fragment key={index}>
          {" · "}
          <span className="screen-title">{entry}</span>
        </Fragment>
      ))}
      {actions ? (
        <>
          <Spacer />
          {actions}
        </>
      ) : null}
    </header>
  );
}
