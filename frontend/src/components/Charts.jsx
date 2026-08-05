import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

function Charts({ history, analytics }) {
  const pieData = [
    { name: "People", value: analytics.people },
    { name: "Cars", value: analytics.cars },
    { name: "Buses", value: analytics.buses },
    { name: "Motorcycles", value: analytics.motorcycles },
  ];

  const colors = ["#22c55e", "#3b82f6", "#f97316", "#ec4899"];

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mt-8">

      {/* Line Chart */}
      <div className="bg-slate-900 rounded-2xl p-6 shadow-xl">
        <h2 className="text-2xl font-bold mb-5 text-white">
          Live People Count
        </h2>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={history}>
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="people"
              stroke="#22c55e"
              strokeWidth={3}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Pie Chart */}
      <div className="bg-slate-900 rounded-2xl p-6 shadow-xl">
        <h2 className="text-2xl font-bold mb-5 text-white">
          Object Distribution
        </h2>

        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              dataKey="value"
              outerRadius={100}
              label
            >
              {pieData.map((entry, index) => (
                <Cell
                  key={index}
                  fill={colors[index]}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}

export default Charts;