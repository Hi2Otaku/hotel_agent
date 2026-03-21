import { Link } from 'react-router';

export function Footer() {
  return (
    <footer className="bg-slate-800 text-slate-300">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* About */}
          <div>
            <h3 className="mb-3 text-base font-semibold text-white">About</h3>
            <p className="text-sm leading-relaxed">
              HotelBook is a modern hotel reservation platform. Search rooms,
              compare prices, and book your perfect stay with ease.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="mb-3 text-base font-semibold text-white">
              Quick Links
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  to="/search"
                  className="hover:text-white transition-colors"
                >
                  Search Rooms
                </Link>
              </li>
              <li>
                <Link
                  to="/pricing"
                  className="hover:text-white transition-colors"
                >
                  Pricing Calendar
                </Link>
              </li>
              <li>
                <Link
                  to="/my-bookings"
                  className="hover:text-white transition-colors"
                >
                  My Bookings
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="mb-3 text-base font-semibold text-white">
              Contact
            </h3>
            <ul className="space-y-2 text-sm">
              <li>info@hotelbook.demo</li>
              <li>123-456-7890</li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 border-t border-slate-700 pt-6 text-center text-sm">
          Powered by HotelBook
        </div>
      </div>
    </footer>
  );
}
