import { ButtonHTMLAttributes, ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonStyles = cva(
  "rounded-full font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2",
  {
    variants: {
      variant: {
        primary: "bg-[#f2ae2a] text-gray-600 hover:bg-[#f2ae2a]/90 focus:ring-[#f2ae2a]",
        secondary: "bg-black text-white hover:bg-black/90 focus:ring-black",
      },
      size: {
        sm: "px-4 py-2 text-sm",
        md: "px-6 py-3 text-base",
        lg: "px-8 py-4 text-lg",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

interface ButtonProps 
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonStyles> {
  children: ReactNode;
}

export const Button = ({
  children,
  variant,
  size,
  className,
  ...props
}: ButtonProps) => {
  return (
    <button
      className={buttonStyles({ variant, size, className })}
      {...props}
    >
      {children}
    </button>
  );
};
