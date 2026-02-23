import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/common/utils';
import {
    LayoutDashboard,
    Activity,
    Globe2,
    Package,
    Users,
    MessageCircle,
    Wrench,
    HelpCircle,
    Settings,
    ChevronLeft,
    ChevronRight,
    Rss,
} from 'lucide-react';

interface SidebarProps {
    collapsed: boolean;
    onToggle: () => void;
}

const navItems = [
    { href: '/', label: 'Dashboard', icon: LayoutDashboard, section: 'main' },
    { href: '/status', label: 'Status', icon: Activity, section: 'main' },
    { href: '/sessions', label: 'Sessions', icon: Globe2, section: 'world' },
    { href: '/inventory', label: 'Inventory', icon: Package, section: 'world' },
    { href: '/contacts', label: 'Contacts', icon: Users, section: 'social' },
    { href: '/chat', label: 'Chat', icon: MessageCircle, section: 'social' },
    { href: '/tools', label: 'Tools', icon: Wrench, section: 'dev' },
    { href: '/help', label: 'Help', icon: HelpCircle, section: 'dev' },
    { href: '/settings', label: 'Settings', icon: Settings, section: 'dev' },
];

const sections: Record<string, string> = {
    main: 'Overview',
    world: 'World',
    social: 'Social',
    dev: 'Tools',
};

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
    const location = useLocation();

    // Group by section
    const grouped: Record<string, typeof navItems> = {};
    for (const item of navItems) {
        if (!grouped[item.section]) grouped[item.section] = [];
        grouped[item.section].push(item);
    }

    return (
        <aside
            className={cn(
                'relative flex flex-col border-r border-slate-800 bg-slate-950/60 backdrop-blur-xl transition-all duration-300 ease-in-out flex-shrink-0',
                collapsed ? 'w-16' : 'w-60'
            )}
            aria-label="Main navigation"
        >
            {/* Brand */}
            <div className="flex h-16 items-center border-b border-slate-800 px-4 gap-2.5">
                <Rss className="h-6 w-6 text-indigo-400 flex-shrink-0" aria-hidden="true" />
                {!collapsed && (
                    <span className="animate-in fade-in duration-300 font-semibold text-slate-100 text-sm leading-tight">
                        Resonite<br /><span className="text-xs text-indigo-400 font-normal">MCP</span>
                    </span>
                )}
            </div>

            {/* Nav */}
            <nav className="flex-1 overflow-y-auto py-3 space-y-4 px-2" aria-label="Site navigation">
                {Object.entries(grouped).map(([sec, items]) => (
                    <div key={sec} className="space-y-0.5">
                        {!collapsed && (
                            <p className="px-3 pb-1 text-[10px] font-semibold text-slate-600 uppercase tracking-widest">
                                {sections[sec]}
                            </p>
                        )}
                        {items.map(item => {
                            const active = location.pathname === item.href;
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.href}
                                    to={item.href}
                                    title={collapsed ? item.label : undefined}
                                    aria-current={active ? 'page' : undefined}
                                    className={cn(
                                        'group relative flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all',
                                        active
                                            ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                                            : 'text-slate-400 hover:bg-white/[0.05] hover:text-slate-200',
                                        collapsed ? 'justify-center' : 'gap-3'
                                    )}
                                >
                                    <Icon className={cn('h-4.5 w-4.5 flex-shrink-0', active && 'text-indigo-400')} aria-hidden="true" />
                                    {!collapsed && <span>{item.label}</span>}
                                    {/* Collapsed tooltip */}
                                    {collapsed && (
                                        <span className="absolute left-full ml-2 hidden rounded-md bg-slate-800 border border-slate-700 px-2 py-1 text-xs text-white group-hover:block z-50 whitespace-nowrap shadow-lg">
                                            {item.label}
                                        </span>
                                    )}
                                </Link>
                            );
                        })}
                    </div>
                ))}
            </nav>

            {/* Collapse toggle */}
            <div className="border-t border-slate-800 p-2">
                <button
                    onClick={onToggle}
                    aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                    className="flex w-full items-center justify-center rounded-lg p-2 text-slate-500 hover:bg-slate-800 hover:text-white transition-colors"
                >
                    {collapsed
                        ? <ChevronRight className="h-4 w-4" aria-hidden="true" />
                        : <div className="flex items-center gap-2"><ChevronLeft className="h-4 w-4" aria-hidden="true" /><span className="text-sm">Collapse</span></div>
                    }
                </button>
            </div>
        </aside>
    );
}
