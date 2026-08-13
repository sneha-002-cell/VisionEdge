import { useEffect, useState } from "react";
import {
  Users,
  Car,
  Bus,
  Bike,
  Gauge,
  ArrowUpRight,
  Activity,
} from "lucide-react";

import AnalyticsCard from "../components/AnalyticsCard";
import Charts from "../components/Charts";
import api from "../services/api";

function Dashboard() {
  const [analytics, setAnalytics] = useState({
    people: 0,
    cars: 0,
    buses: 0,
    motorcycles: 0,
    fps: 0,
    line_crossings: 0,
  });

  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.get("/analytics");

        setAnalytics(res.data);

        setHistory((prev) => [
          ...prev.slice(-19),
          {
            time: new Date().toLocaleTimeString(),
            people: res.data.people,
            cars: res.data.cars,
            buses: res.data.buses,
            motorcycles: res.data.motorcycles,
          },
        ]);
      } catch (err) {
        console.error("Analytics Error:", err);
      }
    };

    fetchAnalytics();

    const interval = setInterval(fetchAnalytics, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page-content">

      {/* Page heading */}

      <div className="page-heading">

        <div>
          <div className="eyebrow">
            <Activity size={14} />
            REAL-TIME INTELLIGENCE
          </div>

          <h1>Security Overview</h1>

          <p>
            Real-time AI video analytics and surveillance monitoring.
          </p>
        </div>

        <div className="heading-status">
          <span className="status-dot" />
          Detection Engine Active
        </div>

      </div>

      {/* Statistics */}

      <div className="stats-grid">

        <AnalyticsCard
          title="People"
          value={analytics.people}
          icon={Users}
          accent="green"
        />

        <AnalyticsCard
          title="Vehicles"
          value={analytics.cars}
          icon={Car}
          accent="blue"
        />

        <AnalyticsCard
          title="Buses"
          value={analytics.buses}
          icon={Bus}
          accent="orange"
        />

        <AnalyticsCard
          title="Motorcycles"
          value={analytics.motorcycles}
          icon={Bike}
          accent="purple"
        />

        <AnalyticsCard
          title="Processing FPS"
          value={Number(analytics.fps || 0).toFixed(2)}
          icon={Gauge}
          accent="yellow"
        />

        <AnalyticsCard
          title="Line Crossings"
          value={analytics.line_crossings}
          icon={ArrowUpRight}
          accent="red"
        />

      </div>

      {/* Quick access */}

      <div className="section-header">
        <div>
          <span className="section-kicker">QUICK ACCESS</span>
          <h2>Monitoring Center</h2>
        </div>
      </div>

      <div className="quick-grid">

        <a href="/live-camera" className="quick-card">
          <div className="quick-icon green">
            <Activity size={22} />
          </div>

          <div>
            <h3>Live Camera</h3>
            <p>View real-time AI detection feed</p>
          </div>

          <ArrowUpRight size={18} />
        </a>

        <a href="/analytics" className="quick-card">
          <div className="quick-icon blue">
            <Gauge size={22} />
          </div>

          <div>
            <h3>Analytics</h3>
            <p>Analyze detection trends and statistics</p>
          </div>

          <ArrowUpRight size={18} />
        </a>

        <a href="/intrusions" className="quick-card danger">
          <div className="quick-icon red">
            <Activity size={22} />
          </div>

          <div>
            <h3>Security Events</h3>
            <p>Review intrusion detections</p>
          </div>

          <ArrowUpRight size={18} />
        </a>

      </div>

      {/* Charts */}

      <div className="section-header chart-heading">
        <div>
          <span className="section-kicker">ANALYTICS</span>
          <h2>Detection Intelligence</h2>
        </div>
      </div>

      <Charts
        history={history}
        analytics={analytics}
      />

    </div>
  );
}

export default Dashboard;