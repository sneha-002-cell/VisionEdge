import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Video,
  BarChart3,
  ShieldAlert,
  FileText,
  Activity,
  ScanLine,
} from "lucide-react";

function Sidebar() {
  const links = [
    {
      path: "/dashboard",
      label: "Dashboard",
      icon: LayoutDashboard,
    },
    {
      path: "/live-camera",
      label: "Live Camera",
      icon: Video,
    },
    {
      path: "/analytics",
      label: "Analytics",
      icon: BarChart3,
    },
    {
      path: "/intrusions",
      label: "Intrusions",
      icon: ShieldAlert,
    },
    {
      path: "/reports",
      label: "Reports",
      icon: FileText,
    },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <ScanLine size={23} />
        </div>

        <div>
          <h1>VisionEdge</h1>
          <span>AI VIDEO INTELLIGENCE</span>
        </div>
      </div>

      <div className="sidebar-section-title">
        MONITORING
      </div>

      <nav className="sidebar-nav">
        {links.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <Icon size={19} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="system-indicator">
          <div className="status-dot" />

          <div>
            <strong>System Online</strong>
            <span>Monitoring active</span>
          </div>
        </div>

        <div className="sidebar-version">
          VisionEdge v1.0
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;