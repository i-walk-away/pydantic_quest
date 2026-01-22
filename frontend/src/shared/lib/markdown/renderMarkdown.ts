import { marked, type Tokens } from "marked";

import { highlightPython } from "@shared/lib/markdown/highlightPython";

const renderer = new marked.Renderer();

renderer.code = ({ text, lang }: Tokens.Code) => {
  if (lang === "expected") {
    return `<div class="callout"><p>Expected output:</p><pre><code>${escapeHtml(text)}</code></pre></div>`;
  }
  const highlighted = highlightPython(text);
  return `<pre><code class="hljs language-python">${highlighted}</code></pre>`;
};

export const renderMarkdown = (value: string): string => {
  const rendered = marked.parse(value, { renderer: renderer, async: false });

  return typeof rendered === "string" ? rendered : "";
};

const escapeHtml = (value: string): string => {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
};
