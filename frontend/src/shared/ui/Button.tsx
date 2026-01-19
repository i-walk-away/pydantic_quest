import { type ButtonHTMLAttributes, type ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "ghost" | "accent";
  children: ReactNode;
}

export const Button = ({ variant = "ghost", children, ...props }: ButtonProps): JSX.Element => {
  const className = [
    "btn",
    variant === "accent" ? "btn--accent" : "btn--ghost",
    props.className || "",
  ]
    .join(" ")
    .trim();

  return (
    <button {...props} className={className}>
      {children}
    </button>
  );
};
