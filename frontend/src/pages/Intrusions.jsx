import {
  ShieldAlert,
  Activity,
} from "lucide-react";

import Alerts from "../components/Alerts";

function Intrusions() {

  return (
    <div className="page-content">

      <div className="page-heading">

        <div>

          <div className="eyebrow danger-eyebrow">
            <ShieldAlert size={14} />
            SECURITY MONITORING
          </div>

          <h1>Intrusion Detection</h1>

          <p>
            Monitor restricted-zone violations and security events.
          </p>

        </div>

        <div className="heading-status threat">
          <span className="status-dot red-dot" />
          THREAT MONITORING ACTIVE
        </div>

      </div>

      <div className="security-banner">

        <div className="security-icon">
          <ShieldAlert size={26} />
        </div>

        <div>
          <strong>AI Security Monitoring</strong>

          <span>
            VisionEdge continuously monitors restricted zones
            and records detected intrusion events.
          </span>
        </div>

      </div>

      <Alerts />

    </div>
  );
}

export default Intrusions;