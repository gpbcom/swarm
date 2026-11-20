import * as Label from "@radix-ui/react-label";
import type { InputHTMLAttributes } from "react";

export interface FieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "className" | "id"> {
  id: string;
  label: string;
  hint?: string;
  error?: string;
}

export function Field({ id, label, hint, error, ...rest }: FieldProps) {
  const messageId = error ? `${id}-error` : hint ? `${id}-hint` : undefined;
  return (
    <div className="field">
      <Label.Root htmlFor={id}>{label}</Label.Root>
      <input
        {...rest}
        id={id}
        className={error ? "input invalid" : "input"}
        aria-invalid={error ? true : undefined}
        aria-describedby={messageId}
      />
      {error ? (
        <p id={messageId} className="error" role="alert">
          {error}
        </p>
      ) : hint ? (
        <p id={messageId} className="hint">
          {hint}
        </p>
      ) : null}
    </div>
  );
}
