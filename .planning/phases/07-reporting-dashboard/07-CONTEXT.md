# Phase 7: Reporting Dashboard - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Staff can view actionable business analytics — occupancy rates, revenue summaries, and booking trends — through interactive charts on a single reports dashboard page. Includes backend aggregation endpoints, historical data seeding, and CSV/PDF export. All charts share a global date range picker. Clicking data points drills down to booking details via slide-out panel.

</domain>

<decisions>
## Implementation Decisions

### Chart Library & Style
- **Nivo** charting library (built on D3, rich chart types including calendar heatmap)
- Teal accent color palette matching existing staff dark theme (#0F766E primary, slate backgrounds, muted grid lines)
- Chart types per report:
  - Occupancy: Calendar heatmap (Nivo's `@nivo/calendar`) — adaptive to date range
  - Revenue: Stacked bar chart (`@nivo/bar`) — by category/room type
  - Booking trends: Line chart (`@nivo/line`) — booking volume over time

### Report Page Structure
- **Single dashboard-style page** — all 3 charts on one scrollable page
- Enable the existing "Reports" sidebar nav item (currently disabled with tooltip)
- 4 KPI summary cards at top: Total revenue (period), Average occupancy %, Total bookings, Average daily rate
- Charts stacked below cards: Occupancy heatmap → Revenue bar → Trends line
- Lazy-load the ReportsPage for code splitting (consistent with other pages)

### Date Range & Interactivity
- **Global date range picker** at top of page — shared across all charts
- Quick presets: Last 7d, 30d, 90d, This month, This year + custom date range picker
- All charts update when date range changes
- **Full drill-down**: Click a chart data point to see that day's bookings
- Hover tooltips with crosshair cursor for precise data reading
- Click a data series to isolate/highlight it

### Drill-Down Experience
- **Slide-out panel** on right side when clicking a data point
- Panel shows that day's/period's booking list with key details
- Chart stays visible behind the panel — context preserved
- Close panel to return to full dashboard view

### Export & Sharing
- **CSV export** button per chart — downloads current chart's data as CSV
- **PDF export** — snapshot of the full dashboard page (use html2canvas or similar)
- Export buttons in chart header area

### Loading & Empty States
- Skeleton chart placeholders while data loads
- "No data for this period" message with suggestion to select a different date range when empty
- Reuse existing LoadingSpinner and EmptyState components from staff common/

### Occupancy Heatmap
- **Adaptive to global date range** — heatmap adjusts display based on selected period
- Short ranges (7d): daily grid view
- Medium ranges (30-90d): monthly calendar grid
- Long ranges (6mo+): GitHub-contribution-style compact grid
- Color scale: light teal (low occupancy) → dark teal (high occupancy)

### Data Aggregation & Seeding
- **New backend reporting endpoints** in booking and room services
- Gateway BFF orchestrates calls to get aggregated report data
- Endpoints: daily occupancy, revenue by period/room type, booking trends by day
- **Seed 3-6 months of historical booking data** with realistic patterns (seasonal variation, weekday/weekend differences, cancellations) for impressive portfolio demo

### Claude's Discretion
- Exact responsive breakpoints for chart sizing
- Nivo chart configuration details (animations, transitions, axis formatting)
- PDF export library choice (html2canvas, jsPDF, etc.)
- Seed data generation algorithm and distribution patterns
- KPI card layout and responsive grid

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements are fully captured in decisions above and REQUIREMENTS.md.

### Requirements
- `.planning/REQUIREMENTS.md` — REPT-01 (occupancy), REPT-02 (revenue), REPT-03 (interactive trends)

### Prior Phase Context
- `.planning/phases/06-staff-dashboard/06-CONTEXT.md` — Staff dashboard architecture, dark theme, sidebar nav, component patterns
- `.planning/phases/06-staff-dashboard/06-02-SUMMARY.md` — Staff frontend scaffold details (API layer, auth store, component structure)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend-staff/src/components/common/LoadingSpinner.tsx` — Loading state component
- `frontend-staff/src/components/common/EmptyState.tsx` — Empty state with message
- `frontend-staff/src/components/common/StatusBadge.tsx` — Status badge for bookings in drill-down
- `frontend-staff/src/components/dashboard/MetricCard.tsx` — KPI card component (icon + value + label)
- `frontend-staff/src/api/client.ts` — Axios client with staff_access_token interceptor
- `frontend-staff/src/hooks/queries/useStaffBookings.ts` — TanStack Query hooks for booking data

### Established Patterns
- Dark admin theme via CSS variables in :root (slate-900 bg, teal #0F766E accent)
- Lazy-loaded pages via React.lazy for code splitting
- TanStack Query for data fetching with cache invalidation
- Zustand for client state (auth, sidebar)
- shadcn/ui components (Button, Card, Select, Popover, Sheet)

### Integration Points
- Sidebar: "Reports" nav item exists but is disabled — enable it and route to ReportsPage
- `frontend-staff/src/App.tsx` — Add lazy-loaded ReportsPage route
- Gateway BFF: Add reporting orchestration endpoints (new file `services/gateway/app/api/reports.py`)
- Booking service: Add reporting query endpoints (new file `services/booking/app/api/v1/reports.py`)
- Room service: Add occupancy aggregation endpoint

</code_context>

<specifics>
## Specific Ideas

- Calendar heatmap for occupancy is a Nivo strength — visually distinctive for portfolio
- Dashboard should feel like an executive overview — all metrics at a glance, drill down for details
- Historical seed data should show realistic hotel patterns: higher weekends, seasonal peaks, cancellation rate

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-reporting-dashboard*
*Context gathered: 2026-03-21*
