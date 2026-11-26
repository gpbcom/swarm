import type { ReactNode } from "react";

export interface CardProps {
  title?: ReactNode;
  children?: ReactNode;
}

export function Card({ title, children }: CardProps) {
  return (
    <section className="card">
      {title === undefined ? null : <h2>{title}</h2>}
      {children}
    </section>
  );
}
