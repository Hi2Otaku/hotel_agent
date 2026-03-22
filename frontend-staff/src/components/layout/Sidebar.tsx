import { NavLink, useLocation } from 'react-router';
import {
  LayoutDashboard,
  CalendarCheck,
  LogIn,
  BedDouble,
  Users,
  BarChart3,
  MessageSquare,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSidebarStore } from '@/stores/sidebarStore';
import { useAuthStore } from '@/stores/authStore';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import type { LucideIcon } from 'lucide-react';

interface NavItem {
  label: string;
  icon: LucideIcon;
  path: string;
  disabled?: boolean;
}

const navItems: NavItem[] = [
  { label: 'Overview', icon: LayoutDashboard, path: '/' },
  { label: 'Reservations', icon: CalendarCheck, path: '/reservations' },
  { label: 'Check-in/out', icon: LogIn, path: '/check-in-out' },
  { label: 'Room Status', icon: BedDouble, path: '/room-status' },
  { label: 'Guests', icon: Users, path: '/guests' },
  { label: 'Reports', icon: BarChart3, path: '/reports' },
  { label: 'Chat', icon: MessageSquare, path: '/chat' },
];

function NavItemContent({
  item,
  isActive,
  collapsed,
}: {
  item: NavItem;
  isActive: boolean;
  collapsed: boolean;
}) {
  const Icon = item.icon;
  const content = (
    <div
      className={cn(
        'flex h-10 items-center gap-2 rounded-md pl-2 pr-3 text-sm transition-colors',
        isActive && 'border-l-[3px] border-[#0F766E] bg-[rgba(15,118,110,0.15)]',
        !isActive && 'hover:bg-[#283548]',
        item.disabled && 'cursor-not-allowed opacity-50',
        collapsed && 'justify-center px-0',
      )}
      aria-current={isActive ? 'page' : undefined}
    >
      <Icon className="h-5 w-5 shrink-0" aria-label={item.label} />
      {!collapsed && <span className="text-xs">{item.label}</span>}
    </div>
  );

  if (collapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>{content}</TooltipTrigger>
        <TooltipContent side="right">
          {item.disabled ? `${item.label} - Coming in Phase 7` : item.label}
        </TooltipContent>
      </Tooltip>
    );
  }

  return content;
}

function SidebarContent({ collapsed }: { collapsed: boolean }) {
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const initials = user
    ? `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase()
    : 'ST';

  return (
    <div className="flex h-full flex-col bg-[#1E293B] border-r border-[#334155]">
      {/* Logo */}
      <div className={cn('flex items-center gap-2 px-4 py-4', collapsed && 'justify-center px-2')}>
        <span className="text-base font-semibold text-[#0F766E]">
          {collapsed ? 'HB' : 'HotelBook'}
        </span>
        {!collapsed && (
          <span className="text-xs text-[#94A3B8]">Staff</span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-2 py-2" aria-label="Main navigation">
        {navItems.map((item) => {
          const isActive =
            item.path === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(item.path);

          if (item.disabled) {
            if (collapsed) {
              return (
                <div key={item.path}>
                  <NavItemContent item={item} isActive={false} collapsed={collapsed} />
                </div>
              );
            }
            return (
              <Tooltip key={item.path}>
                <TooltipTrigger asChild>
                  <div>
                    <NavItemContent item={item} isActive={false} collapsed={collapsed} />
                  </div>
                </TooltipTrigger>
                <TooltipContent side="right">Coming in Phase 7</TooltipContent>
              </Tooltip>
            );
          }

          return (
            <NavLink key={item.path} to={item.path} end={item.path === '/'}>
              <NavItemContent item={item} isActive={isActive} collapsed={collapsed} />
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom section: user info + collapse toggle */}
      <div className="border-t border-[#334155] px-2 py-3">
        {/* Staff info */}
        <div className={cn('flex items-center gap-2 px-2 pb-3', collapsed && 'justify-center')}>
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-[#0F766E] text-xs text-white">
              {initials}
            </AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-xs font-medium text-[#F1F5F9]">
                {user ? `${user.first_name} ${user.last_name}` : 'Staff'}
              </p>
              <Badge variant="outline" className="mt-0.5 text-[10px] text-[#94A3B8] border-[#334155]">
                {user?.role?.replace(/_/g, ' ') ?? 'staff'}
              </Badge>
            </div>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={logout}
                className="rounded p-1.5 text-[#94A3B8] hover:bg-[#283548] hover:text-[#F1F5F9]"
                aria-label="Log out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </TooltipTrigger>
            <TooltipContent side="right">Log out</TooltipContent>
          </Tooltip>
        </div>

        {/* Collapse toggle */}
        <CollapseToggle collapsed={collapsed} />
      </div>
    </div>
  );
}

function CollapseToggle({ collapsed }: { collapsed: boolean }) {
  const { toggle } = useSidebarStore();

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          onClick={toggle}
          className="flex w-full items-center justify-center rounded p-1.5 text-[#94A3B8] hover:bg-[#283548] hover:text-[#F1F5F9]"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </TooltipTrigger>
      <TooltipContent side="right">
        {collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      </TooltipContent>
    </Tooltip>
  );
}

export function Sidebar() {
  const { isCollapsed, isMobileOpen, setMobileOpen } = useSidebarStore();

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={cn(
          'hidden h-screen shrink-0 transition-all duration-200 md:block',
          isCollapsed ? 'w-16' : 'w-56',
        )}
      >
        <SidebarContent collapsed={isCollapsed} />
      </aside>

      {/* Mobile sidebar */}
      <Sheet open={isMobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent side="left" className="w-56 p-0 bg-[#1E293B] border-[#334155]">
          <SidebarContent collapsed={false} />
        </SheetContent>
      </Sheet>
    </>
  );
}
