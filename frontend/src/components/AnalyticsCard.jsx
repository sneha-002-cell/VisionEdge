function AnalyticsCard({ title, value, color }) {
  return (
    <div
      className="rounded-2xl shadow-xl p-6 bg-slate-900 transition-transform duration-300 hover:scale-105"
      style={{
        borderTop: `6px solid ${color}`,
      }}
    >
      <h3 className="text-gray-400 text-lg">
        {title}
      </h3>

      <h1 className="text-4xl font-bold mt-3">
        {value}
      </h1>
    </div>
  );
}

export default AnalyticsCard;