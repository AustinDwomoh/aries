import React from 'react';
import { clsx } from 'clsx';
import { ButtonProps } from '@/types';
import { Loader2 } from 'lucide-react';

const buttonVariants = {
  primary: 'bg-primary-600 hover:bg-primary-700 text-white border-transparent',
  secondary: 'bg-secondary-100 hover:bg-secondary-200 text-secondary-900 border-transparent',
  outline: 'bg-transparent hover:bg-gray-50 text-gray-700 border-gray-300 hover:border-gray-400',
  ghost: 'bg-transparent hover:bg-gray-100 text-gray-700 border-transparent',
  danger: 'bg-error-600 hover:bg-error-700 text-white border-transparent',
};

const buttonSizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className,
  children,
  onClick,
  type = 'button',
}) => {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={clsx(
        'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed',
        buttonVariants[variant],
        buttonSizes[size],
        className
      )}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
};
