import { marked } from "marked";

import { highlightPython } from "@shared/lib/markdown/highlightPython";

const renderer = new marked.Renderer();

renderer.code = (code) => {
  const highlighted = highlightPython(code);
  return `<pre><code class="hljs language-python">${highlighted}</code></pre>`;
};

export const renderMarkdown = (value: string): string => {
  return marked.parse(value, { renderer: renderer });
};
