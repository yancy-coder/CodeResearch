import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  accent?: boolean;
}

export default function Card({ children, title, className = '', accent = false }: CardProps) {
  return (
    <div className={`
      ef-card p-6 ${className}
      ${accent ? 'border-endfield-accent/50 shadow-lg shadow-endfield-accent/5' : ''}
    `}>
      {title && (
        <>
          <h3 className="text-lg font-semibold text-endfield-text-primary mb-4">{title}</h3>
          <div className="ef-divider mb-4" />
        </>
      )}
      {children}
    </div>
  );
}
