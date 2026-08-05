import { useEffect, useState } from "react";
import axios from "axios";

function Alerts() {
  const [alerts, setAlerts] = useState([]);

  const fetchAlerts = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/alerts");
      setAlerts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAlerts();

    const interval = setInterval(fetchAlerts, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 rounded-xl p-6 mt-10">
      <h2 className="text-2xl font-bold text-red-500 mb-4">
        🚨 Live Alerts
      </h2>

      {alerts.length === 0 ? (
        <p className="text-gray-400">No Alerts</p>
      ) : (
        alerts.map((alert, index) => (
          <div
            key={index}
            className="bg-red-600 text-white p-3 rounded-lg mb-2"
          >
            {alert}
          </div>
        ))
      )}
    </div>
  );
}

export default Alerts;