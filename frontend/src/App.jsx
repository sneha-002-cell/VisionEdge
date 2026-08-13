import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import LiveCamera from "./pages/LiveCamera";
import Analytics from "./pages/Analytics";
import Intrusions from "./pages/Intrusions";
import Reports from "./pages/Reports";

import ProtectedRoute from "./components/ProtectedRoute";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

function AppLayout({ children, title }) {
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

function App() {

  return (
    <BrowserRouter>

      <Routes>

        {/* LOGIN */}

        <Route
          path="/"
          element={<Login />}
        />

        {/* DASHBOARD */}

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AppLayout title="Dashboard">
                <Dashboard />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        {/* LIVE CAMERA */}

        <Route
          path="/live-camera"
          element={
            <ProtectedRoute>
              <AppLayout title="Live Camera">
                <LiveCamera />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        {/* ANALYTICS */}

        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AppLayout title="Analytics">
                <Analytics />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        {/* INTRUSIONS */}

        <Route
          path="/intrusions"
          element={
            <ProtectedRoute>
              <AppLayout title="Intrusion Detection">
                <Intrusions />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        {/* REPORTS */}

        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <AppLayout title="Reports">
                <Reports />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        {/* FALLBACK */}

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