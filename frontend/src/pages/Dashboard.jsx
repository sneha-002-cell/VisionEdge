import { useEffect, useState } from "react";
import AnalyticsCard from "../components/AnalyticsCard";
import VideoPlayer from "../components/VideoPlayer";
import Charts from "../components/Charts";
import Alerts from "../components/Alerts";
import api from "../services/api";
import DownloadButtons from "../components/DownloadButtons";

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

        console.log("Analytics:", res.data);

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
    <div className="p-8 bg-slate-950 min-h-screen text-white">

      {/* Dashboard Title */}
      <h1 className="text-4xl font-bold mb-8">
        VisionEdge AI Dashboard
      </h1>

      {/* Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-6">

        <AnalyticsCard
          title="👤 People"
          value={analytics.people}
          color="#22c55e"
        />

        <AnalyticsCard
          title="🚗 Cars"
          value={analytics.cars}
          color="#3b82f6"
        />

        <AnalyticsCard
          title="🚌 Buses"
          value={analytics.buses}
          color="#f97316"
        />

        <AnalyticsCard
          title="🏍️ Bikes"
          value={analytics.motorcycles}
          color="#ec4899"
        />

        <AnalyticsCard
          title="📈 FPS"
          value={analytics.fps}
          color="#facc15"
        />

        <AnalyticsCard
          title="🔴 Crossings"
          value={analytics.line_crossings}
          color="#ef4444"
        />

      </div>

      {/* Live Video */}
      <div className="mt-10 rounded-xl overflow-hidden shadow-2xl">
        <VideoPlayer />
      </div>

      {/* Charts */}
      <div className="mt-10">
        <Charts
          history={history}
          analytics={analytics}
        />
      </div>

      {/* Alerts */}
      <div className="mt-10">
        <Alerts />
        <div className="mt-10">
  <DownloadButtons />
</div>
      </div>

    </div>
  );
}

export default Dashboard;