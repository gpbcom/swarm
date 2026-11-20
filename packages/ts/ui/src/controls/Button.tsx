import type { ButtonHTMLAttributes } from "react";

export type ButtonVariant = "primary" | "secondary" | "danger";

export interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "className"> {
  variant: ButtonVariant;
}

export function Button({ variant, type = "button", ...rest }: ButtonProps) {
  return <button {...rest} type={type} className={`button ${variant}`} />;
}
