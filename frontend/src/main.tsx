import React from "react";
import { createRoot } from "react-dom/client";

import { App } from "@app/App";
import "@shared/styles/theme.css";
import "@shared/styles/admin.css";
import "@shared/styles/quest.css";

const rootElement = document.getElementById("root");

if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
