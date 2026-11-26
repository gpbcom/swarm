import * as RadixToast from "@radix-ui/react-toast";
import type { ReactNode } from "react";

export type ToastKind = "success" | "failure";

export interface ToastProps {
  kind: ToastKind;
  icon: ReactNode;
  message: ReactNode;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export interface ToastProviderProps {
  children: ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
  return (
    <RadixToast.Provider>
      {children}
      <RadixToast.Viewport />
    </RadixToast.Provider>
  );
}

export function Toast({ kind, icon, message, open, onOpenChange }: ToastProps) {
  return (
    <RadixToast.Root className={`toast ${kind}`} open={open} onOpenChange={onOpenChange}>
      <span aria-hidden="true">{icon}</span>
      <RadixToast.Title>{message}</RadixToast.Title>
    </RadixToast.Root>
  );
}
