import { useEffect, useState } from "react";
import api from "../services/api";
import {
  ShieldAlert,
  Clock,
} from "lucide-react";

function Alerts() {

  const [alerts, setAlerts] = useState([]);

  const fetchAlerts = async () => {

    try {

      const res = await api.get("/alerts");

      setAlerts(res.data);

    } catch (err) {

      console.error("Alert error:", err);

    }

  };

  useEffect(() => {

    fetchAlerts();

    const interval = setInterval(
      fetchAlerts,
      2000
    );

    return () => clearInterval(interval);

  }, []);

  return (
    <div className="alerts-panel">

      <div className="alerts-header">

        <div>

          <div className="section-kicker danger-eyebrow">
            SECURITY EVENTS
          </div>

          <h2>
            <ShieldAlert size={22} />
            Intrusion Alerts
          </h2>

        </div>

        <div className="alert-count">
          {alerts.length} EVENTS
        </div>

      </div>

      {alerts.length === 0 ? (

        <div className="no-alerts">

          <div className="safe-icon">
            ✓
          </div>

          <strong>
            No active security threats
          </strong>

          <span>
            VisionEdge is monitoring the environment.
          </span>

        </div>

      ) : (

        <div className="alerts-list">

          {alerts.map((alert, index) => (

            <div
              key={index}
              className="alert-item"
            >

              <div className="alert-icon">
                <ShieldAlert size={19} />
              </div>

              <div className="alert-information">

                <strong>
                  Intrusion Detected
                </strong>

                <span>
                  {alert}
                </span>

              </div>

              <div className="alert-time">
                <Clock size={14} />
                LIVE
              </div>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}

export default Alerts;