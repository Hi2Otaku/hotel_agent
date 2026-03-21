# Phase 7 — UI Review

**Audited:** 2026-03-22
**Baseline:** UI-SPEC.md (07-UI-SPEC.md) — approved design contract
**Screenshots:** Captured (dev server at localhost:5174) — staff frontend redirects to login, code-only audit performed for reports page

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Chart error copy not rendered; date picker label renders "Last 30d" not "Last 30 days" |
| 2. Visuals | 3/4 | Strong visual hierarchy; heatmap adaptive logic is a no-op (all branches return same config) |
| 3. Color | 3/4 | All hex values from approved palette; one off-spec color (#64748B) and no CSS variable usage |
| 4. Typography | 4/4 | Precisely matches 4-role spec: xs/sm/text-[20px], semibold/mono only |
| 5. Spacing | 4/4 | All spacing uses declared scale; chart heights and panel width use spec-sanctioned exceptions |
| 6. Experience Design | 2/4 | No chart-level error state on main fetch; prefers-reduced-motion not implemented |

**Overall: 19/24**

---

## Top 3 Priority Fixes

1. **Chart-level error state missing** — If the backend /api/v1/staff/reports endpoint fails, all three charts silently render as "No data for this period" with no user feedback. Staff cannot distinguish a server error from genuinely empty data. Fix: add `isError` to `useReportData` destructure in `ReportsPage.tsx` and pass an `error` prop to `ChartContainer`, which renders "Failed to load chart data. Check your connection and try again." in place of the empty state. (ReportsPage.tsx:35, ChartContainer.tsx:9)

2. **Occupancy heatmap adaptive display is a dead code path** — The spec defines three distinct display modes (daily grid ≤14d, monthly calendar 15-90d, compact 91+d), but `OccupancyHeatmap.tsx` lines 23-31 return `direction: 'horizontal'` for all three branches — the `if` statements are structurally correct but all produce identical config. The medium-range calendar (15-90d) should use the default Nivo vertical/horizontal layout without override, and the 91+ compact mode should use a reduced `cellSize`. Fix in OccupancyHeatmap.tsx calendarConfig useMemo.

3. **Date range preset display label mismatch** — The spec specifies the default label reads "Last 30 days" but the DateRangePicker `displayLabel` function (line 80) renders `Last ${preset.label}` where label is "30d", producing "Last 30d". This applies to all presets (shows "Last 7d", "Last 30d", "Last 90d"). Fix: set preset labels to "7 days", "30 days", "90 days" or compute the display separately from the chip label.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)

The bulk of the copywriting contract is met precisely:

- Page title renders "Reports" in sidebar nav (Sidebar.tsx — enabled)
- Export PDF button: "Export PDF" — correct (ReportsPage.tsx:67)
- Export CSV button: "Export CSV" — correct (ChartContainer.tsx:41)
- KPI labels: "Total Revenue", "Avg Occupancy", "Total Bookings", "Avg Daily Rate" — all match (ReportsPage.tsx:79,83,88,93)
- Chart headings: "Occupancy Rate", "Revenue by Room Type", "Booking Trends" — all match (ReportsPage.tsx:104,125,151)
- Empty state heading: "No data for this period" — matches (ChartContainer.tsx:51)
- Empty state body: "Try selecting a different date range to view reporting data." — matches (ChartContainer.tsx:53)
- PDF toasts: "Generating PDF...", "PDF downloaded successfully", "Failed to generate PDF. Please try again." — all match (export.ts:43,55,57)
- Drill-down title: "Bookings for {date}" pattern — matches (DrillDownPanel.tsx:37)
- Drill-down empty: "No bookings found for this date. Try selecting a different date on the chart." — matches (DrillDownPanel.tsx:59)

**Gaps:**

- Chart error copy "Failed to load chart data. Check your connection and try again." is never rendered. ChartContainer has no error prop, and ReportsPage does not consume `isError` from `useReportData`. (ReportsPage.tsx:35 — only `data` and `isLoading` destructured)
- Drill-down error message reads "Failed to load booking details." (DrillDownPanel.tsx:53) — spec does not define this string explicitly, but it differs from the chart error copy pattern.
- Date picker preset display label: "Last 30d" is rendered where "Last 30 days" is expected. Affects all numeric presets. (DateRangePicker.tsx:80)

---

### Pillar 2: Visuals (3/4)

Visual hierarchy is strong and matches the spec layout contract:

