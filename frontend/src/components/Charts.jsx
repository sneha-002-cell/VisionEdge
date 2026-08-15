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


function Charts({
  history = [],
  analytics = {},
}) {


  // ============================================================
  // SAFE VALUES
  // ============================================================

  const people =
    Number(analytics.people) || 0;

  const cars =
    Number(analytics.cars) || 0;

  const buses =
    Number(analytics.buses) || 0;

  const motorcycles =
    Number(analytics.motorcycles) || 0;


  // ============================================================
  // PIE DATA
  // ============================================================

  const pieData = [

    {
      name: "People",
      value: people,
    },

    {
      name: "Cars",
      value: cars,
    },

    {
      name: "Buses",
      value: buses,
    },

    {
      name: "Motorcycles",
      value: motorcycles,
    },

  ];


  const colors = [

    "#20e37b",
    "#3b82f6",
    "#f59e0b",
    "#a855f7",

  ];


  const totalObjects =
    people +
    cars +
    buses +
    motorcycles;


  return (

    <div className="charts-grid">


      {/* ======================================================
          PEOPLE TREND
      ======================================================= */}

      <div className="chart-panel">


        <div className="chart-panel-header">

          <div>

            <span className="section-kicker">
              REAL-TIME
            </span>

            <h3>
              People Detection
            </h3>

          </div>


          <div className="chart-live">

            <span className="status-dot" />

            LIVE

          </div>

        </div>


        <div
          className="chart-container"
          style={{
            width: "100%",
            height: "320px",
            minHeight: "320px",
          }}
        >

          {history.length > 0 ? (

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <LineChart
                data={history}
                margin={{
                  top: 10,
                  right: 20,
                  left: 0,
                  bottom: 5,
                }}
              >

                <XAxis
                  dataKey="time"
                  stroke="#596579"
                  tick={{
                    fill: "#7d8a9e",
                    fontSize: 11,
                  }}
                  axisLine={false}
                  tickLine={false}
                />


                <YAxis
                  allowDecimals={false}
                  stroke="#596579"
                  tick={{
                    fill: "#7d8a9e",
                    fontSize: 11,
                  }}
                  axisLine={false}
                  tickLine={false}
                />


                <Tooltip
                  contentStyle={{
                    background: "#101820",
                    border:
                      "1px solid #263340",
                    borderRadius: "10px",
                    color: "#fff",
                  }}
                />


                <Line
                  type="monotone"
                  dataKey="people"
                  name="People"
                  stroke="#20e37b"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{
                    r: 5,
                  }}
                />

              </LineChart>

            </ResponsiveContainer>

          ) : (

            <EmptyChart
              text="Waiting for analytics data..."
            />

          )}

        </div>

      </div>



      {/* ======================================================
          OBJECT DISTRIBUTION
      ======================================================= */}

      <div className="chart-panel">


        <div className="chart-panel-header">

          <div>

            <span className="section-kicker">
              CURRENT
            </span>

            <h3>
              Object Distribution
            </h3>

          </div>

        </div>


        <div
          className="pie-wrapper"
          style={{
            position: "relative",
            width: "100%",
            height: "320px",
            minHeight: "320px",
          }}
        >

          {totalObjects > 0 ? (

            <>

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <PieChart>

                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={105}
                    innerRadius={65}
                    paddingAngle={4}
                  >

                    {pieData.map(
                      (entry, index) => (

                        <Cell
                          key={entry.name}
                          fill={colors[index]}
                          stroke="none"
                        />

                      )
                    )}

                  </Pie>


                  <Tooltip
                    contentStyle={{
                      background:
                        "#101820",
                      border:
                        "1px solid #263340",
                      borderRadius:
                        "10px",
                      color: "#fff",
                    }}
                  />

                </PieChart>

              </ResponsiveContainer>


              <div className="pie-center">

                <strong>
                  {totalObjects}
                </strong>

                <span>
                  OBJECTS
                </span>

              </div>

            </>

          ) : (

            <EmptyChart
              text="No objects detected"
            />

          )}

        </div>


        {/* LEGEND */}

        <div className="chart-legend">

          {pieData.map(
            (item, index) => (

              <div
                className="legend-item"
                key={item.name}
              >

                <span
                  className="legend-color"
                  style={{
                    background:
                      colors[index],
                  }}
                />


                <span>
                  {item.name}
                </span>


                <strong>
                  {item.value}
                </strong>

              </div>

            )
          )}

        </div>

      </div>

    </div>

  );

}


// ============================================================
// EMPTY CHART
// ============================================================

function EmptyChart({
  text,
}) {

  return (

    <div
      style={{
        height: "100%",
        width: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: 0.55,
        fontSize: "14px",
      }}
    >

      {text}

    </div>

  );

}


export default Charts;