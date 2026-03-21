import { toPng } from 'html-to-image';
import { jsPDF } from 'jspdf';
import { toast } from 'sonner';

/**
 * Download an array of objects as a CSV file.
 */
export function downloadCSV(data: Record<string, unknown>[], filename: string) {
  if (!data.length) return;

  const headers = Object.keys(data[0]);
  const rows = data.map((row) =>
    headers
      .map((h) => {
        const val = String(row[h] ?? '');
        // Escape values containing commas or quotes
        return val.includes(',') || val.includes('"')
          ? `"${val.replace(/"/g, '""')}"`
          : val;
      })
      .join(','),
  );

  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Capture an HTML element as a PNG and save as a landscape PDF.
 */
export async function exportDashboardPDF(
  elementRef: HTMLElement,
  dateRange: { from: string; to: string },
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
    pdf.save(`hotelbook-reports-${dateRange.from}-${dateRange.to}.pdf`);
    toast.success('PDF downloaded successfully');
  } catch {
    toast.error('Failed to generate PDF. Please try again.');
  }
}
