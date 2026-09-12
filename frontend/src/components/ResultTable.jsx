import React from 'react';

export default function ResultTable({ rows }) {
  if (!rows || rows.length === 0) return null;

  const columns = Object.keys(rows[0]);

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-700 mt-3 bg-slate-900/60">
      <table className="w-full text-left text-xs text-slate-300">
        <thead className="bg-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
          <tr>
            {columns.map((col) => (
              <th key={col} className="px-3.5 py-2.5 font-medium border-b border-slate-700">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 font-mono">
          {rows.map((row, idx) => (
            <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
              {columns.map((col) => (
                <td key={col} className="px-3.5 py-2 whitespace-nowrap">
                  {row[col] !== null ? String(row[col]) : 'NULL'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}