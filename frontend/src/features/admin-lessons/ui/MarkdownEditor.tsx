import { useMemo, useRef, type ReactElement } from "react";

import { renderMarkdown } from "@shared/lib/markdown/renderMarkdown";
import { eventToCombo, type MarkdownHotkeys } from "@shared/lib/hotkeys";
import { Textarea } from "@shared/ui/Textarea";
import { Button } from "@shared/ui/Button";

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  toolbarHidden: boolean;
  onToggleToolbar: () => void;
  hotkeys: MarkdownHotkeys;
}

export const MarkdownEditor = ({
  value,
  onChange,
  toolbarHidden,
  onToggleToolbar,
  hotkeys,
}: MarkdownEditorProps): ReactElement => {
  const previewHtml = useMemo(() => renderMarkdown(value), [value]);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const wrapSelection = (left: string, right: string, placeholder: string) => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = value.slice(start, end);
    const replacement = selected || placeholder;
    const nextValue = `${value.slice(0, start)}${left}${replacement}${right}${value.slice(end)}`;
    onChange(nextValue);
    const cursorStart = start + left.length;
    const cursorEnd = cursorStart + replacement.length;
    requestAnimationFrame(() => {
      textarea.focus();
      textarea.setSelectionRange(cursorStart, cursorEnd);
    });
  };

  const insertBlock = (block: string) => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }
    const start = textarea.selectionStart;
    const nextValue = `${value.slice(0, start)}${block}${value.slice(start)}`;
    onChange(nextValue);
    requestAnimationFrame(() => {
      textarea.focus();
      textarea.setSelectionRange(start + block.length, start + block.length);
    });
  };

  const handleTool = (tool: string) => {
    if (tool === "bold") {
      wrapSelection("**", "**", "bold");
      return;
    }
    if (tool === "italic") {
      wrapSelection("*", "*", "italic");
      return;
    }
    if (tool === "code") {
      wrapSelection("`", "`", "code");
      return;
    }
    if (tool === "link") {
      wrapSelection("[", "](https://)", "label");
      return;
    }
    if (tool === "h2") {
      insertBlock("\n## Heading\n");
      return;
    }
    if (tool === "quote") {
      insertBlock("\n> quote\n");
      return;
    }
    if (tool === "ul") {
      insertBlock("\n- item\n- item\n");
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const combo = eventToCombo(event.nativeEvent);
    if (combo === hotkeys.bold) {
      event.preventDefault();
      handleTool("bold");
    }
    if (combo === hotkeys.italic) {
      event.preventDefault();
      handleTool("italic");
    }
    if (combo === hotkeys.codeBlock) {
      event.preventDefault();
      wrapSelection("```\n", "\n```", "code");
    }
  };

  return (
    <div className={toolbarHidden ? "markdown-editor markdown-editor--compact" : "markdown-editor"}>
      <div className="toolbar-row">
        <div className="toolbar" role="toolbar">
          <Button variant="ghost" type="button" onClick={() => handleTool("h2")}>H2</Button>
          <Button variant="ghost" type="button" onClick={() => handleTool("bold")}>bold</Button>
          <Button variant="ghost" type="button" onClick={() => handleTool("italic")}>italic</Button>
          <Button variant="ghost" type="button" onClick={() => handleTool("code")}>code</Button>
          <Button variant="ghost" type="button" onClick={() => handleTool("quote")}>quote</Button>
          <Button variant="ghost" type="button" onClick={() => handleTool("ul")}>list</Button>
          <Button variant="ghost" type="button" onClick={() => handleTool("link")}>link</Button>
        </div>
        <Button variant="ghost" type="button" onClick={onToggleToolbar}>
          {toolbarHidden ? "show tools" : "hide tools"}
        </Button>
      </div>

      <div className="editor-grid">
        <label className="field">
          <span className="field__label">Body markdown</span>
          <Textarea
            className="textarea--editor"
            name="body_markdown"
            rows={14}
            value={value}
            ref={textareaRef}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
          />
        </label>
        <div className="preview-block">
          <span className="field__label">Preview</span>
          <div className="preview">
            <div className="markdown" dangerouslySetInnerHTML={{ __html: previewHtml }} />
          </div>
        </div>
      </div>
    </div>
  );
};
