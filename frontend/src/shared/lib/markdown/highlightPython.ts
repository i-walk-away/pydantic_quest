const escapeHtml = (value: string): string => {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
};

export const highlightPython = (code: string): string => {
  const keywords = new Set([
    "False", "None", "True", "and", "as", "assert", "async", "await", "break",
    "class", "continue", "def", "del", "elif", "else", "except", "finally",
    "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
    "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
  ]);

  const highlightCodeSegment = (value: string): string => {
    let result = "";
    let lastIndex = 0;
    let expectTitle = false;
    const tokenRegex = /([A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?)/g;
    let match = tokenRegex.exec(value);

    while (match) {
      const token = match[0];
      const start = match.index;
      const end = start + token.length;
      result += escapeHtml(value.slice(lastIndex, start));
      if (/^\d/.test(token)) {
        result += `<span class="hljs-number">${token}</span>`;
      } else if (expectTitle) {
        result += `<span class="hljs-title">${token}</span>`;
        expectTitle = false;
      } else if (keywords.has(token)) {
        result += `<span class="hljs-keyword">${token}</span>`;
        if (token === "class" || token === "def") {
          expectTitle = true;
        }
      } else {
        result += token;
      }
      lastIndex = end;
      match = tokenRegex.exec(value);
    }
    result += escapeHtml(value.slice(lastIndex));
    return result;
  };

  const tokens: Array<{ type: "code" | "comment" | "string"; text: string }> = [];
  let index = 0;

  while (index < code.length) {
    const char = code[index];

    if (char === "#") {
      let end = code.indexOf("\n", index);
      if (end === -1) {
        end = code.length;
      }
      tokens.push({ type: "comment", text: code.slice(index, end) });
      index = end;
      continue;
    }

    if (char === "\"" || char === "'") {
      const quote = char;
      const triple = code.slice(index, index + 3) === quote.repeat(3);
      let end = index + (triple ? 3 : 1);
      while (end < code.length) {
        if (code[end] === "\\" && !triple) {
          end += 2;
          continue;
        }
        if (triple && code.slice(end, end + 3) === quote.repeat(3)) {
          end += 3;
          break;
        }
        if (!triple && code[end] === quote) {
          end += 1;
          break;
        }
        end += 1;
      }
      tokens.push({ type: "string", text: code.slice(index, end) });
      index = end;
      continue;
    }

    tokens.push({ type: "code", text: char });
    index += 1;
  }

  const merged: Array<{ type: "code" | "comment" | "string"; text: string }> = [];
  for (const token of tokens) {
    const last = merged[merged.length - 1];
    if (token.type === "code" && last && last.type === "code") {
      last.text += token.text;
    } else {
      merged.push({ ...token });
    }
  }

  return merged
    .map((token) => {
      if (token.type === "comment") {
        return `<span class="hljs-comment">${escapeHtml(token.text)}</span>`;
      }
      if (token.type === "string") {
        return `<span class="hljs-string">${escapeHtml(token.text)}</span>`;
      }
      return highlightCodeSegment(token.text);
    })
    .join("");
};
