import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-amber/55 disabled:pointer-events-none disabled:opacity-50",
        variant === "primary" && "bg-amber text-ink hover:bg-amber/90",
        variant === "secondary" && "border border-border-soft bg-panel-2 text-text-1 hover:border-text-2/50",
        variant === "ghost" && "text-text-2 hover:bg-panel-2 hover:text-text-1",
        className
      )}
      {...props}
    />
  );
}
