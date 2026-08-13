import {
  Bell,
  CircleUserRound,
  Wifi,
} from "lucide-react";

function Topbar({ title = "Dashboard" }) {
  return (
    <header className="topbar">

      <div>
        <div className="topbar-breadcrumb">
          VISIONEDGE / MONITORING
        </div>

        <h2>{title}</h2>
      </div>

      <div className="topbar-right">

        <div className="live-status">
          <span className="status-dot" />
          LIVE
        </div>

        <div className="topbar-icon">
          <Wifi size={18} />
        </div>

        <div className="topbar-icon">
          <Bell size={18} />
        </div>

        <div className="profile">
          <CircleUserRound size={20} />
          <span>Operator</span>
        </div>

      </div>

    </header>
  );
}

export default Topbar;