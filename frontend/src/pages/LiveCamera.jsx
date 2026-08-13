import {
  Video,
  Circle,
  Maximize,
  Activity,
} from "lucide-react";

import VideoPlayer from "../components/VideoPlayer";

function LiveCamera() {
  return (
    <div className="page-content">

      <div className="page-heading">

        <div>
          <div className="eyebrow">
            <Video size={14} />
            SURVEILLANCE
          </div>

          <h1>Live Camera</h1>

          <p>
            Real-time video stream with AI-powered object detection.
          </p>
        </div>

        <div className="heading-status">
          <Circle size={10} fill="currentColor" />
          CAMERA ONLINE
        </div>

      </div>

      <div className="camera-panel">

        <div className="camera-header">

          <div className="camera-title">
            <Activity size={18} />
            <span>CAMERA 01</span>
          </div>

          <div className="camera-actions">
            <span className="camera-live">
              <span className="status-dot" />
              LIVE
            </span>

            <button>
              <Maximize size={17} />
            </button>
          </div>

        </div>

        <div className="camera-feed">
          <VideoPlayer />
        </div>

        <div className="camera-footer">

          <div>
            <span>STREAM</span>
            <strong>ACTIVE</strong>
          </div>

          <div>
            <span>AI MODEL</span>
            <strong>YOLO</strong>
          </div>

          <div>
            <span>STATUS</span>
            <strong className="green-text">
              MONITORING
            </strong>
          </div>

        </div>

      </div>

    </div>
  );
}

export default LiveCamera;