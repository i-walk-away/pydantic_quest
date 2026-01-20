import { type ReactElement, type ReactNode } from "react";

interface NoticeProps {
  message: ReactNode;
  variant?: "success" | "error" | "info";
}

export const Notice = ({ message, variant = "success" }: NoticeProps): ReactElement => {
  const className = ["notice", `notice--${variant}`].join(" ").trim();

  return (
    <div className={className} role="status" aria-live="polite">
      {message}
    </div>
  );
};
