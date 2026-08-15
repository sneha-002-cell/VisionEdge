# VisionEdge

## AI-Powered Real-Time Video Analytics & Intelligent Surveillance System

VisionEdge is an AI-powered video surveillance and analytics platform designed to process video streams in real time using computer vision, object detection, object tracking, intrusion detection, heatmap generation, line-crossing analysis, alerts, and analytics.

The system combines a React frontend with a FastAPI backend and YOLO-based computer vision to provide a centralized surveillance dashboard.

---

## 🚀 Features

### 🎥 Live Camera Monitoring

* Real-time laptop webcam access through the browser.
* Start and stop camera controls.
* Persistent camera stream while navigating between application pages.
* Fullscreen camera view.
* Camera status indicators.
* Live/offline/error states.

### 🤖 AI Object Detection

VisionEdge uses YOLO for real-time object detection.

Currently detected object categories include:

* Person
* Car
* Bus
* Motorcycle

The system processes video frames and generates bounding boxes and object labels.

### 🧠 Object Tracking

VisionEdge uses YOLO tracking with ByteTrack to maintain object identities across frames.

Tracking provides:

* Persistent object IDs
* Object movement tracking
* Line-crossing detection
* Restricted-zone monitoring

### 📊 Real-Time Analytics

The analytics engine continuously tracks:

* People count
* Car count
* Bus count
* Motorcycle count
* FPS
* People line crossings

Analytics data is exposed through the FastAPI backend and displayed in the React dashboard.

### 📈 Analytics Dashboard

The Analytics page provides:

* Real-time people detection trends
* Object distribution
* Live analytics updates
* Detection statistics
* Visualization of historical detection values

### 🚨 Intrusion Detection

VisionEdge includes restricted-zone monitoring.

When a person enters a configured restricted zone:

1. The detection is identified.
2. The tracked object ID is recorded.
3. A screenshot is captured.
4. The incident is stored.
5. An alert is generated.

A cooldown mechanism prevents repeated alerts for the same tracked object within a short period.

### 🔔 Alerts

VisionEdge can generate alerts for events such as:

* Intrusion detection
* Crowd detection
* High vehicle count

Example:

```text
Crowd Alert: 3 people detected
Traffic Alert: 5 cars detected
Intrusion Detected
```

### 💾 Database Storage

Analytics records are stored in the backend database.

Stored information can be used for:

* Historical analysis
* Reports
* Analytics
* Monitoring
* Future trend analysis

### 🔐 Authentication

VisionEdge uses JWT-based authentication.

Protected application routes require an authenticated user.

The system includes a demo account configured through environment variables.

---

# 🏗️ System Architecture

```text
                         VisionEdge
                             │
              ┌──────────────┴──────────────┐
              │                             │
        React Frontend                FastAPI Backend
              │                             │
      ┌───────┼────────┐             ┌──────┼──────────┐
      │       │        │             │      │          │
    Login  Dashboard Analytics     Video  Analytics  Alerts
      │       │        │             │      │          │
      └───────┴────────┘             │      │          │
              │                      │      │          │
        Camera Context               │      │          │
              │                      │      │          │
        Laptop Webcam                │      │          │
                                     │      │          │
                                     ▼      ▼          ▼
                                  OpenCV  YOLO      Database
                                     │
                                     ▼
                                  ByteTrack
                                     │
                   ┌─────────────────┼──────────────────┐
                   │                 │                  │
                Tracking          Heatmap          Intrusion
                   │                 │                  │
                   └─────────────────┼──────────────────┘
                                     │
                                  Analytics
```

---

# 🛠️ Technology Stack

## Frontend

* React
* Vite
* React Router
* Axios
* Recharts
* Lucide React
* JavaScript
* HTML
* CSS
* Browser MediaDevices API

## Backend

* Python
* FastAPI
* Uvicorn
* OpenCV
* Ultralytics YOLO
* ByteTrack
* SQLAlchemy
* JWT Authentication

## AI / Computer Vision

