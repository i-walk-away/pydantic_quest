import { Component, type ErrorInfo, type ReactElement, type ReactNode } from "react";

import { Button } from "@shared/ui/Button";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  public static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  public override componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("ui error", error, info);
  }

  private handleReload = (): void => {
    window.location.reload();
  };

  public override render(): ReactElement {
    if (!this.state.hasError) {
      return this.props.children as ReactElement;
    }

    return (
      <div className="error-boundary">
        <div>
          <h1>Something went wrong</h1>
          <p className="muted">Try reloading the page or come back later.</p>
          <Button variant="ghost" type="button" onClick={this.handleReload}>
            reload
          </Button>
        </div>
      </div>
    );
  }
}
