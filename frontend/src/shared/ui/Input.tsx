import { type InputHTMLAttributes, type ReactElement } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export const Input = ({ className, ...props }: InputProps): ReactElement => {
  const combinedClassName = ["input", className || ""].join(" ").trim();
  return <input {...props} className={combinedClassName} />;
};
