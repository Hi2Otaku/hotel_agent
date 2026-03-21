# Phase 7: Reporting Dashboard - Validation Architecture

**Created:** 2026-03-21
**Source:** 07-RESEARCH.md Validation Architecture section

## Test Framework

| Property | Value |
|----------|-------|
| Framework | Vitest 4.1.0 (jsdom) for frontend; pytest for backend |
| Config file | `frontend-staff/vitest.config.ts` (exists) |
| Quick run command | `cd frontend-staff && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend-staff && npx vitest run --reporter=verbose` |

## Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REPT-01 | Occupancy heatmap renders with data | unit | `cd frontend-staff && npx vitest run src/components/reports/OccupancyHeatmap.test.tsx` | No -- Wave 0 (07-00-PLAN.md) |
| REPT-02 | Revenue chart renders stacked bars | unit | `cd frontend-staff && npx vitest run src/components/reports/RevenueChart.test.tsx` | No -- Wave 0 (07-00-PLAN.md) |
| REPT-03 | Trends chart renders with click handler | unit | `cd frontend-staff && npx vitest run src/components/reports/BookingTrendsChart.test.tsx` | No -- Wave 0 (07-00-PLAN.md) |
| REPT-01-03 | ReportsPage integrates all charts | unit | `cd frontend-staff && npx vitest run src/pages/ReportsPage.test.tsx` | No -- Wave 0 (07-00-PLAN.md) |
| REPT-01-03 | Date range picker updates all charts | unit | `cd frontend-staff && npx vitest run src/components/reports/DateRangePicker.test.tsx` | No -- Wave 0 (07-00-PLAN.md) |

## Wave 0 Plan

Plan `07-00-PLAN.md` creates all 5 test stub files with:
- `vi.mock()` for `@nivo/calendar`, `@nivo/bar`, `@nivo/line` (jsdom cannot render SVG)
- `it.todo()` placeholder tests describing expected behaviors
- Stubs run cleanly under Vitest (todo tests reported as pending)

## Sampling Rate

- **Per task commit:** `cd frontend-staff && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend-staff && npx vitest run --reporter=verbose`
- **Phase gate:** Full suite green before `/gsd:verify-work`

## Notes

- Nivo charts render SVG which jsdom cannot process; all chart component tests must mock Nivo packages
- Backend endpoints (booking service, room service, gateway) have no existing test infrastructure; backend tests are deferred to Phase 8
- Test stubs use `it.todo()` pattern -- implementation plans should convert these to real assertions as components are built
