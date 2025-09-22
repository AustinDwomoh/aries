import React from 'react';
import { clsx } from 'clsx';
import { CardProps } from '@/types';

export const Card: React.FC<CardProps> = ({ 
  className, 
  children, 
  onClick, 
  hover = false 
}) => {
  return (
    <div
      className={clsx(
        'bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm',
        hover && 'hover:shadow-md transition-shadow duration-200 cursor-pointer',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{ className?: string; children: React.ReactNode }> = ({ 
  className, 
  children 
}) => {
  return (
    <div className={clsx('px-6 py-4 border-b border-gray-200 dark:border-gray-700', className)}>
      {children}
    </div>
  );
};

export const CardTitle: React.FC<{ className?: string; children: React.ReactNode }> = ({ 
  className, 
  children 
}) => {
  return (
    <h3 className={clsx('text-lg font-semibold text-gray-900 dark:text-white', className)}>
      {children}
    </h3>
  );
};

export const CardContent: React.FC<{ className?: string; children: React.ReactNode }> = ({ 
  className, 
  children 
}) => {
  return (
    <div className={clsx('px-6 py-4', className)}>
      {children}
    </div>
  );
};

export const CardFooter: React.FC<{ className?: string; children: React.ReactNode }> = ({ 
  className, 
  children 
}) => {
  return (
    <div className={clsx('px-6 py-4 border-t border-gray-200 dark:border-gray-700', className)}>
      {children}
    </div>
  );
};
