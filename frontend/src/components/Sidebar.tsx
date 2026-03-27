import { NavLink } from 'react-router-dom';
import { FileText, Code, FolderTree, Settings, Database } from 'lucide-react';

const navItems = [
  { path: '/', icon: Database, label: '概览' },
  { path: '/import', icon: FileText, label: '导入数据' },
  { path: '/codes', icon: Code, label: '代码本' },
  { path: '/categories', icon: FolderTree, label: '类属' },
  { path: '/settings', icon: Settings, label: '设置' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-endfield-bg-secondary border-r border-endfield-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-endfield-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg overflow-hidden bg-gradient-to-br from-orange-400 to-red-500">
            <img 
              src="/icon-64.png" 
              alt="CoderResearch" 
              className="w-full h-full object-cover"
            />
          </div>
          <div>
            <h1 className="text-lg font-bold text-endfield-text-primary">CoderResearch</h1>
            <p className="text-xs text-endfield-text-muted">v3.0.0</p>
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-150
              ${isActive 
                ? 'bg-endfield-accent/10 text-endfield-accent border border-endfield-accent/30' 
                : 'text-endfield-text-secondary hover:bg-endfield-bg-hover hover:text-endfield-text-primary'
              }
            `}
          >
            <item.icon size={18} />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>
      
      {/* Footer */}
      <div className="p-4 border-t border-endfield-border">
        <div className="ef-card p-3">
          <div className="flex items-center gap-2 text-xs text-endfield-text-muted">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>系统运行正常</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
