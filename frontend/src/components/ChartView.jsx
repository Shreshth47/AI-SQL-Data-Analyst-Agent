import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

const COLORS = ['#38bdf8', '#818cf8', '#c084fc', '#f472b6', '#fb7185'];

export default function ChartView({ chart }) {
  if (!chart || chart.type === 'none' || !chart.data || chart.data.length === 0) {
    return null;
  }

  const { type, data } = chart;

  return (
    <div className="w-full h-64 mt-4 p-3 bg-slate-900/80 rounded-lg border border-slate-700/80">
      <ResponsiveContainer width="100%" height="100%">
        {type === 'bar' && (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
            <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', borderRadius: '6px' }}
              itemStyle={{ color: '#38bdf8' }}
            />
            <Bar dataKey="value" fill="#38bdf8" radius={[4, 4, 0, 0]} />
          </BarChart>
        )}

        {type === 'line' && (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
            <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', borderRadius: '6px' }}
              itemStyle={{ color: '#818cf8' }}
            />
            <Line type="monotone" dataKey="value" stroke="#818cf8" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        )}

        {type === 'pie' && (
          <PieChart>
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', borderRadius: '6px' }}
            />
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}