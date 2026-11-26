import type { ReactNode } from "react";

export interface ListProps {
  children?: ReactNode;
}

export function List({ children }: ListProps) {
  return <ul className="list">{children}</ul>;
}

export function ListItem({ children }: ListProps) {
  return <li className="list-item">{children}</li>;
}
