import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    loading?: boolean;
    variant?: "primary" | "secondary";
  }
>;

export function Button({
  children,
  className = "",
  disabled,
  loading = false,
  type = "button",
  variant = "primary",
  ...props
}: ButtonProps) {
  const variantClassName =
    variant === "primary"
      ? "bg-[var(--color-accent)] text-white hover:bg-[#1482f0]"
      : "border border-[rgba(255,255,255,0.24)] bg-transparent text-[var(--color-link-bright)] hover:border-[var(--color-link-bright)]";

  return (
    <button
      type={type}
      className={`inline-flex min-h-11 items-center justify-center rounded-full px-5 text-[17px] font-normal tracking-[0.01em] transition disabled:cursor-not-allowed disabled:opacity-70 ${variantClassName} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? "正在准备梳理页..." : children}
    </button>
  );
}
