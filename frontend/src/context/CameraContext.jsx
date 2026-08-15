import {
  createContext,
  useContext,
  useRef,
  useState,
} from "react";

import api from "../services/api";


// ============================================================
// CAMERA CONTEXT
// ============================================================

const CameraContext = createContext(null);


// ============================================================
// CAMERA PROVIDER
// ============================================================

export function CameraProvider({ children }) {

  const videoRef = useRef(null);

  const streamRef = useRef(null);

  const processingVideoRef = useRef(null);

  const canvasRef = useRef(null);

  const processingRef = useRef(false);

  const [cameraStatus, setCameraStatus] =
    useState("OFFLINE");

  const [error, setError] =
    useState("");


  // ==========================================================
  // START BACKEND PROCESSING
  // ==========================================================

  const startProcessing = async () => {

    if (processingRef.current) {
      return;
    }


    if (!streamRef.current) {
      return;
    }


    processingRef.current = true;


    // --------------------------------------------------------
    // Create hidden video element
    // --------------------------------------------------------

    const processingVideo =
      document.createElement("video");


    processingVideo.autoplay = true;

    processingVideo.playsInline = true;

    processingVideo.muted = true;

    processingVideo.srcObject =
      streamRef.current;


    processingVideoRef.current =
      processingVideo;


    try {

      await processingVideo.play();

    } catch (error) {

      console.warn(
        "Processing video play warning:",
        error
      );

    }


    // --------------------------------------------------------
    // Canvas
    // --------------------------------------------------------

    const canvas =
      document.createElement("canvas");


    canvas.width = 640;

    canvas.height = 360;


    canvasRef.current = canvas;


    const context =
      canvas.getContext("2d");


    // --------------------------------------------------------
    // Continuous frame processing
    // --------------------------------------------------------

    while (
      processingRef.current &&
      streamRef.current
    ) {

      try {

        if (
          processingVideo.readyState >= 2 &&
          processingVideo.videoWidth > 0 &&
          processingVideo.videoHeight > 0
        ) {

          context.drawImage(
            processingVideo,
            0,
            0,
            canvas.width,
            canvas.height
          );


          // --------------------------------------------------
          // Convert frame to JPEG
          // --------------------------------------------------

          const blob =
            await new Promise(
              (resolve) => {

                canvas.toBlob(
                  resolve,
                  "image/jpeg",
                  0.7
                );

              }
            );


          if (!blob) {
            continue;
          }


          // --------------------------------------------------
          // Send frame to FastAPI
          // --------------------------------------------------

          const formData =
            new FormData();


          formData.append(
            "file",
            blob,
            "camera.jpg"
          );


          await api.post(
            "/camera/frame",
            formData
          );

        }


      } catch (error) {

        console.error(
          "Camera frame processing error:",
          error
        );

      }


      // ------------------------------------------------------
      // Process approximately 4 frames per second
      // ------------------------------------------------------

      await new Promise(
        (resolve) =>
          setTimeout(
            resolve,
            250
          )
      );

    }


    processingVideo.srcObject = null;

    processingVideoRef.current = null;

    canvasRef.current = null;

  };


  // ==========================================================
  // STOP BACKEND PROCESSING
  // ==========================================================

  const stopProcessing = () => {

    processingRef.current = false;


    if (
      processingVideoRef.current
    ) {

      processingVideoRef.current.srcObject =
        null;

      processingVideoRef.current = null;

    }


    canvasRef.current = null;

  };


  // ==========================================================
  // START CAMERA
  // ==========================================================

  const startCamera = async () => {

    // --------------------------------------------------------
    // Already running
    // --------------------------------------------------------

    if (streamRef.current) {

      setCameraStatus("ONLINE");

      return streamRef.current;

    }


    setError("");

    setCameraStatus("STARTING");


    try {

      // ------------------------------------------------------
      // Browser camera support
      // ------------------------------------------------------

      if (
        !navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia
      ) {

        throw new Error(
          "Your browser does not support camera access."
        );

      }


      // ------------------------------------------------------
      // Request laptop webcam
      // ------------------------------------------------------

      const stream =
        await navigator.mediaDevices.getUserMedia({

          video: {

            width: {
              ideal: 1280,
            },

            height: {
              ideal: 720,
            },

            facingMode: "user",

          },

          audio: false,

        });


      // ------------------------------------------------------
      // Save stream
      // ------------------------------------------------------

      streamRef.current =
        stream;


      setCameraStatus("ONLINE");


      // ------------------------------------------------------
      // Attach to current video element
      // ------------------------------------------------------

      if (videoRef.current) {

        videoRef.current.srcObject =
          stream;


        await videoRef.current.play();

      }


      // ------------------------------------------------------
      // Start YOLO backend processing
      // ------------------------------------------------------

      startProcessing();


      return stream;


    } catch (err) {

      console.error(
        "Camera access error:",
        err
      );


      setCameraStatus("ERROR");


      if (
        err.name ===
        "NotAllowedError"
      ) {

        setError(
          "Camera permission was denied. Please allow camera access in your browser."
        );

      }

      else if (
        err.name ===
        "NotFoundError"
      ) {

        setError(
          "No camera was found on this device."
        );

      }

      else if (
        err.name ===
        "NotReadableError"
      ) {

        setError(
          "The camera is already being used by another application."
        );

      }

      else {

        setError(
          err.message ||
          "Unable to access the camera."
        );

      }


      return null;

    }

  };


  // ==========================================================
  // ATTACH CAMERA TO PAGE VIDEO
  // ==========================================================

  const attachVideo = async (
    element
  ) => {

    videoRef.current =
      element;


    if (
      element &&
      streamRef.current
    ) {

      element.srcObject =
        streamRef.current;


      try {

        await element.play();

      } catch (error) {

        console.warn(
          "Video autoplay warning:",
          error
        );

      }

    }

  };


  // ==========================================================
  // STOP CAMERA
  // ==========================================================

  const stopCamera = () => {

    stopProcessing();


    if (streamRef.current) {

      streamRef.current
        .getTracks()
        .forEach(
          (track) => {

            track.stop();

          }
        );


      streamRef.current =
        null;

    }


    if (videoRef.current) {

      videoRef.current.srcObject =
        null;

    }


    setCameraStatus("OFFLINE");

    setError("");

  };


  // ==========================================================
  // CAMERA STATUS
  // ==========================================================

  const handleTrackEnded = () => {

    stopProcessing();

    streamRef.current =
      null;

    setCameraStatus("OFFLINE");

  };


  // ==========================================================
  // PROVIDER
  // ==========================================================

  return (

    <CameraContext.Provider
      value={{

        videoRef,

        streamRef,

        cameraStatus,

        error,

        startCamera,

        stopCamera,

        attachVideo,

      }}
    >

      {children}

    </CameraContext.Provider>

  );

}


// ============================================================
// CAMERA HOOK
// ============================================================

export function useCamera() {

  const context =
    useContext(CameraContext);


  if (!context) {

    throw new Error(
      "useCamera must be used inside CameraProvider"
    );

  }


  return context;

}