import { Bell, Menu } from 'lucide-react';
import { useSidebarStore } from '@/stores/sidebarStore';
import { useAuthStore } from '@/stores/authStore';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface TopBarProps {
  title: string;
}

export function TopBar({ title }: TopBarProps) {
  const { setMobileOpen } = useSidebarStore();
  const { user, logout } = useAuthStore();

  const initials = user
    ? `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase()
    : 'ST';

  return (
    <header
      className="flex h-14 shrink-0 items-center justify-between border-b border-[#334155] bg-[#0F172A] px-4 md:px-6"
      role="banner"
    >
      {/* Left side */}
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <button
          className="rounded p-1.5 text-[#94A3B8] hover:bg-[#283548] hover:text-[#F1F5F9] md:hidden"
          onClick={() => setMobileOpen(true)}
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </button>
        <h1 className="text-xl font-semibold text-[#F1F5F9]">{title}</h1>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Notification bell (placeholder) */}
        <button
          className="rounded p-1.5 text-[#94A3B8] hover:bg-[#283548] hover:text-[#F1F5F9]"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
        </button>

        {/* Avatar dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="rounded-full focus:outline-none focus:ring-2 focus:ring-[#0F766E]">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-[#0F766E] text-xs text-white">
                  {initials}
                </AvatarFallback>
              </Avatar>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-[#1E293B] border-[#334155]">
            <DropdownMenuItem
              onClick={logout}
              className="text-[#F1F5F9] focus:bg-[#283548] focus:text-[#F1F5F9] cursor-pointer"
            >
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