* YOLO11
* ByteTrack
* OpenCV
* Object Detection
* Object Tracking
* Heatmap Analysis
* Restricted Zone Detection
* Line Crossing Detection

## Database

* SQLAlchemy
* SQLite / configured database backend

## Deployment

* GitHub
* Render
* Render-hosted FastAPI backend
* Render-hosted React frontend

---

# 📁 Project Structure

```text
VisionEdge/
│
├── backend/
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── analytics.py
│   │   │   ├── alerts.py
│   │   │   ├── detection.py
│   │   │   ├── export.py
│   │   │   ├── history.py
│   │   │   ├── report.py
│   │   │   └── video.py
│   │   │
│   │   └── services/
│   │       ├── analytics_service.py
│   │       ├── alert_service.py
│   │       └── video_service.py
│   │
│   ├── auth/
│   │   ├── auth.py
│   │   └── security.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── core/
│   │   ├── heatmap.py
│   │   ├── line_counter.py
│   │   ├── restricted_zone.py
│   │   └── tracker.py
│   │
│   ├── database/
│   │   ├── crud.py
│   │   ├── database.py
│   │   └── models.py
│   │
│   └── main.py
│
├── frontend/
│   │
│   └── src/
│       ├── components/
│       │   ├── Charts.jsx
│       │   ├── ProtectedRoute.jsx
│       │   ├── Sidebar.jsx
│       │   └── Topbar.jsx
│       │
│       ├── context/
│       │   └── CameraContext.jsx
│       │
│       ├── pages/
│       │   ├── Analytics.jsx
│       │   ├── Dashboard.jsx
│       │   ├── Intrusions.jsx
│       │   ├── LiveCamera.jsx
│       │   ├── Login.jsx
│       │   └── Reports.jsx
│       │
│       ├── services/
│       │   └── api.jsx
│       │
│       ├── App.jsx
│       ├── main.jsx
│       └── index.css
│
├── assets/
│   ├── incidents/
│   └── videos/
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ Backend Setup

Clone the repository:

```bash
git clone <repository-url>
cd VisionEdge
```

Create a Python virtual environment:

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
pip install -r requirements.txt
```

---

# 🤖 YOLO Model

VisionEdge uses an Ultralytics YOLO model.

The tracker loads the model using:

```python
from ultralytics import YOLO

model = YOLO("yolo11n.pt")
```

The model is used for detection and tracking.

---

# ▶️ Run the Backend

From the project root:

```powershell
python -m uvicorn backend.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

# 💻 Frontend Setup

Navigate to the frontend:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

The frontend will normally run at:

```text
http://localhost:5173
```

---

# 🔑 Environment Variables

Create the required environment configuration for the frontend.

Example:

```text
VITE_API_URL=http://127.0.0.1:8000
```

For production, the frontend API URL should point to the deployed VisionEdge backend.

The backend supports environment variables such as:

```text
VIDEO_SOURCE
DEMO_EMAIL
DEMO_PASSWORD
DEMO_USERNAME
```

Example:

```text
VIDEO_SOURCE=0
```

A numeric `VIDEO_SOURCE` can be used for a webcam.

---

# 🎥 Video Sources

VisionEdge supports multiple video source types.

### Webcam

```text
VIDEO_SOURCE=0
```

### Video file

```text
VIDEO_SOURCE=assets/videos/traffic.mp4
```

### Absolute local path

```text
VIDEO_SOURCE=C:/Videos/traffic.mp4
```

### RTSP stream

```text
VIDEO_SOURCE=rtsp://...
```

### HTTP/HTTPS stream

```text
VIDEO_SOURCE=https://...
```

The backend automatically determines the source type.

---

# 📡 Video API

VisionEdge exposes the processed video stream through:

```text
GET /video
```

The endpoint returns an MJPEG stream.

The backend processes frames using:

```text
OpenCV
   ↓
YOLO
   ↓
ByteTrack
   ↓
Analytics
   ↓
Annotations
   ↓
