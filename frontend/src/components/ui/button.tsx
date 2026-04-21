import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/services/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-full text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 disabled:pointer-events-none disabled:opacity-50 border border-outline-variant hover:border-primary',
  {
    variants: {
      variant: {
        default:
          'bg-primary-container text-on-surface hover:bg-primary-container/90',
        secondary:
          'bg-surface-container-lowest text-primary hover:bg-surface-container-low',
        outline:
          'bg-transparent hover:bg-surface-container-low text-on-surface',
        ghost: 'border-transparent hover:border-transparent hover:bg-surface-container-low text-on-surface',
        destructive: 'bg-error text-on-error hover:bg-error/90 border-transparent hover:border-transparent',
        link: 'text-primary underline-offset-4 hover:underline border-transparent hover:border-transparent',
      },
      size: {
        default: 'h-10 px-5 py-2',
        sm: 'h-8 px-3 text-xs',
        lg: 'h-12 px-8 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
