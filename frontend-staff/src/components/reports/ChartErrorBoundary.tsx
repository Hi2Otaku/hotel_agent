import { Component, type ErrorInfo, type ReactNode } from 'react';
import { RefreshCw } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ChartErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Chart render error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <Card className="bg-[#1E293B] border-[#334155] p-4">
          <div className="flex h-[260px] flex-col items-center justify-center">
            <p className="text-sm text-[#F87171]">
              Something went wrong rendering the charts.
            </p>
            <p className="mt-1 text-xs text-[#94A3B8]">
              {this.state.error?.message || 'An unexpected error occurred.'}
            </p>
            <Button
              variant="ghost"
              size="sm"
              onClick={this.handleReset}
              className="mt-3 text-[#94A3B8] hover:text-[#F1F5F9]"
            >
              <RefreshCw className="mr-1 h-4 w-4" />
              Try Again
            </Button>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}
