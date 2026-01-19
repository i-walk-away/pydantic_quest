import { type AnchorHTMLAttributes, type ReactNode } from "react";
import { Link, type LinkProps } from "react-router-dom";

interface LinkButtonProps extends Omit<LinkProps, "to">, AnchorHTMLAttributes<HTMLAnchorElement> {
  to: string;
  variant?: "ghost" | "accent";
  children: ReactNode;
}

export const LinkButton = ({ variant = "ghost", children, to, className, ...props }: LinkButtonProps): JSX.Element => {
  const combinedClassName = [
    "btn",
    variant === "accent" ? "btn--accent" : "btn--ghost",
    className || "",
  ]
    .join(" ")
    .trim();

  return (
    <Link {...props} to={to} className={combinedClassName}>
      {children}
    </Link>
  );
};
