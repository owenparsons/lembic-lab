import { Loader } from "lucide-react";

interface SpinnerProps {
  size?: number;
  className?: string;
}

export function Spinner({ size = 16, className = "" }: SpinnerProps) {
  return <Loader size={size} className={`animate-spin text-df-accent-primary ${className}`} />;
}
