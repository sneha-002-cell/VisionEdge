import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Video,
  Circle,
  Maximize,
  Activity,
  Camera,
  CameraOff,
  AlertCircle,
} from "lucide-react";


// ============================================================
// API URL
// ============================================================

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


// ============================================================
// LIVE CAMERA
// ============================================================

function LiveCamera({
  cameraStream,
  cameraStatus,
  startCamera,
  stopCamera,
}) {

  const videoRef = useRef(null);

  const canvasRef = useRef(null);

  const processingRef = useRef(false);

  const intervalRef = useRef(null);

  const [error, setError] = useState("");

  const [aiStatus, setAiStatus] = useState("WAITING");

  const [detections, setDetections] = useState({
    people: 0,
    cars: 0,
    buses: 0,
    motorcycles: 0,
    fps: 0,
  });


  // ============================================================
  // ATTACH GLOBAL CAMERA STREAM
  // ============================================================

  useEffect(() => {

    if (!videoRef.current) {
      return;
    }

    if (cameraStream) {

      videoRef.current.srcObject =
        cameraStream;

      videoRef.current
        .play()
        .catch((err) => {

          console.warn(
            "Video autoplay warning:",
            err
          );

        });

    }

    return () => {

      if (videoRef.current) {

        videoRef.current.srcObject =
          null;

      }

    };

  }, [cameraStream]);


  // ============================================================
  // SEND CAMERA FRAME TO BACKEND
  // ============================================================

  const processCameraFrame = async () => {

    // Camera must be online
    if (
      cameraStatus !== "ONLINE"
    ) {
      return;
    }


    // Video element must exist
    if (!videoRef.current) {
      return;
    }


    // Avoid overlapping requests
    if (processingRef.current) {
      return;
    }


    const video =
      videoRef.current;


    // Camera needs actual dimensions
    if (
      video.videoWidth === 0 ||
      video.videoHeight === 0
    ) {
      return;
    }


    const canvas =
      canvasRef.current;


    if (!canvas) {
      return;
    }


    processingRef.current = true;

    setAiStatus("PROCESSING");


    try {

      // --------------------------------------------------------
      // Use a smaller frame for faster AI processing
      // --------------------------------------------------------

      const targetWidth = 640;

      const scale =
        targetWidth /
        video.videoWidth;

      const targetHeight =
        Math.round(
          video.videoHeight * scale
        );


      canvas.width =
        targetWidth;

      canvas.height =
        targetHeight;


      const context =
        canvas.getContext("2d");


      if (!context) {
        return;
      }


      // --------------------------------------------------------
      // Capture current webcam frame
      // --------------------------------------------------------

      context.drawImage(
        video,
        0,
        0,
        targetWidth,
        targetHeight
      );


      // --------------------------------------------------------
      // Convert frame to JPEG
      // --------------------------------------------------------

      const blob =
        await new Promise(
          (resolve) => {

            canvas.toBlob(
              resolve,
              "image/jpeg",
              0.75
            );

          }
        );


      if (!blob) {
        throw new Error(
          "Could not create camera frame."
        );
      }


      // --------------------------------------------------------
      // Create multipart form
      // --------------------------------------------------------

      const formData =
        new FormData();

      formData.append(
        "file",
        blob,
        "camera.jpg"
      );


      // --------------------------------------------------------
      // Send frame to FastAPI
      // --------------------------------------------------------

      const response =
        await fetch(
          `${API_URL}/camera/frame`,
          {
            method: "POST",
            body: formData,
          }
        );


      if (!response.ok) {

        const message =
          await response.text();

        throw new Error(
          `AI server error ${response.status}: ${message}`
        );

      }


      const data =
        await response.json();


      // --------------------------------------------------------
      // Update detection information
      // --------------------------------------------------------

      setDetections({
        people:
          Number(data.people) || 0,

        cars:
          Number(data.cars) || 0,

        buses:
          Number(data.buses) || 0,

        motorcycles:
          Number(data.motorcycles) || 0,

        fps:
          Number(data.fps) || 0,
      });


      setAiStatus("ONLINE");

    } catch (err) {

      console.error(
        "Camera AI processing error:",
        err
      );

      setAiStatus("ERROR");

      setError(
        err.message ||
        "Unable to send camera frame to VisionEdge AI."
      );

    } finally {

      processingRef.current =
        false;

    }

  };


  // ============================================================
  // START AI PROCESSING
  // ============================================================

  useEffect(() => {

    // ----------------------------------------------------------
    // Stop processing if camera isn't online
    // ----------------------------------------------------------

    if (
      cameraStatus !== "ONLINE"
    ) {

      if (intervalRef.current) {

        clearInterval(
          intervalRef.current
        );

        intervalRef.current =
          null;

      }

      processingRef.current =
        false;

      setAiStatus("WAITING");

      return;

    }


    // ----------------------------------------------------------
    // Start processing
    //
    // One frame approximately every 500ms.
    // This prevents sending too many requests.
    // ----------------------------------------------------------

    processCameraFrame();

    intervalRef.current =
      setInterval(
        processCameraFrame,
        500
      );


    // ----------------------------------------------------------
    // Cleanup
    // ----------------------------------------------------------

    return () => {

      if (intervalRef.current) {

        clearInterval(
          intervalRef.current
        );

        intervalRef.current =
          null;

      }

      processingRef.current =
        false;

    };

  }, [cameraStatus]);


  // ============================================================
  // START CAMERA
  // ============================================================

  const handleStartCamera =
    async () => {

      setError("");

      try {

        await startCamera();

      } catch (err) {

        console.error(
          "Camera access error:",
          err
        );


        if (
          err.name ===
          "NotAllowedError"
        ) {

          setError(
            "Camera permission was denied. Please allow camera access in your browser."
          );

        } else if (
          err.name ===
          "NotFoundError"
        ) {

          setError(
            "No camera was found on this device."
          );

        } else if (
          err.name ===
          "NotReadableError"
        ) {

          setError(
            "The camera is already being used by another application."
          );

        } else {

          setError(
            err.message ||
            "Unable to access the camera."
          );

        }

      }

    };


  // ============================================================
  // STOP CAMERA
  // ============================================================

  const handleStopCamera =
    () => {

      if (intervalRef.current) {

        clearInterval(
          intervalRef.current
        );

        intervalRef.current =
          null;

      }

      processingRef.current =
        false;

      setAiStatus("WAITING");

      setDetections({
        people: 0,
        cars: 0,
        buses: 0,
        motorcycles: 0,
        fps: 0,
      });

      stopCamera();

      setError("");

    };


  // ============================================================
  // FULLSCREEN
  // ============================================================

  const handleFullscreen =
    () => {

      if (!videoRef.current) {
        return;
      }


      if (
        document.fullscreenElement
      ) {

        document.exitFullscreen();

      } else {

        videoRef.current
          .requestFullscreen()
          .catch((err) => {

            console.error(
              "Fullscreen error:",
              err
            );

          });

      }

    };


  // ============================================================
  // STATUS TEXT
  // ============================================================

  const getStatusText =
    () => {

      if (
        cameraStatus ===
        "ONLINE"
      ) {

        return "CAMERA ONLINE";

      }


      if (
        cameraStatus ===
        "STARTING"
      ) {

        return "STARTING CAMERA";

      }


      if (
        cameraStatus ===
        "ERROR"
      ) {

        return "CAMERA ERROR";

      }


      return "CAMERA OFFLINE";

    };


  // ============================================================
  // AI STATUS TEXT
  // ============================================================

  const getAIStatusText =
    () => {

      if (
        aiStatus ===
        "PROCESSING"
      ) {

        return "AI PROCESSING";

      }

      if (
        aiStatus ===
        "ONLINE"
      ) {

        return "AI ONLINE";

      }

      if (
        aiStatus ===
        "ERROR"
      ) {

        return "AI ERROR";

      }

      return "AI WAITING";

    };


  // ============================================================
  // RENDER
  // ============================================================

  return (

    <div className="page-content">


      {/* ======================================================
          PAGE HEADING
      ======================================================= */}

      <div className="page-heading">

        <div>

          <div className="eyebrow">

            <Video size={14} />

            SURVEILLANCE

          </div>


          <h1>
            Live Camera
          </h1>


          <p>
            Real-time laptop camera feed
            with VisionEdge AI detection.
          </p>

        </div>


        {/* CAMERA STATUS */}

        <div
          className="heading-status"
          style={{
            color:
              cameraStatus ===
              "ONLINE"
                ? "#22c55e"
                : cameraStatus ===
                  "ERROR"
                  ? "#ef4444"
                  : undefined,
          }}
        >

          <Circle
            size={10}
            fill="currentColor"
          />

          {getStatusText()}

        </div>

      </div>


      {/* ======================================================
          CAMERA PANEL
      ======================================================= */}

      <div className="camera-panel">


        {/* CAMERA HEADER */}

        <div className="camera-header">

          <div className="camera-title">

            <Activity
              size={18}
            />

            <span>
              LAPTOP CAMERA
            </span>

          </div>


          <div className="camera-actions">

            <span
              className="camera-live"
            >

              <span
                className="status-dot"
                style={{
                  background:
                    cameraStatus ===
                    "ONLINE"
                      ? "#22c55e"
                      : "#6b7280",
                }}
              />

              {cameraStatus ===
              "ONLINE"
                ? "LIVE"
                : "OFFLINE"}

            </span>


            <button
              type="button"
              onClick={
                handleFullscreen
              }
              title="Fullscreen"
            >

              <Maximize
                size={17}
              />

            </button>

          </div>

        </div>


        {/* ====================================================
            CAMERA FEED
        ===================================================== */}

        <div
          className="camera-feed"
          style={{
            position: "relative",
            overflow: "hidden",
            background: "#000",
          }}
        >

          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted

            style={{
              width: "100%",
              height: "100%",
              minHeight: "400px",
              objectFit: "cover",
              display:
                cameraStatus ===
                "ONLINE"
                  ? "block"
                  : "none",
              background: "#000",
            }}
          />


          {/* Hidden canvas used for AI frame capture */}

          <canvas
            ref={canvasRef}
            style={{
              display: "none",
            }}
          />


          {/* ==================================================
              OFFLINE PLACEHOLDER
          ================================================== */}

          {cameraStatus !==
            "ONLINE" && (

            <div
              style={{
                width: "100%",
                minHeight: "400px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexDirection: "column",
                gap: "14px",
                textAlign: "center",
              }}
            >

              {cameraStatus ===
                "ERROR" ? (

                <AlertCircle
                  size={42}
                />

              ) : (

                <Camera
                  size={42}
                />

              )}


              <strong>

                {cameraStatus ===
                "STARTING"

                  ? "Starting camera..."

                  : cameraStatus ===
                    "ERROR"

                    ? "Camera unavailable"

                    : "Camera is offline"}

              </strong>


              <span>

                {cameraStatus ===
                "STARTING"

                  ? "Please wait..."

                  : cameraStatus ===
                    "ERROR"

                    ? "Check your browser camera permission."

                    : "Click START CAMERA to access your laptop webcam."}

              </span>

            </div>

          )}


          {/* ==================================================
              AI STATUS OVERLAY
          ================================================== */}

          {cameraStatus ===
            "ONLINE" && (

            <div
              style={{
                position: "absolute",
                top: "15px",
                left: "15px",
                padding: "8px 12px",
                borderRadius: "8px",
                background:
                  "rgba(0, 0, 0, 0.72)",
                color: "#fff",
                fontSize: "12px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: "8px",
                zIndex: 5,
              }}
            >

              <span
                className="status-dot"
                style={{
                  background:
                    aiStatus ===
                    "ONLINE"
                      ? "#22c55e"
                      : aiStatus ===
                        "ERROR"
                        ? "#ef4444"
                        : "#f59e0b",
                }}
              />

              {getAIStatusText()}

            </div>

          )}


          {/* ==================================================
              DETECTION OVERLAY
          ================================================== */}

          {cameraStatus ===
            "ONLINE" && (

            <div
              style={{
                position: "absolute",
                top: "15px",
                right: "15px",
                padding: "12px 14px",
                borderRadius: "10px",
                background:
                  "rgba(0, 0, 0, 0.72)",
                color: "#fff",
                fontSize: "12px",
                lineHeight: "1.7",
                minWidth: "150px",
                zIndex: 5,
              }}
            >

              <div>
                PEOPLE:{" "}
                <strong>
                  {detections.people}
                </strong>
              </div>

              <div>
                CARS:{" "}
                <strong>
                  {detections.cars}
                </strong>
              </div>

              <div>
                BUSES:{" "}
                <strong>
                  {detections.buses}
                </strong>
              </div>

              <div>
                MOTORCYCLES:{" "}
                <strong>
                  {detections.motorcycles}
                </strong>
              </div>

              <div>
                AI FPS:{" "}
                <strong>
                  {detections.fps.toFixed
                    ? detections.fps.toFixed(1)
                    : detections.fps}
                </strong>
              </div>

            </div>

          )}


          {/* ==================================================
              ERROR MESSAGE
          ================================================== */}

          {error && (

            <div
              style={{
                position: "absolute",
                left: "20px",
                right: "20px",
                bottom: "20px",
                padding: "12px 16px",
                borderRadius: "8px",
                background:
                  "rgba(127, 29, 29, 0.92)",
                color: "#fff",
                display: "flex",
                alignItems: "center",
                gap: "10px",
                zIndex: 10,
              }}
            >

              <AlertCircle
                size={18}
              />

              <span>
                {error}
              </span>

            </div>

          )}

        </div>


        {/* ====================================================
            CAMERA CONTROLS
        ===================================================== */}

        <div
          style={{
            display: "flex",
            gap: "10px",
            padding: "14px 18px",
            borderTop:
              "1px solid rgba(255,255,255,0.08)",
          }}
        >

          <button
            type="button"
            onClick={
              handleStartCamera
            }
            disabled={
              cameraStatus ===
                "ONLINE" ||
              cameraStatus ===
                "STARTING"
            }
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              cursor:
                cameraStatus ===
                  "ONLINE" ||
                cameraStatus ===
                  "STARTING"
                  ? "not-allowed"
                  : "pointer",
              opacity:
                cameraStatus ===
                  "ONLINE" ||
                cameraStatus ===
                  "STARTING"
                  ? 0.5
                  : 1,
            }}
          >

            <Camera
              size={17}
            />

            START CAMERA

          </button>


          <button
            type="button"
            onClick={
              handleStopCamera
            }
            disabled={
              cameraStatus !==
              "ONLINE"
            }
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              cursor:
                cameraStatus !==
                  "ONLINE"
                  ? "not-allowed"
                  : "pointer",
              opacity:
                cameraStatus !==
                  "ONLINE"
                  ? 0.5
                  : 1,
            }}
          >

            <CameraOff
              size={17}
            />

            STOP CAMERA

          </button>

        </div>


        {/* ====================================================
            CAMERA FOOTER
        ===================================================== */}

        <div
          className="camera-footer"
        >

          <div>

            <span>
              STREAM
            </span>

            <strong>

              {cameraStatus ===
              "ONLINE"
                ? "ACTIVE"
                : "INACTIVE"}

            </strong>

          </div>


          <div>

            <span>
              SOURCE
            </span>

            <strong>
              LAPTOP WEBCAM
            </strong>

          </div>


          <div>

            <span>
              AI MODEL
            </span>

            <strong>
              YOLO11n
            </strong>

          </div>


          <div>

            <span>
              AI STATUS
            </span>

            <strong
              className={
                aiStatus ===
                "ONLINE"
                  ? "green-text"
                  : ""
              }
            >

              {getAIStatusText()}

            </strong>

          </div>

        </div>

      </div>

    </div>

  );

}


export default LiveCamera;