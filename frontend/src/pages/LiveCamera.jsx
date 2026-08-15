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
// RESTRICTED ZONE
//
// These coordinates MUST match RestrictedZone.py
//
// x1 = 50
// y1 = 300
// x2 = 300
// y2 = 470
//
// These coordinates are based on the 640px AI frame.
// ============================================================

const RESTRICTED_ZONE = {
  x1: 50,
  y1: 300,
  x2: 300,
  y2: 470,
};


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


  // ==========================================================
  // DETECTION STATE
  // ==========================================================

  const [detections, setDetections] = useState({
    people: 0,
    cars: 0,
    buses: 0,
    motorcycles: 0,
    fps: 0,
  });


  // ==========================================================
  // BOUNDING BOX STATE
  // ==========================================================

  const [boxes, setBoxes] = useState([]);


  // ==========================================================
  // INTRUSION STATE
  // ==========================================================

  const [intrusionDetected, setIntrusionDetected] =
    useState(false);


  // ==========================================================
  // ATTACH GLOBAL CAMERA STREAM
  // ==========================================================

  useEffect(() => {
    if (!videoRef.current) {
      return;
    }

    if (cameraStream) {
      videoRef.current.srcObject = cameraStream;

      videoRef.current.play().catch((err) => {
        console.warn(
          "Video autoplay warning:",
          err
        );
      });
    }

    return () => {
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    };
  }, [cameraStream]);


  // ==========================================================
  // SEND CAMERA FRAME TO BACKEND
  // ==========================================================

  const processCameraFrame = async () => {

    // Camera must be online
    if (cameraStatus !== "ONLINE") {
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


    const video = videoRef.current;


    // Camera needs actual dimensions
    if (
      video.videoWidth === 0 ||
      video.videoHeight === 0
    ) {
      return;
    }


    const canvas = canvasRef.current;

    if (!canvas) {
      return;
    }


    processingRef.current = true;
    setAiStatus("PROCESSING");


    try {

      // ======================================================
      // RESIZE FRAME FOR AI
      // ======================================================

      const targetWidth = 640;

      const scale =
        targetWidth / video.videoWidth;

      const targetHeight =
        Math.round(
          video.videoHeight * scale
        );


      canvas.width = targetWidth;
      canvas.height = targetHeight;


      const context =
        canvas.getContext("2d");


      if (!context) {
        throw new Error(
          "Could not create canvas context."
        );
      }


      // ======================================================
      // CAPTURE CURRENT FRAME
      // ======================================================

      context.drawImage(
        video,
        0,
        0,
        targetWidth,
        targetHeight
      );


      // ======================================================
      // CONVERT FRAME TO JPEG
      // ======================================================

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


      // ======================================================
      // CREATE MULTIPART FORM
      // ======================================================

      const formData = new FormData();

      formData.append(
        "file",
        blob,
        "camera.jpg"
      );


      // ======================================================
      // SEND FRAME TO FASTAPI
      // ======================================================

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


      // ======================================================
      // UPDATE COUNTS
      // ======================================================

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


      // ======================================================
      // UPDATE BOUNDING BOXES
      // ======================================================

      const backendDetections =
        Array.isArray(data.detections)
          ? data.detections
          : [];


      setBoxes(
        backendDetections
      );


      // ======================================================
      // UPDATE INTRUSION STATUS
      // ======================================================

      const hasIntrusion =
        Boolean(data.intrusion) ||
        backendDetections.some(
          (detection) =>
            detection.intrusion === true
        );


      setIntrusionDetected(
        hasIntrusion
      );


      // ======================================================
      // AI ONLINE
      // ======================================================

      setAiStatus("ONLINE");
      setError("");


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

      processingRef.current = false;

    }

  };


  // ==========================================================
  // START AI PROCESSING
  // ==========================================================

  useEffect(() => {

    if (cameraStatus !== "ONLINE") {

      if (intervalRef.current) {

        clearInterval(
          intervalRef.current
        );

        intervalRef.current = null;

      }

      processingRef.current = false;

      setAiStatus("WAITING");

      setBoxes([]);

      setIntrusionDetected(false);

      return;

    }


    // Process immediately

    processCameraFrame();


    // Process approximately every 500ms

    intervalRef.current =
      setInterval(
        processCameraFrame,
        500
      );


    // Cleanup

    return () => {

      if (intervalRef.current) {

        clearInterval(
          intervalRef.current
        );

        intervalRef.current = null;

      }

      processingRef.current = false;

    };

  }, [cameraStatus]);


  // ==========================================================
  // START CAMERA
  // ==========================================================

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


  // ==========================================================
  // STOP CAMERA
  // ==========================================================

  const handleStopCamera =
    () => {

      if (intervalRef.current) {

        clearInterval(
          intervalRef.current
        );

        intervalRef.current = null;

      }

      processingRef.current = false;

      setAiStatus("WAITING");


      setDetections({

        people: 0,
        cars: 0,
        buses: 0,
        motorcycles: 0,
        fps: 0,

      });


      setBoxes([]);

      setIntrusionDetected(false);


      stopCamera();

      setError("");

    };


  // ==========================================================
  // FULLSCREEN
  // ==========================================================

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


  // ==========================================================
  // STATUS TEXT
  // ==========================================================

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


  // ==========================================================
  // AI STATUS TEXT
  // ==========================================================

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


  // ==========================================================
  // CALCULATE OBJECT BOX POSITION
  //
  // Backend coordinates are based on the 640px AI frame.
  // ==========================================================

  const getBoxStyle =
    (box) => {

      if (!videoRef.current) {
        return {};
      }


      const video =
        videoRef.current;


      const sourceWidth =
        640;


      const sourceHeight =
        Math.round(
          640 *
          (
            video.videoHeight /
            video.videoWidth
          )
        );


      const displayWidth =
        video.clientWidth;


      const displayHeight =
        video.clientHeight;


      if (
        sourceWidth <= 0 ||
        sourceHeight <= 0 ||
        displayWidth <= 0 ||
        displayHeight <= 0
      ) {

        return {};

      }


      // Match object-fit: cover

      const scale =
        Math.max(
          displayWidth /
            sourceWidth,

          displayHeight /
            sourceHeight
        );


      const renderedWidth =
        sourceWidth * scale;


      const renderedHeight =
        sourceHeight * scale;


      const offsetX =
        (
          displayWidth -
          renderedWidth
        ) / 2;


      const offsetY =
        (
          displayHeight -
          renderedHeight
        ) / 2;


      const left =
        offsetX +
        Number(box.x1) * scale;


      const top =
        offsetY +
        Number(box.y1) * scale;


      const width =
        (
          Number(box.x2) -
          Number(box.x1)
        ) * scale;


      const height =
        (
          Number(box.y2) -
          Number(box.y1)
        ) * scale;


      const isIntrusion =
        box.intrusion === true;


      return {

        position:
          "absolute",

        left:
          `${left}px`,

        top:
          `${top}px`,

        width:
          `${width}px`,

        height:
          `${height}px`,

        border:
          isIntrusion
            ? "3px solid #ef4444"
            : "3px solid #22c55e",

        boxSizing:
          "border-box",

        pointerEvents:
          "none",

        zIndex:
          8,

        borderRadius:
          "4px",

        boxShadow:
          isIntrusion
            ? "0 0 12px rgba(239,68,68,0.75)"
            : "0 0 8px rgba(34,197,94,0.45)",

      };

    };


  // ==========================================================
  // FIXED RESTRICTED ZONE STYLE
  //
  // IMPORTANT:
  // This is completely independent from detection boxes.
  //
  // It NEVER uses box.x1 / box.y1.
  // Therefore it cannot follow the person.
  // ==========================================================

  const getRestrictedZoneStyle =
    () => {

      if (!videoRef.current) {
        return {};
      }


      const video =
        videoRef.current;


      const sourceWidth =
        640;


      const sourceHeight =
        Math.round(
          640 *
          (
            video.videoHeight /
            video.videoWidth
          )
        );


      const displayWidth =
        video.clientWidth;


      const displayHeight =
        video.clientHeight;


      if (
        sourceWidth <= 0 ||
        sourceHeight <= 0 ||
        displayWidth <= 0 ||
        displayHeight <= 0
      ) {

        return {};

      }


      // ------------------------------------------------------
      // Match object-fit: cover
      // ------------------------------------------------------

      const scale =
        Math.max(
          displayWidth /
            sourceWidth,

          displayHeight /
            sourceHeight
        );


      const renderedWidth =
        sourceWidth * scale;


      const renderedHeight =
        sourceHeight * scale;


      const offsetX =
        (
          displayWidth -
          renderedWidth
        ) / 2;


      const offsetY =
        (
          displayHeight -
          renderedHeight
        ) / 2;


      const left =
        offsetX +
        RESTRICTED_ZONE.x1 *
          scale;


      const top =
        offsetY +
        RESTRICTED_ZONE.y1 *
          scale;


      const width =
        (
          RESTRICTED_ZONE.x2 -
          RESTRICTED_ZONE.x1
        ) * scale;


      const height =
        (
          RESTRICTED_ZONE.y2 -
          RESTRICTED_ZONE.y1
        ) * scale;


      return {

        position:
          "absolute",

        left:
          `${left}px`,

        top:
          `${top}px`,

        width:
          `${width}px`,

        height:
          `${height}px`,

        border:
          "3px solid #ef4444",

        boxSizing:
          "border-box",

        pointerEvents:
          "none",

        zIndex:
          6,

        borderRadius:
          "4px",

        background:
          "rgba(239, 68, 68, 0.06)",

        boxShadow:
          "0 0 10px rgba(239, 68, 68, 0.35)",

      };

    };


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="page-content">


      {/* =====================================================
          PAGE HEADING
      ====================================================== */}

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


      {/* =====================================================
          CAMERA PANEL
      ====================================================== */}

      <div className="camera-panel">


        {/* ===================================================
            CAMERA HEADER
        ==================================================== */}

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


        {/* ===================================================
            CAMERA FEED
        ==================================================== */}

        <div
          className="camera-feed"
          style={{
            position: "relative",
            overflow: "hidden",
            background: "#000",
          }}
        >


          {/* =================================================
              VIDEO
          ================================================== */}

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


          {/* =================================================
              FIXED RESTRICTED AREA
              
              THIS BOX STAYS IN ONE PLACE.
              IT DOES NOT COME FROM YOLO DETECTIONS.
              IT DOES NOT MOVE WITH THE PERSON.
          ================================================== */}

          {cameraStatus ===
            "ONLINE" && (

            <div
              style={
                getRestrictedZoneStyle()
              }
            >

              <div
                style={{
                  position:
                    "absolute",

                  left:
                    "-3px",

                  top:
                    "-30px",

                  padding:
                    "5px 9px",

                  background:
                    "#ef4444",

                  color:
                    "#fff",

                  fontSize:
                    "11px",

                  fontWeight:
                    800,

                  borderRadius:
                    "4px",

                  whiteSpace:
                    "nowrap",

                  letterSpacing:
                    "0.3px",

                  boxShadow:
                    "0 2px 7px rgba(0,0,0,0.4)",

                }}
              >

                RESTRICTED AREA

              </div>

            </div>

          )}


          {/* =================================================
              MOVING DETECTION BOXES
              
              These boxes DO move with detected objects.
          ================================================== */}

          {cameraStatus ===
            "ONLINE" &&
            boxes.map(
              (box, index) => {

                const isIntrusion =
                  box.intrusion === true;


                return (

                  <div
                    key={
                      `${box.track_id ?? "box"}-${index}`
                    }
                    style={
                      getBoxStyle(box)
                    }
                  >

                    {/* ---------------------------------------
                        DETECTION LABEL
                    ---------------------------------------- */}

                    <div
                      style={{
                        position:
                          "absolute",

                        left:
                          "-3px",

                        top:
                          "-28px",

                        padding:
                          "4px 8px",

                        background:
                          isIntrusion
                            ? "#ef4444"
                            : "#22c55e",

                        color:
                          "#fff",

                        fontSize:
                          "11px",

                        fontWeight:
                          700,

                        borderRadius:
                          "4px",

                        whiteSpace:
                          "nowrap",

                        boxShadow:
                          "0 2px 6px rgba(0,0,0,0.35)",

                      }}
                    >

                      {String(
                        box.class ||
                        "OBJECT"
                      ).toUpperCase()}

                      {" "}

                      {Math.round(
                        Number(
                          box.confidence
                        ) * 100
                      )}

                      %

                    </div>


                    {/* ---------------------------------------
                        INTRUSION LABEL
                    ---------------------------------------- */}

                    {isIntrusion && (

                      <div
                        style={{
                          position:
                            "absolute",

                          left:
                            "-3px",

                          bottom:
                            "-28px",

                          padding:
                            "4px 8px",

                          background:
                            "#991b1b",

                          color:
                            "#fff",

                          fontSize:
                            "11px",

                          fontWeight:
                            800,

                          borderRadius:
                            "4px",

                          whiteSpace:
                            "nowrap",

                          boxShadow:
                            "0 2px 8px rgba(239,68,68,0.6)",

                        }}
                      >

                        🚨 INTRUSION

                      </div>

                    )}

                  </div>

                );

              }
            )}


          {/* =================================================
              HIDDEN CANVAS
          ================================================== */}

          <canvas
            ref={canvasRef}
            style={{
              display: "none",
            }}
          />


          {/* =================================================
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


          {/* =================================================
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
                zIndex: 10,
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


          {/* =================================================
              INTRUSION ALERT OVERLAY
          ================================================== */}

          {cameraStatus ===
            "ONLINE" &&
            intrusionDetected && (

            <div
              style={{
                position:
                  "absolute",

                top:
                  "15px",

                left:
                  "50%",

                transform:
                  "translateX(-50%)",

                padding:
                  "9px 16px",

                borderRadius:
                  "8px",

                background:
                  "rgba(153, 27, 27, 0.94)",

                color:
                  "#fff",

                fontSize:
                  "13px",

                fontWeight:
                  800,

                letterSpacing:
                  "0.5px",

                display:
                  "flex",

                alignItems:
                  "center",

                gap:
                  "8px",

                zIndex:
                  15,

                boxShadow:
                  "0 0 18px rgba(239,68,68,0.55)",

              }}
            >

              🚨 INTRUSION DETECTED

            </div>

          )}


          {/* =================================================
              DETECTION INFORMATION
          ================================================== */}

          {cameraStatus ===
            "ONLINE" && (

            <div
              style={{
                position:
                  "absolute",

                top:
                  "15px",

                right:
                  "15px",

                padding:
                  "12px 14px",

                borderRadius:
                  "10px",

                background:
                  "rgba(0, 0, 0, 0.72)",

                color:
                  "#fff",

                fontSize:
                  "12px",

                lineHeight:
                  "1.7",

                minWidth:
                  "150px",

                zIndex:
                  10,

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


              <div
                style={{
                  marginTop:
                    "5px",

                  paddingTop:
                    "5px",

                  borderTop:
                    "1px solid rgba(255,255,255,0.15)",

                  color:
                    intrusionDetected
                      ? "#f87171"
                      : "#4ade80",

                  fontWeight:
                    700,

                }}
              >

                SECURITY:{" "}

                {intrusionDetected
                  ? "INTRUSION"
                  : "CLEAR"}

              </div>

            </div>

          )}


          {/* =================================================
              ERROR MESSAGE
          ================================================== */}

          {error && (

            <div
              style={{
                position:
                  "absolute",

                left:
                  "20px",

                right:
                  "20px",

                bottom:
                  "20px",

                padding:
                  "12px 16px",

                borderRadius:
                  "8px",

                background:
                  "rgba(127, 29, 29, 0.92)",

                color:
                  "#fff",

                display:
                  "flex",

                alignItems:
                  "center",

                gap:
                  "10px",

                zIndex:
                  20,

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


        {/* ===================================================
            CAMERA CONTROLS
        ==================================================== */}

        <div
          style={{
            display:
              "flex",

            gap:
              "10px",

            padding:
              "14px 18px",

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
              display:
                "flex",

              alignItems:
                "center",

              gap:
                "8px",

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
              display:
                "flex",

              alignItems:
                "center",

              gap:
                "8px",

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


        {/* ===================================================
            CAMERA FOOTER
        ==================================================== */}

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