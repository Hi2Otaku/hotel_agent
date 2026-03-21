import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { Menu, X, User, LogOut, BookOpen } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
} from '@/components/ui/sheet';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navLinks = [
    { to: '/search', label: 'Search' },
    { to: '/pricing', label: 'Pricing' },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-16 border-b border-slate-200 bg-white">
      <nav className="mx-auto flex h-full max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <Link
          to="/"
          className="text-xl font-semibold text-accent"
        >
          HotelBook
        </Link>

        {/* Desktop navigation */}
        <div className="hidden items-center gap-2 lg:flex">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="flex min-h-[44px] items-center px-3 text-sm font-medium text-slate-700 hover:text-accent"
            >
              {link.label}
            </Link>
          ))}

          {isAuthenticated && (
            <Link
              to="/my-bookings"
              className="flex min-h-[44px] items-center px-3 text-sm font-medium text-slate-700 hover:text-accent"
            >
              My Bookings
            </Link>
          )}

          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="min-h-[44px] gap-2"
                >
                  <User className="h-5 w-5" />
                  <span className="text-sm">
                    {user?.first_name || 'Account'}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => navigate('/my-bookings')}>
                  <BookOpen className="mr-2 h-4 w-4" />
                  My Bookings
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Link to="/login">
              <Button variant="default" className="min-h-[44px] bg-accent hover:bg-accent-hover">
                Log In
              </Button>
            </Link>
          )}
        </div>

        {/* Mobile hamburger */}
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="min-h-[44px] min-w-[44px] lg:hidden"
              aria-label="Open menu"
            >
              {mobileOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-72">
            <SheetTitle className="text-lg font-semibold text-accent">
              Menu
            </SheetTitle>
            <div className="mt-6 flex flex-col gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="flex min-h-[44px] items-center rounded-md px-3 text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-accent"
                  onClick={() => setMobileOpen(false)}
                >
                  {link.label}
                </Link>
              ))}

              {isAuthenticated && (
                <Link
                  to="/my-bookings"
                  className="flex min-h-[44px] items-center rounded-md px-3 text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-accent"
                  onClick={() => setMobileOpen(false)}
                >
                  My Bookings
                </Link>
              )}

              <div className="my-2 border-t border-slate-200" />

              {isAuthenticated ? (
                <button
                  onClick={() => {
                    handleLogout();
                    setMobileOpen(false);
                  }}
                  className="flex min-h-[44px] items-center rounded-md px-3 text-base font-medium text-slate-700 hover:bg-slate-100"
                >
                  <LogOut className="mr-2 h-5 w-5" />
                  Logout
                </button>
              ) : (
                <Link
                  to="/login"
                  className="flex min-h-[44px] items-center rounded-md px-3 text-base font-medium text-accent hover:bg-slate-100"
                  onClick={() => setMobileOpen(false)}
                >
                  Log In
                </Link>
              )}
            </div>
          </SheetContent>
        </Sheet>
      </nav>
    </header>
  );
}
