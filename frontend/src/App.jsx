import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import {
  useEffect,
  useRef,
  useState,
} from "react";


import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import LiveCamera from "./pages/LiveCamera";
import Analytics from "./pages/Analytics";
import Intrusions from "./pages/Intrusions";
import Reports from "./pages/Reports";


import ProtectedRoute from "./components/ProtectedRoute";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";



/* ============================================================
   APP LAYOUT
============================================================ */

function AppLayout({
  children,
  title,
  cameraStream,
  cameraStatus,
  startCamera,
  stopCamera,
}) {

  return (

    <div className="app-shell">

      <Sidebar />

      <main className="main-area">

        <Topbar title={title} />

        {children}

      </main>

    </div>

  );

}



/* ============================================================
   APP
============================================================ */

function App() {

  /*
   * IMPORTANT
   *
   * The camera stream lives here instead of inside
   * LiveCamera.jsx.
   *
   * Therefore navigating between pages does NOT destroy
   * the webcam stream.
   */

  const cameraStreamRef = useRef(null);

  const [cameraStatus, setCameraStatus] =
    useState("OFFLINE");



  /* ==========================================================
     START CAMERA
  ========================================================== */

  const startCamera = async () => {

    /*
     * If camera is already running,
     * don't request another stream.
     */

    if (cameraStreamRef.current) {

      setCameraStatus("ONLINE");

      return cameraStreamRef.current;

    }


    setCameraStatus("STARTING");


    try {

      /*
       * Browser camera support check
       */

      if (
        !navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia
      ) {

        throw new Error(
          "Your browser does not support camera access."
        );

      }


      /*
       * Request laptop webcam
       */

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


      /*
       * Store globally in App
       */

      cameraStreamRef.current = stream;


      /*
       * Listen for camera being disconnected
       */

      stream.getVideoTracks().forEach(
        (track) => {

          track.onended = () => {

            cameraStreamRef.current = null;

            setCameraStatus("OFFLINE");

          };

        }
      );


      setCameraStatus("ONLINE");


      return stream;


    } catch (error) {

      console.error(
        "VisionEdge camera error:",
        error
      );


      cameraStreamRef.current = null;

      setCameraStatus("ERROR");


      throw error;

    }

  };



  /* ==========================================================
     STOP CAMERA
  ========================================================== */

  const stopCamera = () => {

    const stream =
      cameraStreamRef.current;


    if (stream) {

      stream
        .getTracks()
        .forEach(
          (track) => {

            track.stop();

          }
        );

    }


    cameraStreamRef.current = null;

    setCameraStatus("OFFLINE");

  };



  /* ==========================================================
     GLOBAL CAMERA CLEANUP
  ========================================================== */

  useEffect(() => {

    /*
     * This runs only when the ENTIRE application is closed/
     * unmounted.
     *
     * It does NOT run when navigating between pages.
     */

    return () => {

      const stream =
        cameraStreamRef.current;


      if (stream) {

        stream
          .getTracks()
          .forEach(
            (track) => {

              track.stop();

            }
          );

      }

    };

  }, []);



  /* ==========================================================
     ROUTES
  ========================================================== */

  return (

    <BrowserRouter>

      <Routes>


        {/* ==================================================
            LOGIN
        ================================================== */}

        <Route
          path="/"
          element={
            <Login />
          }
        />



        {/* ==================================================
            DASHBOARD
        ================================================== */}

        <Route
          path="/dashboard"
          element={

            <ProtectedRoute>

              <AppLayout
                title="Dashboard"
                cameraStream={
                  cameraStreamRef.current
                }
                cameraStatus={
                  cameraStatus
                }
                startCamera={
                  startCamera
                }
                stopCamera={
                  stopCamera
                }
              >

                <Dashboard />

              </AppLayout>

            </ProtectedRoute>

          }
        />



        {/* ==================================================
            LIVE CAMERA
        ================================================== */}

        <Route
          path="/live-camera"
          element={

            <ProtectedRoute>

              <AppLayout
                title="Live Camera"
                cameraStream={
                  cameraStreamRef.current
                }
                cameraStatus={
                  cameraStatus
                }
                startCamera={
                  startCamera
                }
                stopCamera={
                  stopCamera
                }
              >

                <LiveCamera
                  cameraStream={
                    cameraStreamRef.current
                  }

                  cameraStatus={
                    cameraStatus
                  }

                  startCamera={
                    startCamera
                  }

                  stopCamera={
                    stopCamera
                  }
                />

              </AppLayout>

            </ProtectedRoute>

          }
        />



        {/* ==================================================
            ANALYTICS
        ================================================== */}

        <Route
          path="/analytics"
          element={

            <ProtectedRoute>

              <AppLayout
                title="Analytics"
                cameraStream={
                  cameraStreamRef.current
                }
                cameraStatus={
                  cameraStatus
                }
                startCamera={
                  startCamera
                }
                stopCamera={
                  stopCamera
                }
              >

                <Analytics />

              </AppLayout>

            </ProtectedRoute>

          }
        />



        {/* ==================================================
            INTRUSIONS
        ================================================== */}

        <Route
          path="/intrusions"
          element={

            <ProtectedRoute>

              <AppLayout
                title="Intrusion Detection"
                cameraStream={
                  cameraStreamRef.current
                }
                cameraStatus={
                  cameraStatus
                }
                startCamera={
                  startCamera
                }
                stopCamera={
                  stopCamera
                }
              >

                <Intrusions />

              </AppLayout>

            </ProtectedRoute>

          }
        />



        {/* ==================================================
            REPORTS
        ================================================== */}

        <Route
          path="/reports"
          element={

            <ProtectedRoute>

              <AppLayout
                title="Reports"
                cameraStream={
                  cameraStreamRef.current
                }
                cameraStatus={
                  cameraStatus
                }
                startCamera={
                  startCamera
                }
                stopCamera={
                  stopCamera
                }
              >

                <Reports />

              </AppLayout>

            </ProtectedRoute>

          }
        />



        {/* ==================================================
            FALLBACK
        ================================================== */}

        <Route
          path="*"
          element={

            <Navigate
              to="/dashboard"
              replace
            />

          }
        />


      </Routes>

    </BrowserRouter>

  );

}


export default App;