- KPI row anchors the page as primary visual focal point (4 large MetricCards at 32px/600)
- Three chart sections stacked vertically beneath KPIs, each wrapped in a dark Card
- ChartContainer title is left-aligned at 20px/semibold; Export CSV ghost button is right-aligned in the same row — matches layout spec
- Drill-down panel uses SheetContent with side="right" and w-[400px] on sm+ breakpoints — correct
- Date range picker with ToggleGroup presets is positioned top-left; Export PDF ghost button is top-right — matches layout spec diagram
- Icon-only elements: none found (all buttons have text labels; chart icons are decorative Nivo-rendered elements with role="img" and aria-label)
- Role="img" + aria-label applied to all three chart wrappers (OccupancyHeatmap.tsx:34, RevenueChart.tsx:40, BookingTrendsChart.tsx:23)

**Gaps:**

- Heatmap adaptive display is non-functional (see Priority Fix #2). The occupancy heatmap will look identical for a 7-day view and a 6-month view, reducing visual clarity for short date ranges where a daily grid view would be more informative.
- No visually-hidden summary table exists per chart (spec accessibility requirement: "supplement with visually-hidden summary table per chart"). This is a secondary concern but impacts screen reader experience.
- Focus management for drill-down panel: SheetContent from shadcn handles Radix Dialog focus trapping automatically, so this is likely met, but no explicit `onOpenAutoFocus`/`onCloseAutoFocus` customization is present to return focus to the triggering chart element.

---

### Pillar 3: Color (3/4)

All hex values used across report components are drawn from the approved palette in UI-SPEC §Color:

| Color | Spec Role | Uses in code |
|-------|-----------|--------------|
| #0F172A | Dominant background | Skeleton bg, chart background, PDF capture bg |
| #1E293B | Secondary (cards) | ChartContainer Card, DrillDownPanel, PopoverContent, Heatmap tooltip |
| #334155 | Border | All border classes across components |
| #0F766E | Accent teal | Active preset chip, loading spinner, trendline color, pointBorderColor, crosshair |
| #94A3B8 | Muted text | Secondary labels, axis labels, ghost button text |
| #F1F5F9 | Foreground | Primary text, headings, hover states |
| #DC2626 | Destructive | DrillDownPanel error text |

**One off-spec color:**
- `#64748B` (Slate 500) used in ChartContainer.tsx:52 for the empty state secondary text. This color is not listed in the spec color table. The spec designates `#94A3B8` (Slate 400) as muted text. Using Slate 500 instead reduces contrast slightly. Fix: change `text-[#64748B]` to `text-[#94A3B8]` at ChartContainer.tsx:52.

**Hardcoded hex values vs CSS variables:**
The entire report subsystem uses hardcoded hex values rather than Tailwind CSS variables (`text-muted-foreground`, `bg-card`, `border-border`). This is a deliberate architectural choice for Nivo integration compatibility and is consistent with the existing staff theme approach. Not flagged as a defect given the pattern was pre-established.

**Accent usage scope:**
Accent (#0F766E) is confined to: active date preset chip, loading spinner, line chart color, crosshair, point border — all within the allowed list from the spec. No accent overuse on decorative elements detected.

---

### Pillar 4: Typography (4/4)

Typography matches the spec's 4-role system precisely.

**Sizes found in report components:**
- `text-xs` (12px) — label role: axis labels (via nivoTheme fontSize: 12), secondary text in DrillDownBookingRow, tooltip text
- `text-sm` (14px) — body role: DrillDownPanel content, error/empty state text, Export button labels
- `text-[20px]` — heading role: ChartContainer title (exactly as specified)

No `text-lg`, `text-xl`, `text-2xl`, or other sizes found. Display size (32px) is inherited from the pre-existing MetricCard component and not repeated here.

**Weights found:**
- `font-semibold` — heading at 20px (ChartContainer.tsx:29) — correct
- `font-mono` — confirmation numbers in DrillDownBookingRow (DrillDownBookingRow.tsx:26) — appropriate for confirmations, not in conflict with spec

No `font-bold`, `font-light`, or `font-medium` found in report components. Weight discipline is excellent.

**Line heights:**
- `leading-[1.2]` for ChartContainer heading — matches spec (Heading: 1.2 line height)

---

### Pillar 5: Spacing (4/4)

Spacing is consistent with the declared scale (multiples of 4px):

| Class | Value | Spec Token | Location |
|-------|-------|------------|----------|
| `p-4` | 16px | md | ChartContainer card padding |
| `gap-4` | 16px | md | ReportsPage top row gap, KPI grid gap |
| `gap-2` | 8px | sm | DateRangePicker preset gap |
| `space-y-6` | 24px | lg | ReportsPage outer vertical spacing |
| `mt-8` | 32px | xl | Charts section top margin |
| `space-y-8` | 32px | xl | Gap between chart sections |
| `py-3` | 12px | 3 Tailwind units | DrillDownBookingRow row padding |
| `py-8` | 32px | xl | Empty/error state vertical padding in DrillDown |
| `py-12` | 48px | 2xl | Loading spinner vertical padding in DrillDown |
| `px-4` | 16px | md | DrillDown body horizontal padding |

**Spec-sanctioned exceptions present:**
- `h-[220px]`, `h-[260px]`, `h-[300px]` — responsive chart heights (explicitly declared in spec Layout Contract §Chart Sections)
- `w-[400px]` — drill-down panel width (explicitly declared in spec Layout Contract §Drill-Down Panel)
- `text-[20px]`, `leading-[1.2]` — typography spec values

KPI grid uses `grid-cols-2 lg:grid-cols-4 gap-4` — exactly matches spec §KPI Row.

No unapproved arbitrary px or rem values found.

---

### Pillar 6: Experience Design (2/4)

**States present:**
- Loading: Skeleton fills each chart container while `isLoading` is true (ChartContainer.tsx:47-48). KPI values show '-' while loading (ReportsPage.tsx:77,83,89,95). Export buttons disabled during load (ChartContainer.tsx:37, ReportsPage.tsx:63). This is the correct behavior.
- Empty: Per-chart empty state renders "No data for this period" with suggestion text (ChartContainer.tsx:49-55). Drill-down empty state renders (DrillDownPanel.tsx:57-61).
- Error (drill-down): Drill-down panel shows error message when `isError` is true (DrillDownPanel.tsx:51-54).
- Disabled states: Export CSV disabled when loading or empty (ChartContainer.tsx:37). Export PDF disabled when loading or no data (ReportsPage.tsx:63).

**States missing:**

1. **Chart-level error state for main data fetch** (critical): `useReportData` at ReportsPage.tsx:35 only destructures `{ data, isLoading }` — `isError` is silently discarded. When the gateway /api/v1/staff/reports endpoint fails, all charts receive `empty={true}` and show "No data for this period" — indistinguishable from a legitimate empty response. The UI-SPEC mandates: "Individual chart error: Show inline error message within that chart container; other charts unaffected." ChartContainer needs an `error?: boolean` prop to render the "Failed to load chart data..." message.

2. **prefers-reduced-motion not implemented** (spec requirement): The UI-SPEC accessibility section lists "Respect `prefers-reduced-motion`: disable Nivo chart animations when enabled." The shared `nivoTheme` in chartTheme.ts has no `animate` or `motionConfig` control. Fix: read `window.matchMedia('(prefers-reduced-motion: reduce)')` in chartTheme.ts and conditionally export `animate: false` to Nivo chart props.

3. **No error boundary at page level**: If a chart component throws (e.g., malformed data from API), no ErrorBoundary wraps the report components. A single runtime error would crash the entire ReportsPage to a blank white screen.

4. **Revenue chart shows UUID substrings as room type labels** (UX): RevenueChart.tsx:18 uses `row.room_type_id.substring(0, 8)` as both the data key and legend label. Bar chart legend will display cryptic strings like "a3f2e1d0" instead of human-readable room type names. The backend should return room type names, or the frontend should map UUIDs to display names. This degrades the readability of the most data-rich chart.

---

## Registry Safety

shadcn is initialized. UI-SPEC Registry Safety table lists only "shadcn official" blocks (Calendar, Toggle Group) — no third-party registries present.

Registry audit: 0 third-party blocks to check, no flags.

---

## Files Audited

**Phase 7 report components:**
- `frontend-staff/src/pages/ReportsPage.tsx`
- `frontend-staff/src/components/reports/ChartContainer.tsx`
- `frontend-staff/src/components/reports/DateRangePicker.tsx`
- `frontend-staff/src/components/reports/OccupancyHeatmap.tsx`
- `frontend-staff/src/components/reports/RevenueChart.tsx`
- `frontend-staff/src/components/reports/BookingTrendsChart.tsx`
- `frontend-staff/src/components/reports/DrillDownPanel.tsx`
- `frontend-staff/src/components/reports/DrillDownBookingRow.tsx`
- `frontend-staff/src/lib/chartTheme.ts`
- `frontend-staff/src/lib/export.ts`
- `frontend-staff/src/hooks/queries/useReports.ts`

**Supporting context:**
- `.planning/phases/07-reporting-dashboard/07-UI-SPEC.md`
- `.planning/phases/07-reporting-dashboard/07-CONTEXT.md`
- `.planning/phases/07-reporting-dashboard/07-00-SUMMARY.md`
- `.planning/phases/07-reporting-dashboard/07-01-SUMMARY.md`
- `.planning/phases/07-reporting-dashboard/07-02-SUMMARY.md`
- `.planning/phases/07-reporting-dashboard/07-03-SUMMARY.md`
- `frontend-staff/components.json`

**Screenshots:**
- `.planning/ui-reviews/07-20260322-010019/desktop.png` — guest frontend (5173, wrong app)
- `.planning/ui-reviews/07-20260322-010019/staff-reports-desktop.png` — staff app (5174, shows login wall)
