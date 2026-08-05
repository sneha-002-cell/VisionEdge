function DownloadButtons() {
  const downloadCSV = () => {
    window.open("http://127.0.0.1:8000/export/csv", "_blank");
  };

  const downloadPDF = () => {
    window.open("http://127.0.0.1:8000/report", "_blank");
  };

  return (
    <div className="bg-slate-900 rounded-2xl p-6 shadow-xl mt-10">

      <h2 className="text-2xl font-bold text-white mb-6">
        📥 Download Reports
      </h2>

      <div className="flex gap-6">

        <button
          onClick={downloadCSV}
          className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-semibold transition"
        >
          📊 Download CSV
        </button>

        <button
          onClick={downloadPDF}
          className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-lg font-semibold transition"
        >
          📄 Download PDF
        </button>

      </div>

    </div>
  );
}

export default DownloadButtons;