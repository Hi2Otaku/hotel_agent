import { SearchForm } from '@/components/search/SearchForm';

export default function Landing() {
  return (
    <div className="min-h-[calc(100vh-64px)]">
      <div className="grid min-h-[calc(100vh-64px)] lg:grid-cols-2">
        {/* Mobile hero photo */}
        <div className="relative h-64 lg:hidden">
          <img
            src="https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=1200"
            alt="Oceanfront resort with palm trees and pool"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
        </div>

        {/* Left: Search form */}
        <div className="flex items-center justify-center px-4 py-16 md:px-8 lg:px-16">
          <div className="w-full max-w-md">
            <h1 className="mb-2 text-4xl font-semibold leading-tight">
              Find Your Perfect Stay
            </h1>
            <p className="mb-8 text-base text-muted">
              Search available rooms and book your beach getaway
            </p>
            <SearchForm />
          </div>
        </div>

        {/* Right: Desktop photo */}
        <div className="relative hidden lg:block">
          <img
            src="https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=1200"
            alt="Oceanfront resort with palm trees and pool"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
        </div>
      </div>
    </div>
  );
}
