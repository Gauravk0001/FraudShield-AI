import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme, type Theme } from '../../context/ThemeContext';

export const ThemeToggle: React.FC<{ variant?: 'icon' | 'segmented' }> = ({ variant = 'icon' }) => {
  const { theme, setTheme, isDark } = useTheme();

  if (variant === 'segmented') {
    const options: { value: Theme; label: string; icon: React.ElementType }[] = [
      { value: 'light', label: 'Light', icon: Sun },
      { value: 'dark', label: 'Dark', icon: Moon },
      { value: 'system', label: 'System', icon: Monitor },
    ];

    return (
      <div className="inline-flex p-1 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
        {options.map((opt) => {
          const Icon = opt.icon;
          const isSelected = theme === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => setTheme(opt.value)}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                isSelected
                  ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{opt.label}</span>
            </button>
          );
        })}
      </div>
    );
  }

  // Header quick toggle cycle: light -> dark -> system
  const toggleNext = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  const Icon = theme === 'system' ? Monitor : isDark ? Moon : Sun;
  const label = theme === 'system' ? 'System Theme' : isDark ? 'Dark Mode' : 'Light Mode';

  return (
    <button
      type="button"
      onClick={toggleNext}
      title={`Theme: ${label} (Click to switch)`}
      aria-label={`Current theme is ${label}. Click to switch theme.`}
      className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <Icon className="w-5 h-5 transition-transform duration-200 hover:rotate-12" />
    </button>
  );
};
