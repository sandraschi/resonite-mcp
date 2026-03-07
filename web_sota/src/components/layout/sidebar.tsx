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
    Radio,
    Terminal,
    User,
    ShoppingBag,
    Cloud,
    Share2,
    Archive,
    Cpu,
    Link2,
    TreePine,
    Gamepad2,
    Navigation,
    Search,
    Grid,
} from 'lucide-react';

interface SidebarProps {
    collapsed: boolean;
    onToggle: () => void;
}

const navItems = [
    { href: '/', label: 'Dashboard', icon: LayoutDashboard, section: 'main' },
    { href: '/search', label: 'Semantic Search', icon: Search, section: 'main' },
    { href: '/status', label: 'Status', icon: Activity, section: 'main' },
    { href: '/sessions', label: 'Sessions', icon: Globe2, section: 'world' },
    { href: '/world', label: 'World', icon: TreePine, section: 'world' },
    { href: '/io', label: 'IO & Assets', icon: Package, section: 'world' },
    { href: '/inventory', label: 'Inventory', icon: Archive, section: 'world' },
    { href: '/map', label: 'Map', icon: Navigation, section: 'world' },
    { href: '/marketplace', label: 'Marketplace', icon: ShoppingBag, section: 'world' },
    { href: '/avatar', label: 'Avatar', icon: User, section: 'identity' },
    { href: '/control', label: 'Control', icon: Gamepad2, section: 'identity' },
    { href: '/osc', label: 'OSC Control', icon: Radio, section: 'systems' },
    { href: '/scripting', label: 'Scripting', icon: Terminal, section: 'systems' },
    { href: '/integrations', label: 'Integrations', icon: Share2, section: 'systems' },
    { href: '/rest-api', label: 'Cloud API', icon: Cloud, section: 'systems' },
    { href: '/protoflux', label: 'ProtoFlux', icon: Cpu, section: 'systems' },
    { href: '/resonite-link', label: 'ResoniteLink', icon: Link2, section: 'systems' },
    { href: '/contacts', label: 'Contacts', icon: Users, section: 'social' },
    { href: '/chat', label: 'Chat', icon: MessageCircle, section: 'social' },
    { href: '/apps', label: 'App Hub', icon: Grid, section: 'social' },
    { href: '/tools', label: 'Dev Tools', icon: Wrench, section: 'dev' },
    { href: '/help', label: 'Reference', icon: HelpCircle, section: 'dev' },
    { href: '/settings', label: 'Settings', icon: Settings, section: 'dev' },
];

const sections: Record<string, string> = {
    main: 'Overview',
    world: 'World',
    identity: 'Identity',
    systems: 'Systems',
    social: 'Social',
    dev: 'Meta',
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
                'relative flex flex-col border-r border-border bg-background/60 backdrop-blur-xl transition-all duration-300 ease-in-out flex-shrink-0',
                collapsed ? 'w-16' : 'w-60'
            )}
            aria-label="Main navigation"
        >
            {/* Brand */}
            <div className="flex h-16 items-center border-b border-border px-4 gap-2.5">
                <Rss className="h-6 w-6 text-indigo-400 flex-shrink-0" aria-hidden="true" />
                {!collapsed && (
                    <span className="animate-in fade-in duration-300 font-semibold text-foreground text-sm leading-tight">
                        Resonite<br /><span className="text-xs text-indigo-400 font-normal tracking-wider">MCP</span>
                    </span>
                )}
            </div>

            {/* Nav */}
            <nav className="flex-1 overflow-y-auto py-3 space-y-4 px-2 scrollbar-none" aria-label="Site navigation">
                {Object.entries(grouped).map(([sec, items]) => (
                    <div key={sec} className="space-y-0.5">
                        {!collapsed && (
                            <p className="px-3 pb-1 text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] opacity-50">
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
                                        'group relative flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300',
                                        active
                                            ? 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/30'
                                            : 'text-muted-foreground hover:bg-white/[0.03] hover:text-foreground',
                                        collapsed ? 'justify-center' : 'gap-3'
                                    )}
                                >
                                    <Icon className={cn('h-4.5 w-4.5 flex-shrink-0 transition-transform duration-300 group-hover:scale-110', active && 'text-indigo-400')} aria-hidden="true" />
                                    {!collapsed && <span>{item.label}</span>}
                                    {/* Collapsed tooltip */}
                                    {collapsed && (
                                        <span className="absolute left-full ml-2 hidden rounded-md bg-background border border-border px-2 py-1 text-xs text-foreground group-hover:block z-50 whitespace-nowrap shadow-2xl glass animate-in fade-in slide-in-from-left-1">
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
            <div className="border-t border-border p-2">
                <button
                    onClick={onToggle}
                    aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                    className="flex w-full items-center justify-center rounded-lg p-2 text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-all duration-300 border border-transparent hover:border-border"
                >
                    {collapsed
                        ? <ChevronRight className="h-4 w-4" aria-hidden="true" />
                        : <div className="flex items-center gap-2"><ChevronLeft className="h-4 w-4" aria-hidden="true" /><span className="text-xs font-semibold uppercase tracking-wider">Minimize</span></div>
                    }
                </button>
            </div>
        </aside>
    );
}
