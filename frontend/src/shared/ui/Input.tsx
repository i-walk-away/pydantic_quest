import { type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export const Input = ({ className, ...props }: InputProps): JSX.Element => {
  const combinedClassName = ["input", className || ""].join(" ").trim();
  return <input {...props} className={combinedClassName} />;
};
