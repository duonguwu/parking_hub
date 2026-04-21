import { cn } from '@/services/utils'

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-[0.6875rem] uppercase font-medium tracking-[0.05em] transition-colors border border-outline-variant',
        {
          'bg-surface-container-low text-on-surface': variant === 'default',
          'bg-success-soft text-success border-success/20': variant === 'success',
          'bg-warning-soft text-warning border-warning/20': variant === 'warning',
          'bg-error-container text-on-error-container border-error/20': variant === 'error',
          'bg-info-soft text-info border-info/20': variant === 'info',
        },
        className
      )}
      {...props}
    />
  )
}
