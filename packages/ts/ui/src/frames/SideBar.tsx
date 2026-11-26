import type { ReactNode } from "react";
import { useIntl } from "react-intl";

import type { NavItem } from "./parts";

export interface SideBarProps {
  items: readonly NavItem[];
  active: string;
  onSelect?: ((id: string) => void) | undefined;
}

export function SideBar({ items, active, onSelect }: SideBarProps): ReactNode {
  const intl = useIntl();
  return (
    <nav className="sidebar">
      {items.map((item) => {
        const current = item.id === active;
        return (
          <button
            key={item.id}
            type="button"
            className={current ? "nav-item active" : "nav-item"}
            aria-current={current ? "page" : undefined}
            onClick={() => onSelect?.(item.id)}
          >
            <span aria-hidden="true">{item.icon}</span> {intl.formatMessage({ id: item.messageId })}
          </button>
        );
      })}
    </nav>
  );
}
