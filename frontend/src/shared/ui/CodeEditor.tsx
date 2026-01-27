import { useEffect, useMemo, useRef, type ReactElement } from "react";

import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import { EditorView, highlightActiveLineGutter, keymap, lineNumbers } from "@codemirror/view";
import { tags } from "@lezer/highlight";

export interface CodeEditorProps {
  value: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
  ariaLabel?: string;
  className?: string;
}

export const CodeEditor = ({
  value,
  onChange,
  readOnly = false,
  ariaLabel = "code editor",
  className,
}: CodeEditorProps): ReactElement => {
  const parentRef = useRef<HTMLDivElement | null>(null);
  const viewRef = useRef<EditorView | null>(null);
  const onChangeRef = useRef<CodeEditorProps["onChange"]>(onChange);

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  const highlightStyle = useMemo(
    () =>
      HighlightStyle.define([
        { tag: tags.keyword, color: "#cf8e6d", fontWeight: "600" },
        { tag: tags.string, color: "#6aab73" },
        { tag: tags.comment, color: "#7a7e85", fontStyle: "italic" },
        { tag: tags.number, color: "#2aacb8" },
        { tag: tags.typeName, color: "#ff4d8d" },
      ]),
    []
  );

  const theme = useMemo(
    () =>
      EditorView.theme(
        {
          "&": {
            height: "100%",
            color: "var(--text-strong)",
            backgroundColor: "transparent",
          },
          ".cm-content": {
            fontFamily: '"IBM Plex Mono", monospace',
            fontSize: "0.92rem",
            lineHeight: "1.6",
            textTransform: "none",
          },
          ".cm-line": {
            textTransform: "none",
          },
          ".cm-scroller": {
            overflow: "auto",
          },
          ".cm-gutters": {
            backgroundColor: "rgba(0, 0, 0, 0.35)",
            color: "var(--text-muted)",
            borderRight: "none",
          },
          ".cm-activeLine": {
            backgroundColor: "#26282E",
          },
          ".cm-activeLineGutter": {
            backgroundColor: "#26282E",
          },
          ".cm-cursor": {
            borderLeftColor: "#CED0D6",
          },
          ".cm-selectionBackground": {
            backgroundColor: "#3E3E3E",
          },
        },
        { dark: true }
      ),
    []
  );

  useEffect(() => {
    const parent = parentRef.current;
    if (!parent || viewRef.current) {
      return;
    }

    const updateListener = EditorView.updateListener.of((update) => {
      if (!update.docChanged) {
        return;
      }

      onChangeRef.current?.(update.state.doc.toString());
    });

    const state = EditorState.create({
      doc: value,
      extensions: [
        lineNumbers(),
        highlightActiveLineGutter(),
        history(),
        keymap.of([...defaultKeymap, ...historyKeymap]),
        python(),
        syntaxHighlighting(highlightStyle),
        theme,
        updateListener,
        EditorState.readOnly.of(readOnly),
        EditorView.editable.of(!readOnly),
      ],
    });

    viewRef.current = new EditorView({
      state,
      parent,
    });

    return () => {
      viewRef.current?.destroy();
      viewRef.current = null;
    };
  }, [highlightStyle, readOnly, theme]);

  useEffect(() => {
    const view = viewRef.current;
    if (!view) {
      return;
    }

    const currentValue = view.state.doc.toString();
    if (currentValue === value) {
      return;
    }

    view.dispatch({
      changes: { from: 0, to: view.state.doc.length, insert: value },
    });
  }, [value]);

  return <div aria-label={ariaLabel} className={className} ref={parentRef} />;
};
