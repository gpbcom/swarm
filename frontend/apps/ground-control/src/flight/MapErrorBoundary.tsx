import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

export interface MapErrorBoundaryProps {
  children: ReactNode;
}

interface MapErrorBoundaryState {
  failed: boolean;
}

/**
 * Keeps a failure of the map inside the map: without it, an error thrown while the map is built unmounts the whole
 * app, the safety controls of the title bar included. The failed map shows nothing, and the error goes to the console.
 */
export class MapErrorBoundary extends Component<MapErrorBoundaryProps, MapErrorBoundaryState> {
  override state: MapErrorBoundaryState = { failed: false };

  static getDerivedStateFromError(): MapErrorBoundaryState {
    return { failed: true };
  }

  override componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('The map of the Squad failed.', error, info.componentStack);
  }

  override render(): ReactNode {
    if (this.state.failed) {
      return null;
    }
    return this.props.children;
  }
}
