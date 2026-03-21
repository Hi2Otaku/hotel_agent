# Phase 7: Reporting Dashboard - Research

**Researched:** 2026-03-21
**Domain:** Data visualization (Nivo charts), backend aggregation endpoints, CSV/PDF export
**Confidence:** HIGH

## Summary

Phase 7 adds a single Reports dashboard page to the staff frontend with three Nivo charts (calendar heatmap, stacked bar, line), four KPI summary cards, a global date range picker, drill-down panel, and CSV/PDF export. The backend needs new aggregation endpoints in the booking service (daily occupancy, revenue by room type, booking trends) and a gateway BFF orchestration layer. Historical seed data (3-6 months) must be generated in the booking service for portfolio demo purposes.

The existing codebase provides strong patterns to follow: TanStack Query hooks for data fetching, MetricCard component for KPIs, Sheet component for the drill-down panel, lazy-loaded page routes, and the gateway BFF orchestration pattern with httpx and asyncio.gather. Nivo v0.99 is the current stable release and provides all three required chart types with responsive wrappers.

**Primary recommendation:** Build backend aggregation endpoints first (booking service reports + room service occupancy), then gateway BFF orchestration, then frontend components. Use Nivo's ResponsiveCalendar, ResponsiveBar, and ResponsiveLine with dark theme configuration. Use html-to-image + jsPDF for PDF export (lighter and more reliable than html2canvas).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Nivo** charting library (built on D3, rich chart types including calendar heatmap)
- Teal accent color palette matching existing staff dark theme (#0F766E primary, slate backgrounds, muted grid lines)
- Chart types: Occupancy = Calendar heatmap (@nivo/calendar), Revenue = Stacked bar (@nivo/bar), Booking trends = Line chart (@nivo/line)
- Single dashboard-style page -- all 3 charts on one scrollable page
- Enable existing "Reports" sidebar nav item (currently disabled with tooltip)
- 4 KPI summary cards at top: Total revenue, Average occupancy %, Total bookings, Average daily rate
- Global date range picker at top, shared across all charts
- Quick presets: Last 7d, 30d, 90d, This month, This year + custom date range picker
- Full drill-down: Click chart data point to see bookings via slide-out panel (Sheet)
- CSV export per chart, PDF export for full dashboard
- Skeleton chart placeholders while loading; "No data for this period" empty states
- Occupancy heatmap adaptive to date range: daily grid (7d), monthly calendar (30-90d), compact grid (6mo+)
- New backend reporting endpoints in booking and room services
- Gateway BFF orchestrates report data aggregation
- Seed 3-6 months of historical booking data with realistic patterns
- Lazy-load ReportsPage for code splitting

### Claude's Discretion
- Exact responsive breakpoints for chart sizing
- Nivo chart configuration details (animations, transitions, axis formatting)
- PDF export library choice (html2canvas, jsPDF, etc.)
- Seed data generation algorithm and distribution patterns
- KPI card layout and responsive grid

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REPT-01 | Staff dashboard shows occupancy rate by date range | Nivo ResponsiveCalendar heatmap with adaptive display modes; backend daily occupancy aggregation endpoint; room count from room service |
| REPT-02 | Staff dashboard shows revenue summary | Nivo ResponsiveBar stacked chart by room type; backend revenue aggregation endpoint grouping by room_type_id and time period |
| REPT-03 | Staff dashboard shows booking trend charts (interactive) | Nivo ResponsiveLine with click handlers; backend booking trends endpoint; drill-down panel via Sheet component |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| @nivo/core | 0.99.0 | Shared chart theming and utilities | Required base for all Nivo charts |
| @nivo/calendar | 0.99.0 | Calendar heatmap for occupancy | Locked decision; provides ResponsiveCalendar |
| @nivo/bar | 0.99.0 | Stacked bar chart for revenue | Locked decision; provides ResponsiveBar |
| @nivo/line | 0.99.0 | Line chart for booking trends | Locked decision; provides ResponsiveLine |
| @nivo/tooltip | 0.99.0 | Custom tooltip rendering | Required for crosshair cursor and styled tooltips |
| date-fns | 4.1.0 | Date range calculations | Already installed; used for preset date ranges |
| html-to-image | 1.11.13 | Capture dashboard as image for PDF | Lighter than html2canvas, better SVG support for Nivo charts |
| jspdf | 4.2.1 | Generate PDF from captured image | Pairs with html-to-image for PDF export |

### Supporting (already installed)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tanstack/react-query | 5.91.3 | Data fetching for report endpoints | All report data fetching with caching |
| sonner | 2.0.7 | Toast notifications | PDF export progress/success/error toasts |
| lucide-react | 0.577.0 | Icons for KPI cards and buttons | DollarSign, Percent, CalendarCheck, TrendingUp, Download |
| radix-ui | 1.4.3 | Underlying primitives for shadcn | Sheet (drill-down), Popover (date picker), ToggleGroup (presets) |

### shadcn Components to Install
| Component | Purpose |
|-----------|---------|
| Calendar | Date range picker calendar widget |
| Toggle Group | Date range quick preset selector |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| html-to-image | html2canvas | html2canvas has known issues with SVG elements (Nivo renders SVG); html-to-image handles SVG natively |
| jspdf | @react-pdf/renderer | jspdf is simpler for screenshot-to-PDF; @react-pdf is for building PDF documents from scratch |

**Installation:**
```bash
cd frontend-staff
npm install @nivo/core@0.99.0 @nivo/calendar@0.99.0 @nivo/bar@0.99.0 @nivo/line@0.99.0 @nivo/tooltip@0.99.0 html-to-image jspdf
npx shadcn@latest add calendar toggle-group
```

## Architecture Patterns

### Recommended Project Structure
```
frontend-staff/src/
├── pages/
│   └── ReportsPage.tsx              # Lazy-loaded page shell
├── components/reports/
│   ├── DateRangePicker.tsx           # Global date range with presets
│   ├── OccupancyHeatmap.tsx          # Nivo calendar heatmap (adaptive)
│   ├── RevenueChart.tsx              # Nivo stacked bar
│   ├── BookingTrendsChart.tsx        # Nivo line chart
│   ├── ChartContainer.tsx            # Wrapper: heading + export + skeleton
│   ├── DrillDownPanel.tsx            # Sheet-based slide-out panel
│   └── DrillDownBookingRow.tsx       # Single booking row in panel
├── hooks/queries/
│   └── useReports.ts                 # TanStack Query hooks for report data
├── api/
│   └── reports.ts                    # Axios API functions for report endpoints
└── lib/
    └── export.ts                     # CSV generation + PDF export utilities

services/booking/app/
├── api/v1/
│   └── reports.py                    # Staff report query endpoints
├── services/
│   ├── reports.py                    # Aggregation query logic
│   └── seed_bookings.py             # Historical booking seed data generator

services/room/app/
├── api/v1/
│   └── reports.py                    # Occupancy aggregation endpoint

services/gateway/app/
├── api/
│   └── reports.py                    # BFF orchestration for report data
```

### Pattern 1: Gateway BFF Report Orchestration
**What:** Gateway fetches occupancy from room service and revenue/trends from booking service in parallel via asyncio.gather, then merges into a single response.
**When to use:** All report data fetching (matches existing staff_overview pattern).
**Example:**
```python
# services/gateway/app/api/reports.py
@router.get("/api/v1/staff/reports")
async def staff_reports(request: Request):
    headers = _auth_headers(request)
    query_string = str(request.url.query)

    async with httpx.AsyncClient(timeout=30.0) as client:
        async def fetch_occupancy():
            resp = await client.get(
                f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/reports/occupancy?{query_string}",
                headers=headers,
            )
            return resp.json() if resp.status_code == 200 else {"daily": []}

        async def fetch_revenue():
            resp = await client.get(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/reports/revenue?{query_string}",
                headers=headers,
            )
            return resp.json() if resp.status_code == 200 else {"data": []}

        async def fetch_trends():
            resp = await client.get(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/reports/trends?{query_string}",
                headers=headers,
            )
            return resp.json() if resp.status_code == 200 else {"data": []}

        occupancy, revenue, trends = await asyncio.gather(
            fetch_occupancy(), fetch_revenue(), fetch_trends()
        )

    return {"occupancy": occupancy, "revenue": revenue, "trends": trends}
```

### Pattern 2: TanStack Query Hook with Date Range
**What:** Report data hook accepts date range params, uses them as query key for automatic refetch.
**When to use:** All frontend report data fetching.
**Example:**
```typescript
// hooks/queries/useReports.ts
export function useReportData(dateRange: { from: string; to: string }) {
  return useQuery({
    queryKey: ['reports', dateRange.from, dateRange.to],
    queryFn: () => getReportData(dateRange),
    staleTime: 5 * 60 * 1000,  // 5 min -- report data doesn't change fast
    enabled: !!dateRange.from && !!dateRange.to,
  });
}
```

### Pattern 3: Nivo Dark Theme Configuration
**What:** Shared Nivo theme object matching the staff dark theme CSS variables.
**When to use:** Applied to all three Nivo charts for consistent appearance.
**Example:**
```typescript
// Shared Nivo theme for dark staff dashboard
const nivoTheme = {
  background: 'transparent',
  text: { fontSize: 12, fill: '#94A3B8' },
  axis: {
    ticks: { text: { fill: '#94A3B8', fontSize: 11 } },
    legend: { text: { fill: '#94A3B8', fontSize: 12 } },
  },
  grid: { line: { stroke: '#334155', strokeOpacity: 0.4 } },
  tooltip: {
    container: {
      background: '#1E293B',
      color: '#F1F5F9',
      fontSize: 12,
      borderRadius: '6px',
      border: '1px solid #334155',
    },
  },
  crosshair: { line: { stroke: '#0F766E', strokeWidth: 1 } },
};
```

### Pattern 4: Adaptive Heatmap Display
**What:** OccupancyHeatmap switches Nivo Calendar configuration based on date range length.
**When to use:** Occupancy chart rendering.
**Example:**
```typescript
function getHeatmapConfig(dayCount: number) {
  if (dayCount <= 14) {
    // Daily grid: single row of cells
    return { direction: 'horizontal' as const, cellSize: 'auto' };
  } else if (dayCount <= 90) {
    // Standard calendar grid
    return { direction: 'horizontal' as const, cellSize: undefined };
  } else {
    // Compact contribution-style
    return { direction: 'horizontal' as const, cellSize: 10 };
  }
}
```

### Pattern 5: CSV Export Utility
**What:** Generic CSV generation from chart data arrays.
**When to use:** Per-chart CSV export buttons.
**Example:**
```typescript
// lib/export.ts
export function downloadCSV(data: Record<string, unknown>[], filename: string) {
  const headers = Object.keys(data[0]);
  const rows = data.map(row => headers.map(h => String(row[h] ?? '')).join(','));
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
```

### Pattern 6: Backend Aggregation Queries
**What:** SQL aggregation queries using SQLAlchemy for daily occupancy, revenue by room type, and booking volume.
**When to use:** Booking service report endpoints.
**Example:**
```python
# Occupancy: count bookings per day where check_in <= day < check_out
# Revenue: SUM(total_price) GROUP BY room_type_id, date_trunc('day/week/month', check_in)
# Trends: COUNT(*) GROUP BY date_trunc('day', created_at) for booking volume

from sqlalchemy import func, cast, Date, and_
from sqlalchemy.future import select

async def get_daily_occupancy(db: AsyncSession, start: date, end: date, total_rooms: int):
    """Return daily occupancy percentages for the date range."""
    # Generate date series, count overlapping bookings per day
    # occupancy_pct = bookings_overlapping_day / total_rooms * 100
```

### Anti-Patterns to Avoid
- **Fetching all bookings client-side for aggregation:** Always aggregate in the backend SQL queries. Never send raw booking rows to the frontend for charting.
- **Separate API calls per chart:** Use a single BFF endpoint that fetches all report data in parallel, or at most 2-3 endpoints. Avoid N+1 API calls.
- **Hardcoding chart dimensions:** Use Nivo's Responsive* wrappers and let the container div control sizing.
- **Coupling seed data to production models:** Keep seed_bookings.py separate from production booking creation logic.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Calendar heatmap | Custom SVG/Canvas calendar | @nivo/calendar ResponsiveCalendar | Complex date grid layout, color scales, tooltips |
| Stacked bar chart | Custom D3 bars | @nivo/bar ResponsiveBar | Stacking math, animations, legends, responsive sizing |
| Line chart with crosshair | Custom SVG path rendering | @nivo/line ResponsiveLine | Bezier curves, crosshair interaction, point detection |
| PDF generation | Custom canvas rendering | html-to-image + jspdf | SVG capture, page formatting, file download |
| CSV generation | Complex serialization | Simple map/join utility | CSV is trivial but easy to get encoding wrong |
| Date range presets | Manual date math | date-fns (subDays, startOfMonth, startOfYear) | Already installed, handles edge cases |
| Date picker calendar | Custom date grid | shadcn Calendar (Radix + date-fns) | Accessibility, keyboard nav, range selection |

**Key insight:** Nivo handles all the hard charting work (scales, axes, responsive sizing, tooltips, animations). The implementation effort is in data transformation (backend aggregation) and wiring (API -> hooks -> chart props), not chart rendering.

## Common Pitfalls

### Pitfall 1: Nivo Calendar Date Format
**What goes wrong:** Nivo's ResponsiveCalendar requires data in `{ day: "YYYY-MM-DD", value: number }` format. Backend returns dates as ISO datetime strings or date objects, causing silent render failures.
**Why it happens:** Python's date serialization differs from Nivo's expected format.
**How to avoid:** Ensure backend returns dates as "YYYY-MM-DD" strings. Add explicit formatting in the API response schema.
**Warning signs:** Heatmap renders but shows no colored cells despite data being present.

### Pitfall 2: Nivo Calendar `from`/`to` Props
**What goes wrong:** ResponsiveCalendar requires explicit `from` and `to` date strings matching the data range. If omitted or wrong, the calendar renders empty or with wrong date range.
**Why it happens:** Unlike bar/line which auto-scale, calendar needs explicit date boundaries.
**How to avoid:** Always pass `from` and `to` props derived from the date range picker state.
**Warning signs:** Calendar shows but covers wrong months or appears empty.

### Pitfall 3: Nivo SVG Container Sizing
**What goes wrong:** Nivo Responsive* components render to 0x0 if their parent container has no explicit height.
**Why it happens:** SVG elements don't have intrinsic sizing; Nivo uses the parent's dimensions.
**How to avoid:** Always set explicit height on the chart container div (e.g., `h-[300px]`).
**Warning signs:** Charts render but are invisible or show console warnings about dimensions.

### Pitfall 4: Large Date Ranges in Occupancy Query
**What goes wrong:** Naive approach generates a row per day per room for overlap checking, causing O(days * rooms) query complexity.
**Why it happens:** Occupancy requires counting how many bookings overlap each individual day.
**How to avoid:** Use a date series CTE with generate_series and join against bookings. Or pre-aggregate by counting distinct bookings that overlap each day using range overlap logic.
**Warning signs:** Report endpoints become slow (>2s) for 6-month ranges.

### Pitfall 5: PDF Export with Nivo SVG
**What goes wrong:** html2canvas fails to render Nivo charts correctly because they use SVG, not Canvas.
**Why it happens:** html2canvas has limited SVG support and often produces blank rectangles for complex SVGs.
**How to avoid:** Use html-to-image (which uses foreignObject or serializes SVG directly) instead of html2canvas.
**Warning signs:** PDF exports show blank white rectangles where charts should be.

### Pitfall 6: Seed Data Referencing Non-Existent Room Types
**What goes wrong:** Booking seed data uses hardcoded room_type_ids that don't match the actual seeded room types.
**Why it happens:** Room types are seeded with auto-generated UUIDs in the room service database; booking service has a separate database.
**How to avoid:** Seed booking data must either: (a) query room types from the room service API, or (b) use a shared seed script that seeds both services, or (c) hardcode known UUIDs in both seed scripts. Option (c) is simplest for a demo project.
**Warning signs:** Report queries return zero results because room_type_id foreign keys don't match.

### Pitfall 7: Date Range Picker Timezone Issues
**What goes wrong:** Date range picker returns local timezone dates, but backend expects UTC dates, causing off-by-one day errors.
**Why it happens:** JavaScript Date objects include timezone offset; "2026-03-21" in PST is different from UTC.
**How to avoid:** Use date-fns `format(date, 'yyyy-MM-dd')` to send date-only strings. Backend treats them as date (not datetime).
**Warning signs:** Data for day boundaries appears in wrong adjacent day.

## Code Examples

### Nivo ResponsiveCalendar (Occupancy Heatmap)
```typescript
import { ResponsiveCalendar } from '@nivo/calendar';

interface OccupancyData {
  day: string;    // "2026-01-15"
  value: number;  // 0-100 (percentage)
}

<div style={{ height: 300 }}>
  <ResponsiveCalendar
    data={occupancyData}
    from={dateRange.from}
    to={dateRange.to}
    emptyColor="#1E293B"
    colors={['#134E4A', '#0F766E', '#14B8A6', '#5EEAD4']}
    margin={{ top: 20, right: 32, bottom: 40, left: 48 }}
    yearSpacing={40}
    monthBorderColor="#334155"
    dayBorderWidth={2}
    dayBorderColor="#0F172A"
    theme={nivoTheme}
    onClick={(datum) => handleDrillDown(datum.day)}
    tooltip={({ day, value }) => (
      <div style={{ background: '#1E293B', padding: 8, border: '1px solid #334155', borderRadius: 6 }}>
        <strong style={{ color: '#F1F5F9' }}>{day}</strong>
        <br />
        <span style={{ color: '#94A3B8' }}>Occupancy: {value}%</span>
      </div>
    )}
  />
</div>
```

### Nivo ResponsiveBar (Revenue Chart)
```typescript
import { ResponsiveBar } from '@nivo/bar';

// Data shape: [{ period: "Jan 2026", garden_room: 12500, ocean_view: 18200, ... }]
<div style={{ height: 300 }}>
  <ResponsiveBar
    data={revenueData}
    keys={roomTypeKeys}  // ['garden_room', 'ocean_view', 'junior_suite', 'beachfront_villa']
    indexBy="period"
    margin={{ top: 20, right: 130, bottom: 40, left: 60 }}
    padding={0.3}
    colors={['#0F766E', '#2DB87E', '#D98C2E', '#A855F7']}
    borderRadius={2}
    theme={nivoTheme}
    axisLeft={{ format: (v) => `$${(v / 1000).toFixed(0)}k` }}
    enableLabel={false}
    legends={[{
      dataFrom: 'keys',
      anchor: 'bottom-right',
      direction: 'column',
      translateX: 120,
      itemWidth: 100,
      itemHeight: 20,
      itemTextColor: '#94A3B8',
    }]}
    onClick={(datum) => handleDrillDown(datum.indexValue, datum.id)}
  />
</div>
```

### Nivo ResponsiveLine (Booking Trends)
```typescript
import { ResponsiveLine } from '@nivo/line';

// Data shape: [{ id: "Bookings", data: [{ x: "2026-01-15", y: 12 }, ...] }]
<div style={{ height: 300 }}>
  <ResponsiveLine
    data={trendsData}
    margin={{ top: 20, right: 32, bottom: 40, left: 48 }}
    xScale={{ type: 'time', format: '%Y-%m-%d', precision: 'day' }}
    xFormat="time:%b %d"
    yScale={{ type: 'linear', min: 0, max: 'auto' }}
    curve="monotoneX"
    colors={['#0F766E']}
    pointSize={6}
    pointColor="#0F172A"
    pointBorderWidth={2}
    pointBorderColor="#0F766E"
    enableCrosshair={true}
    crosshairType="x"
    useMesh={true}
    theme={nivoTheme}
    axisBottom={{
      format: '%b %d',
      tickRotation: -45,
    }}
    onClick={(point) => handleDrillDown(point.data.x)}
  />
</div>
```

### PDF Export with html-to-image + jsPDF
```typescript
import { toPng } from 'html-to-image';
import { jsPDF } from 'jspdf';
import { toast } from 'sonner';

export async function exportDashboardPDF(
  elementRef: HTMLElement,
  filename: string
) {
  toast('Generating PDF...');
  try {
    const dataUrl = await toPng(elementRef, {
      backgroundColor: '#0F172A',
      pixelRatio: 2,
    });
    const pdf = new jsPDF('landscape', 'mm', 'a4');
    const imgProps = pdf.getImageProperties(dataUrl);
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
    pdf.addImage(dataUrl, 'PNG', 0, 0, pdfWidth, pdfHeight);
    pdf.save(filename);
    toast.success('PDF downloaded successfully');
  } catch {
    toast.error('Failed to generate PDF. Please try again.');
  }
}
```

### Backend Occupancy Aggregation (SQLAlchemy)
```python
from datetime import date, timedelta
from sqlalchemy import func, and_, case
from sqlalchemy.future import select

async def get_daily_occupancy(
    db: AsyncSession, start_date: date, end_date: date, total_rooms: int
) -> list[dict]:
    """Calculate daily occupancy percentage for date range."""
    results = []
    current = start_date
    # Batch query: count bookings overlapping each day
    # A booking overlaps day D if check_in <= D and check_out > D
    while current <= end_date:
        count = await db.scalar(
            select(func.count()).select_from(Booking).where(
                and_(
                    Booking.check_in <= current,
                    Booking.check_out > current,
                    Booking.status.in_(['confirmed', 'checked_in', 'checked_out']),
                )
            )
        )
        occupancy_pct = round((count / total_rooms * 100) if total_rooms > 0 else 0, 1)
        results.append({"day": current.isoformat(), "value": occupancy_pct})
        current += timedelta(days=1)
    return results
```

**Note:** For ranges > 90 days, consider a single query using a date series CTE for efficiency instead of N individual queries.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Chart.js for React | Nivo (D3-based, React-native) | Stable since 2023 | Better React integration, declarative API, built-in responsive wrappers |
| html2canvas for screenshots | html-to-image | 2023+ | Better SVG support, smaller bundle, more reliable |
| Custom date pickers | shadcn Calendar (Radix-based) | 2024 | Accessible, composable, theme-consistent |
| Manual CSV string building | Blob + URL.createObjectURL | Stable | Standard browser API, handles encoding correctly |

**Deprecated/outdated:**
- recharts: Simpler but lacks calendar heatmap; Nivo chosen per locked decision
- victory: Less maintained than Nivo; fewer chart types
- html2canvas: Known SVG rendering issues; use html-to-image instead

## Open Questions

1. **Occupancy calculation: rooms vs bookings**
   - What we know: We have 55 total rooms across 4 types. Occupancy = booked rooms / total rooms per day.
   - What's unclear: Should occupancy use total_rooms (55) or available rooms per type? The decision says "occupancy rate" generically.
   - Recommendation: Use total property rooms (55) as denominator for simplicity. The room count can be fetched from the room service.

2. **Revenue aggregation grouping**
   - What we know: Revenue by room type is the primary breakdown. Date range affects the time axis.
   - What's unclear: For short ranges (7d), should bars be daily? For long ranges (year), monthly?
   - Recommendation: Auto-adapt grouping: daily for <30d, weekly for 30-90d, monthly for >90d.

3. **Historical seed data cross-service consistency**
   - What we know: Booking and room services have separate databases. Seed bookings need valid room_type_ids from the room service.
   - What's unclear: Best way to ensure ID consistency across services.
   - Recommendation: Use a deterministic UUID approach (e.g., uuid5 from room type slugs) so both services generate matching IDs, or have the booking seed script fetch room types from the room service API.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest 4.1.0 (jsdom) for frontend; pytest for backend |
| Config file | `frontend-staff/vitest.config.ts` (exists); no backend test config |
| Quick run command | `cd frontend-staff && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend-staff && npx vitest run --reporter=verbose` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REPT-01 | Occupancy heatmap renders with data | unit | `cd frontend-staff && npx vitest run src/components/reports/OccupancyHeatmap.test.tsx` | No -- Wave 0 |
| REPT-02 | Revenue chart renders stacked bars | unit | `cd frontend-staff && npx vitest run src/components/reports/RevenueChart.test.tsx` | No -- Wave 0 |
| REPT-03 | Trends chart renders with click handler | unit | `cd frontend-staff && npx vitest run src/components/reports/BookingTrendsChart.test.tsx` | No -- Wave 0 |
| REPT-01-03 | ReportsPage integrates all charts | unit | `cd frontend-staff && npx vitest run src/pages/ReportsPage.test.tsx` | No -- Wave 0 |
| REPT-01-03 | Date range picker updates all charts | unit | `cd frontend-staff && npx vitest run src/components/reports/DateRangePicker.test.tsx` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend-staff && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend-staff && npx vitest run --reporter=verbose`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `frontend-staff/src/components/reports/OccupancyHeatmap.test.tsx` -- covers REPT-01
- [ ] `frontend-staff/src/components/reports/RevenueChart.test.tsx` -- covers REPT-02
- [ ] `frontend-staff/src/components/reports/BookingTrendsChart.test.tsx` -- covers REPT-03
- [ ] `frontend-staff/src/pages/ReportsPage.test.tsx` -- covers REPT-01, REPT-02, REPT-03 integration
- [ ] `frontend-staff/src/components/reports/DateRangePicker.test.tsx` -- covers date range interaction
- [ ] Nivo charts may need mock due to SVG rendering in jsdom; consider `vi.mock('@nivo/calendar')` etc.

## Sources

### Primary (HIGH confidence)
- Project codebase: `services/gateway/app/api/staff.py` -- BFF orchestration pattern
- Project codebase: `frontend-staff/src/hooks/queries/useStaffBookings.ts` -- TanStack Query hook pattern
- Project codebase: `frontend-staff/src/components/dashboard/MetricCard.tsx` -- KPI card component
- Project codebase: `services/booking/app/models/booking.py` -- Booking model with status enum
- Project codebase: `services/room/app/services/seed.py` -- Seed data pattern (55 rooms, 4 types)
- npm registry: @nivo/* packages v0.99.0 (verified via `npm view`)
- npm registry: html-to-image v1.11.13, jspdf v4.2.1 (verified via `npm view`)

### Secondary (MEDIUM confidence)
- [Nivo Calendar docs](https://nivo.rocks/calendar/) -- ResponsiveCalendar API and data format
- [Nivo Bar docs](https://nivo.rocks/bar/) -- ResponsiveBar stacked configuration
- [Nivo Line docs](https://nivo.rocks/line/) -- ResponsiveLine with time scale
- [GitHub plouc/nivo](https://github.com/plouc/nivo) -- Calendar types.ts for TypeScript interfaces

### Tertiary (LOW confidence)
- html-to-image vs html2canvas SVG handling -- based on common community reports; should be verified during implementation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- Nivo v0.99.0 confirmed on npm; all supporting libraries already installed or version-verified
- Architecture: HIGH -- follows established project patterns (BFF orchestration, TanStack Query hooks, lazy-loaded pages)
- Pitfalls: HIGH -- based on direct code inspection (SVG sizing, date formats, cross-service IDs) and well-known Nivo behaviors
- Backend aggregation: MEDIUM -- SQL aggregation patterns are standard but exact query optimization for large date ranges may need tuning

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (Nivo 0.99 is stable; unlikely to have breaking changes)
