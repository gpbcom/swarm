import type { ReactNode } from "react";

export type MessageSender = "person" | "agent";

export interface ConversationProps {
  children?: ReactNode;
}

export interface MessageProps {
  from: MessageSender;
  children?: ReactNode;
}

export function Conversation({ children }: ConversationProps) {
  return <div className="conversation">{children}</div>;
}

export function Message({ from, children }: MessageProps) {
  return <div className={`message ${from}`}>{children}</div>;
}