MJPEG
```

---

# 📊 Analytics API

Endpoint:

```text
GET /analytics
```

Example response:

```json
{
  "fps": 28.4,
  "people": 2,
  "cars": 4,
  "buses": 0,
  "motorcycles": 1,
  "line_crossings": 0
}
```

The frontend periodically requests this endpoint to update the Analytics dashboard.

---

# 🔐 Authentication

The application uses JWT authentication.

The frontend stores the authentication token and attaches it to API requests:

```text
Authorization: Bearer <token>
```

Protected routes include:

```text
/dashboard
/live-camera
/analytics
/intrusions
/reports
```

---

# 📱 Application Pages

## Login

Authentication entry point for the application.

## Dashboard

Provides an overview of VisionEdge monitoring information.

## Live Camera

Displays the laptop webcam and camera controls.

Features:

* Start Camera
* Stop Camera
* Fullscreen
* Camera status
* Live status
* Monitoring status

## Analytics

Displays:

* People detection trend
* Object distribution
* Current detection counts
* Live analytics updates

## Intrusion Detection

Displays security-related detection events and alerts.

## Reports

Provides access to generated monitoring and analytics reports.

---

# 🧠 AI Processing Pipeline

Each frame follows the VisionEdge processing pipeline:

```text
Frame
  │
  ▼
YOLO Detection
  │
  ▼
ByteTrack Tracking
  │
  ▼
Object Classification
  │
  ├── Person
  ├── Car
  ├── Bus
  └── Motorcycle
  │
  ▼
Analytics
  │
  ├── Object Counts
  ├── FPS
  └── Line Crossings
  │
  ├── Heatmap
  ├── Restricted Zone
  ├── Alerts
  └── Database
  │
  ▼
Annotated Frame
```

---

# 🚨 Intrusion Detection Pipeline

```text
Person Detected
       │
       ▼
Object Tracking
       │
       ▼
Check Restricted Zone
       │
       ├── Outside → Continue Monitoring
       │
       └── Inside
              │
              ▼
        Check Cooldown
              │
              ▼
       Capture Screenshot
              │
              ▼
          Save Incident
              │
              ▼
         Generate Alert
```
---

# 🗄️ Database

VisionEdge stores analytics records through SQLAlchemy.

Database records can be used for:

* Historical analytics
* Reporting
* Detection statistics
* Monitoring history

---

# 🌐 Deployment

VisionEdge is designed to support deployment using Render.

The backend runs using:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

The frontend can be deployed separately as a Vite/React application.

The backend CORS configuration supports the deployed frontend origin.

---

# 🧪 Local Testing

Start the backend:

```powershell
python -m uvicorn backend.main:app --reload
```

Start the frontend:

```powershell
cd frontend
npm run dev
```

Then:

1. Open the frontend.
2. Login.
3. Open **Live Camera**.
4. Click **START CAMERA**.
5. Verify the webcam feed.
6. Navigate to **Dashboard**.
7. Navigate to **Analytics**.
8. Verify that detection statistics update.
9. Test intrusion detection.
10. Test reports and alerts.

---

# 🔒 Security Considerations

VisionEdge uses:

* JWT authentication
* Protected API routes
* Password hashing
* Environment variables for configurable credentials
* CORS configuration
* Protected frontend routes

Sensitive credentials should not be committed to GitHub.

---

# 🎯 Future Enhancements

Planned improvements include:

* Multi-camera support
* RTSP camera management
* Advanced person tracking
* Face recognition
* Vehicle classification
* License plate recognition
* Configurable restricted zones
* Configurable counting lines
* Advanced alert rules
* Email notifications
* Mobile monitoring
* Historical analytics
* AI-based anomaly detection
* Cloud storage for incidents
* Performance optimization
* Hardware acceleration

---

# 👩‍💻 Project

**VisionEdge**

AI-Powered Real-Time Video Analytics & Intelligent Surveillance System

Built using modern web development, computer vision, AI, and real-time analytics technologies.

---

## License

This project is currently developed as an academic/portfolio project.

License terms can be added when the project is prepared for public distribution.
