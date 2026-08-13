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
    {
      name: "People",
      value: Number(analytics.people) || 0,
    },
    {
      name: "Cars",
      value: Number(analytics.cars) || 0,
    },
    {
      name: "Buses",
      value: Number(analytics.buses) || 0,
    },
    {
      name: "Motorcycles",
      value: Number(analytics.motorcycles) || 0,
    },
  ];

  const colors = [
    "#20e37b",
    "#3b82f6",
    "#f59e0b",
    "#a855f7",
  ];

  return (
    <div className="charts-grid">

      {/* PEOPLE TREND */}

      <div className="chart-panel">

        <div className="chart-panel-header">

          <div>
            <span className="section-kicker">
              REAL-TIME
            </span>

            <h3>People Detection</h3>
          </div>

          <div className="chart-live">
            <span className="status-dot" />
            LIVE
          </div>

        </div>

        <div className="chart-container">

          <ResponsiveContainer width="100%" height="100%">

            <LineChart data={history}>

              <XAxis
                dataKey="time"
                stroke="#596579"
                tick={{ fill: "#7d8a9e", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                stroke="#596579"
                tick={{ fill: "#7d8a9e", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />

              <Tooltip
                contentStyle={{
                  background: "#101820",
                  border: "1px solid #263340",
                  borderRadius: "10px",
                  color: "#fff",
                }}
              />

              <Line
                type="monotone"
                dataKey="people"
                stroke="#20e37b"
                strokeWidth={3}
                dot={false}
                activeDot={{
                  r: 5,
                  fill: "#20e37b",
                }}
              />

            </LineChart>

          </ResponsiveContainer>

        </div>

      </div>

      {/* DISTRIBUTION */}

      <div className="chart-panel">

        <div className="chart-panel-header">

          <div>
            <span className="section-kicker">
              CURRENT
            </span>

            <h3>Object Distribution</h3>
          </div>

        </div>

        <div className="pie-wrapper">

          <ResponsiveContainer width="100%" height="100%">

            <PieChart>

              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                outerRadius={110}
                innerRadius={68}
                paddingAngle={4}
              >

                {pieData.map((entry, index) => (
                  <Cell
                    key={entry.name}
                    fill={colors[index]}
                    stroke="none"
                  />
                ))}

              </Pie>

              <Tooltip
                contentStyle={{
                  background: "#101820",
                  border: "1px solid #263340",
                  borderRadius: "10px",
                  color: "#fff",
                }}
              />

            </PieChart>

          </ResponsiveContainer>

          <div className="pie-center">
            <strong>
              {pieData.reduce(
                (sum, item) => sum + item.value,
                0
              )}
            </strong>

            <span>OBJECTS</span>
          </div>

        </div>

        <div className="chart-legend">

          {pieData.map((item, index) => (
            <div
              className="legend-item"
              key={item.name}
            >
              <span
                className="legend-color"
                style={{
                  background: colors[index],
                }}
              />

              <span>{item.name}</span>

              <strong>{item.value}</strong>
            </div>
          ))}

        </div>

      </div>

    </div>
  );
}

export default Charts;