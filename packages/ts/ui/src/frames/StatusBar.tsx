import { Fragment } from "react";
import type { ReactNode } from "react";

export interface StatusBarProps {
  items?: readonly ReactNode[] | undefined;
}

export function StatusBar({ items = [] }: StatusBarProps): ReactNode {
  return (
    <footer className="statusbar">
      {items.map((item, index) => (
        <Fragment key={index}>
          {index > 0 ? " · " : null}
          <span>{item}</span>
        </Fragment>
      ))}
    </footer>
  );
}
