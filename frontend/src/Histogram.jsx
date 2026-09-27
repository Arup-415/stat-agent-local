import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function Histogram({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 16, left: 0, bottom: 30 }}>
        <CartesianGrid stroke="rgba(150, 180, 195, 0.13)" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="interval" angle={-24} textAnchor="end" tick={{ fill: "#91a4ae", fontSize: 10 }} axisLine={{ stroke: "#34424d" }} tickLine={false} />
        <YAxis allowDecimals={false} tick={{ fill: "#91a4ae", fontSize: 10 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={{ background: "#0b1119", border: "1px solid #31505c", color: "#d6e7ed" }} />
        <Bar dataKey="count" name="Observations" fill="#00cfea" maxBarSize={54} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default Histogram;

export function GroupComparison({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 16, left: 0, bottom: 20 }}>
        <CartesianGrid stroke="rgba(150, 180, 195, 0.13)" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="group" tick={{ fill: "#91a4ae", fontSize: 10 }} axisLine={{ stroke: "#34424d" }} tickLine={false} />
        <YAxis tick={{ fill: "#91a4ae", fontSize: 10 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={{ background: "#0b1119", border: "1px solid #31505c", color: "#d6e7ed" }} />
        <Legend />
        <Bar dataKey="mean" name="Mean" fill="#00cfea" maxBarSize={48} />
        <Bar dataKey="median" name="Median" fill="#f5b942" maxBarSize={48} />
      </BarChart>
    </ResponsiveContainer>
  );
}