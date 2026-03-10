import { useEffect, useMemo, useRef, type ReactElement } from "react";

import {
  defaultKeymap,
  history,
  historyKeymap,
  indentWithTab,
} from "@codemirror/commands";
import {
  acceptCompletion,
  autocompletion,
  closeBrackets,
  closeBracketsKeymap,
  completionKeymap,
} from "@codemirror/autocomplete";
import { python } from "@codemirror/lang-python";
import {
  bracketMatching,
  defaultHighlightStyle,
  HighlightStyle,
  indentUnit,
  indentOnInput,
  syntaxHighlighting,
} from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import {
  type Diagnostic,
  lintGutter,
  lintKeymap,
  linter,
  setDiagnostics,
} from "@codemirror/lint";
import {
  drawSelection,
  Decoration,
  dropCursor,
  EditorView,
  highlightActiveLine,
  highlightActiveLineGutter,
  keymap,
  lineNumbers,
  MatchDecorator,
  ViewPlugin,
} from "@codemirror/view";
import { tags } from "@lezer/highlight";

import { type CodeAnalysisDiagnostic } from "@shared/model/execution";

const completionTypePriority: Record<string, number> = {
  keyword: 0,
  class: 1,
  type: 1,
  function: 2,
  method: 2,
  variable: 3,
  property: 4,
  text: 5,
};

const builtinTypeDecorator = new MatchDecorator({
  regexp:
    /\b(?:int|str|bool|float|bytes|bytearray|list|dict|tuple|set|frozenset|complex|object|type)\b/g,
  decoration: Decoration.mark({ class: "cm-py-builtin-type" }),
});

const typingSymbolDecorator = new MatchDecorator({
  regexp:
    /\b(?:Any|Annotated|Callable|ClassVar|Final|Generic|Iterable|Iterator|Literal|Mapping|MutableMapping|Optional|Protocol|Self|Sequence|TypeAlias|TypeVar|Union)\b/g,
  decoration: Decoration.mark({ class: "cm-py-typing-symbol" }),
});

const pydanticSymbolDecorator = new MatchDecorator({
  regexp:
    /\b(?:BaseModel|ConfigDict|Field|ValidationError|TypeAdapter|AfterValidator|BeforeValidator|PlainValidator|WrapValidator|field_validator|model_validator|computed_field)\b/g,
  decoration: Decoration.mark({ class: "cm-py-pydantic-symbol" }),
});

const createSemanticHighlightPlugin = (decorator: MatchDecorator) =>
  ViewPlugin.fromClass(
    class {
      decorations;

      constructor(view: EditorView) {
        this.decorations = decorator.createDeco(view);
      }

      update(update: { view: EditorView; docChanged: boolean; viewportChanged: boolean }): void {
        if (update.docChanged || update.viewportChanged) {
          this.decorations = decorator.createDeco(update.view);
        }
      }
    },
    {
      decorations: (plugin) => plugin.decorations,
    }
  );

const builtinTypeHighlightPlugin = createSemanticHighlightPlugin(builtinTypeDecorator);
const typingSymbolHighlightPlugin = createSemanticHighlightPlugin(typingSymbolDecorator);
const pydanticSymbolHighlightPlugin = createSemanticHighlightPlugin(pydanticSymbolDecorator);

export interface CodeEditorProps {
  value: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
  ariaLabel?: string;
  className?: string;
  diagnostics?: CodeAnalysisDiagnostic[];
}

const buildOffset = (value: string, line: number, column: number): number => {
  const lines = value.split("\n");
  const normalizedLine = Math.max(line - 1, 0);
  const targetLine = lines[normalizedLine] ?? "";
  const safeColumn = Math.max(column - 1, 0);
  let offset = 0;

  for (let index = 0; index < normalizedLine; index += 1) {
    offset += (lines[index] ?? "").length + 1;
  }

  return offset + Math.min(safeColumn, targetLine.length);
};

const mapDiagnostics = (value: string, diagnostics: CodeAnalysisDiagnostic[]): Diagnostic[] => {
  const documentLength = value.length;

  return diagnostics.map((item) => {
    const from = buildOffset(value, item.line, item.column);
    const to = Math.max(from, buildOffset(value, item.stop_line, item.stop_column));
    const source = item.name ? `pyrefly:${item.name}` : "pyrefly";
    const safeTo = to === from ? Math.min(from + 1, documentLength) : to;

    return {
      from: from,
      to: safeTo,
      severity: item.severity === "information" ? "info" : item.severity,
      source: source,
      message: item.message,
    };
  });
};

export const CodeEditor = ({
  value,
  onChange,
  readOnly = false,
  ariaLabel = "code editor",
  className,
  diagnostics = [],
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
        { tag: [tags.typeName, tags.className], color: "#ff4d8d", fontWeight: "600" },
        { tag: [tags.function(tags.variableName), tags.function(tags.propertyName)], color: "#57b6c2" },
        { tag: [tags.variableName, tags.propertyName], color: "#ced0d6" },
        { tag: tags.definition(tags.variableName), color: "#f3c86b" },
        { tag: [tags.operator, tags.punctuation], color: "#a9b7c6" },
        { tag: tags.bool, color: "#c77dff", fontWeight: "600" },
        { tag: tags.null, color: "#c77dff", fontWeight: "600" },
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
          ".cm-diagnosticText": {
            borderBottomWidth: "2px",
          },
          ".cm-tooltip-lint": {
            border: "1px solid rgba(255, 255, 255, 0.08)",
            backgroundColor: "#15171c",
            color: "var(--text-strong)",
          },
          ".cm-py-builtin-type": {
            color: "#cf8e6d",
          },
          ".cm-py-typing-symbol": {
            color: "#f3c86b",
          },
          ".cm-py-pydantic-symbol": {
            color: "#ff4d8d",
            fontWeight: "600",
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
        drawSelection(),
        dropCursor(),
        highlightActiveLineGutter(),
        highlightActiveLine(),
        history(),
        indentOnInput(),
        bracketMatching(),
        closeBrackets(),
        autocompletion({
          compareCompletions: (left, right) => {
            const leftType = left.type?.split(" ")[0] ?? "text";
            const rightType = right.type?.split(" ")[0] ?? "text";
            const leftRank = completionTypePriority[leftType] ?? 99;
            const rightRank = completionTypePriority[rightType] ?? 99;

            if (leftRank !== rightRank) {
              return leftRank - rightRank;
            }

            const leftLabel = left.sortText ?? left.label;
            const rightLabel = right.sortText ?? right.label;

            return leftLabel.localeCompare(rightLabel);
          },
        }),
        lintGutter(),
        linter(() => [], { delay: 0 }),
        keymap.of([
          { key: "Tab", run: acceptCompletion },
          indentWithTab,
          ...closeBracketsKeymap,
          ...completionKeymap,
          ...lintKeymap,
          ...defaultKeymap,
          ...historyKeymap,
        ]),
        python(),
        builtinTypeHighlightPlugin,
        typingSymbolHighlightPlugin,
        pydanticSymbolHighlightPlugin,
        EditorState.tabSize.of(4),
        indentUnit.of("    "),
        syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
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

  useEffect(() => {
    const view = viewRef.current;
    if (!view) {
      return;
    }

    view.dispatch(setDiagnostics(view.state, mapDiagnostics(view.state.doc.toString(), diagnostics)));
  }, [diagnostics, value]);

  return <div aria-label={ariaLabel} className={className} ref={parentRef} />;
};
