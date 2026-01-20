import { marked, type Tokens } from "marked";

import { highlightPython } from "@shared/lib/markdown/highlightPython";

const renderer = new marked.Renderer();

renderer.code = ({ text }: Tokens.Code) => {
  const highlighted = highlightPython(text);
  return `<pre><code class="hljs language-python">${highlighted}</code></pre>`;
};

export const renderMarkdown = (value: string): string => {
  const rendered = marked.parse(value, { renderer: renderer, async: false });

  return typeof rendered === "string" ? rendered : "";
};
