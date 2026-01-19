import { forwardRef, type TextareaHTMLAttributes } from "react";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(({ className, ...props }, ref) => {
  const combinedClassName = ["textarea", className || ""].join(" ").trim();
  return <textarea {...props} ref={ref} className={combinedClassName} />;
});

Textarea.displayName = "Textarea";
