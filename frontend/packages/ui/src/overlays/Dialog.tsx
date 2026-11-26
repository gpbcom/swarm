import * as RadixDialog from "@radix-ui/react-dialog";
import type { ReactNode } from "react";

export interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  actions?: ReactNode;
  children?: ReactNode;
}

export function Dialog({ open, onOpenChange, title, description, actions, children }: DialogProps) {
  return (
    <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
      <RadixDialog.Portal>
        <RadixDialog.Overlay className="overlay" />
        <RadixDialog.Content className="dialog">
          <RadixDialog.Title>{title}</RadixDialog.Title>
          {description ? <RadixDialog.Description>{description}</RadixDialog.Description> : null}
          {children}
          {actions}
        </RadixDialog.Content>
      </RadixDialog.Portal>
    </RadixDialog.Root>
  );
}
