function AnalyticsCard({
  title,
  value,
  icon: Icon,
  accent = "green",
}) {
  return (
    <div className={`stat-card ${accent}`}>

      <div className="stat-card-top">

        <div className="stat-icon">
          <Icon size={20} />
        </div>

        <span className="stat-live">
          LIVE
        </span>

      </div>

      <div className="stat-value">
        {value}
      </div>

      <div className="stat-title">
        {title}
      </div>

      <div className="stat-footer">
        <span>Real-time reading</span>
        <span className="mini-dot" />
      </div>

    </div>
  );
}

export default AnalyticsCard;