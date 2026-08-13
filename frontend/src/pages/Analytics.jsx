import { useEffect, useState } from "react";
import { BarChart3, Activity } from "lucide-react";

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

      } catch (error) {
        console.error(error);
      }

    };

    fetchAnalytics();

    const interval = setInterval(
      fetchAnalytics,
      1000
    );

    return () => clearInterval(interval);

  }, []);

  return (
    <div className="page-content">

      <div className="page-heading">

        <div>
          <div className="eyebrow">
            <BarChart3 size={14} />
            DATA INTELLIGENCE
          </div>

          <h1>Analytics</h1>

          <p>
            Detailed AI detection metrics and behavioral trends.
          </p>
        </div>

      </div>

      <div className="analytics-banner">

        <Activity size={22} />

        <div>
          <strong>Real-Time Analytics Engine</strong>

          <span>
            Detection data is being updated continuously.
          </span>
        </div>

      </div>

      <Charts
        history={history}
        analytics={analytics}
      />

    </div>
  );
}

export default Analytics;