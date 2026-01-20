import { type ButtonHTMLAttributes, type ReactElement, type ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "ghost" | "accent";
  children: ReactNode;
}

export const Button = ({
  variant = "ghost",
  children,
  type = "button",
  ...props
}: ButtonProps): ReactElement => {
  const className = [
    "btn",
    variant === "accent" ? "btn--accent" : "btn--ghost",
    props.className || "",
  ]
    .join(" ")
    .trim();

  return (
    <button {...props} type={type} className={className}>
      {children}
    </button>
  );
};
