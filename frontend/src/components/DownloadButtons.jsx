import {
  FileText,
  FileSpreadsheet,
  Download,
} from "lucide-react";

const API_URL = "https://visionedge-api.onrender.com";

function DownloadButtons() {
  const downloadCSV = () => {
    window.open(`${API_URL}/export/csv`, "_blank");
  };

  const downloadPDF = () => {
    window.open(`${API_URL}/report`, "_blank");
  };

  return (
    <div className="page-content">

      <div className="page-heading">
        <div>

          <div className="eyebrow">
            <FileText size={14} />
            DATA EXPORT
          </div>

          <h1>Reports</h1>

          <p>
            Download and archive VisionEdge analytics reports.
          </p>

        </div>
      </div>

      <div className="reports-grid">

        {/* CSV REPORT */}
        <div className="report-card">

          <div className="report-icon csv">
            <FileSpreadsheet size={28} />
          </div>

          <div className="report-content">

            <span className="report-type">
              DATA EXPORT
            </span>

            <h2>CSV Analytics Report</h2>

            <p>
              Export detection statistics and historical
              analytics as a CSV file.
            </p>

            <button
              className="report-button green-button"
              onClick={downloadCSV}
            >
              <Download size={17} />
              Download CSV
            </button>

          </div>
        </div>


        {/* PDF REPORT */}
        <div className="report-card">

          <div className="report-icon pdf">
            <FileText size={28} />
          </div>

          <div className="report-content">

            <span className="report-type">
              DOCUMENT
            </span>

            <h2>PDF Security Report</h2>

            <p>
              Generate a professional PDF report containing
              VisionEdge analytics and security information.
            </p>

            <button
              className="report-button red-button"
              onClick={downloadPDF}
            >
              <Download size={17} />
              Download PDF
            </button>

          </div>
        </div>

      </div>

    </div>
  );
}

export default DownloadButtons;