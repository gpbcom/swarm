import type { ReactNode } from "react";

export interface WindowProps {
  titleBar: ReactNode;
  sideBar: ReactNode;
  statusBar: ReactNode;
  children?: ReactNode;
}

export function Window({ titleBar, sideBar, statusBar, children }: WindowProps): ReactNode {
  return (
    <div className="window">
      {titleBar}
      <div className="layout">
        {sideBar}
        <main className="content">{children}</main>
      </div>
      {statusBar}
    </div>
  );
}
