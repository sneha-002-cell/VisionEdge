import { useEffect, useState } from "react";

import {
  BarChart3,
  Activity,
  Users,
  Car,
  Bus,
  Bike,
  Gauge,
  ArrowUpRight,
} from "lucide-react";

import Charts from "../components/Charts";
import api from "../services/api";


function Analytics() {

  const [analytics, setAnalytics] = useState({
    people: 0,
    cars: 0,
    buses: 0,
    motorcycles: 0,
    fps: 0,
    line_crossings: 0,
  });

  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");


  // ============================================================
  // FETCH ANALYTICS
  // ============================================================

  useEffect(() => {

    let mounted = true;


    const fetchAnalytics = async () => {

      try {

        const res = await api.get("/analytics");

        if (!mounted) {
          return;
        }


        const data = {

          people:
            Number(res.data?.people) || 0,

          cars:
            Number(res.data?.cars) || 0,

          buses:
            Number(res.data?.buses) || 0,

          motorcycles:
            Number(res.data?.motorcycles) || 0,

          fps:
            Number(res.data?.fps) || 0,

          line_crossings:
            Number(
              res.data?.line_crossings
            ) || 0,

        };


        setAnalytics(data);

        setError("");

        setLoading(false);


        // ======================================================
        // HISTORY
        // ======================================================

        setHistory((previous) => {

          const point = {

            time:
              new Date().toLocaleTimeString(),

            people:
              data.people,

            cars:
              data.cars,

            buses:
              data.buses,

            motorcycles:
              data.motorcycles,

          };


          return [
            ...previous.slice(-29),
            point,
          ];

        });

      } catch (err) {

        console.error(
          "Analytics request failed:",
          err
        );


        if (!mounted) {
          return;
        }


        setLoading(false);

        setError(
          err?.response?.data?.detail ||
          "Unable to load analytics data."
        );

      }

    };


    // Initial request

    fetchAnalytics();


    // Poll every second

    const interval = setInterval(
      fetchAnalytics,
      1000
    );


    return () => {

      mounted = false;

      clearInterval(interval);

    };

  }, []);


  // ============================================================
  // TOTAL OBJECTS
  // ============================================================

  const totalObjects =
    analytics.people +
    analytics.cars +
    analytics.buses +
    analytics.motorcycles;


  // ============================================================
  // RENDER
  // ============================================================

  return (

    <div className="page-content">


      {/* ======================================================
          PAGE HEADING
      ======================================================= */}

      <div className="page-heading">

        <div>

          <div className="eyebrow">

            <BarChart3 size={14} />

            DATA INTELLIGENCE

          </div>


          <h1>
            Analytics
          </h1>


          <p>
            Detailed AI detection metrics and
            behavioral trends.
          </p>

        </div>


        {/* LIVE STATUS */}

        <div
          className="heading-status"
          style={{
            color:
              error
                ? "#ef4444"
                : "#22c55e",
          }}
        >

          <span
            className="status-dot"
            style={{
              background:
                error
                  ? "#ef4444"
                  : "#22c55e",
            }}
          />

          {error
            ? "ANALYTICS ERROR"
            : loading
              ? "CONNECTING"
              : "LIVE ANALYTICS"}

        </div>

      </div>



      {/* ======================================================
          ERROR
      ======================================================= */}

      {error && (

        <div
          style={{
            marginBottom: "20px",
            padding: "14px 18px",
            borderRadius: "10px",
            border:
              "1px solid rgba(239,68,68,0.35)",
            background:
              "rgba(127,29,29,0.18)",
            color: "#fca5a5",
          }}
        >

          {error}

        </div>

      )}



      {/* ======================================================
          ANALYTICS BANNER
      ======================================================= */}

      <div className="analytics-banner">

        <Activity size={22} />

        <div>

          <strong>
            Real-Time Analytics Engine
          </strong>

          <span>
            Detection data is being updated continuously.
          </span>

        </div>

      </div>



      {/* ======================================================
          LIVE METRIC CARDS
      ======================================================= */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >


        {/* PEOPLE */}

        <MetricCard
          icon={<Users size={20} />}
          label="People"
          value={analytics.people}
        />


        {/* CARS */}

        <MetricCard
          icon={<Car size={20} />}
          label="Cars"
          value={analytics.cars}
        />


        {/* BUSES */}

        <MetricCard
          icon={<Bus size={20} />}
          label="Buses"
          value={analytics.buses}
        />


        {/* MOTORCYCLES */}

        <MetricCard
          icon={<Bike size={20} />}
          label="Motorcycles"
          value={analytics.motorcycles}
        />


        {/* FPS */}

        <MetricCard
          icon={<Gauge size={20} />}
          label="Processing FPS"
          value={analytics.fps.toFixed(1)}
        />


        {/* LINE CROSSINGS */}

        <MetricCard
          icon={<ArrowUpRight size={20} />}
          label="Line Crossings"
          value={analytics.line_crossings}
        />

      </div>



      {/* ======================================================
          TOTAL OBJECTS
      ======================================================= */}

      <div
        style={{
          marginBottom: "24px",
          padding: "18px 20px",
          borderRadius: "12px",
          border:
            "1px solid rgba(255,255,255,0.08)",
          background:
            "rgba(255,255,255,0.025)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >

        <div>

          <span
            style={{
              display: "block",
              fontSize: "12px",
              opacity: 0.6,
              marginBottom: "5px",
            }}
          >
            CURRENT DETECTED OBJECTS
          </span>

          <strong
            style={{
              fontSize: "28px",
            }}
          >
            {totalObjects}
          </strong>

        </div>


        <Activity
          size={26}
          style={{
            opacity: 0.7,
          }}
        />

      </div>



      {/* ======================================================
          CHARTS
      ======================================================= */}

      <Charts
        history={history}
        analytics={analytics}
      />

    </div>

  );

}


// ============================================================
// METRIC CARD
// ============================================================

function MetricCard({
  icon,
  label,
  value,
}) {

  return (

    <div
      style={{
        padding: "18px",
        borderRadius: "12px",
        border:
          "1px solid rgba(255,255,255,0.08)",
        background:
          "rgba(255,255,255,0.025)",
        minHeight: "100px",
      }}
    >

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "15px",
          opacity: 0.7,
        }}
      >

        {icon}

      </div>


      <span
        style={{
          display: "block",
          fontSize: "12px",
          opacity: 0.6,
          marginBottom: "5px",
        }}
      >
        {label}
      </span>


      <strong
        style={{
          fontSize: "25px",
        }}
      >
        {value}

      </strong>

    </div>

  );

}


export default Analytics;