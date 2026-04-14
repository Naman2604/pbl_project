
# 🚗 Smart Parking Detection System

> An AI-powered, real-time parking monitoring system built with OpenCV, Flask, and React — designed to detect vehicles, track slot occupancy, and stream live analytics to a web dashboard.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [How It Works](#-how-it-works)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Dashboard Features](#-dashboard-features)
- [Deployment](#-deployment)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [Author](#-author)
- [License](#-license)

---

## 📖 Project Overview

The **Smart Parking Detection System** is a computer vision project that simulates an intelligent parking management solution using a CCTV feed (live or recorded). It processes video frames in real time to:

- Detect vehicles using **OpenCV**
- Determine which parking slots are **occupied or available**
- Generate **live analytics** (total slots, occupied, available, occupancy rate)
- Stream the processed video feed to a **React-based web dashboard**
- Expose data via a clean **REST API** for frontend consumption

This project was built as a **Final Year Engineering Project** demonstrating the integration of computer vision, backend services, and modern frontend development — ready for cloud deployment.

---

## 🧠 How It Works

The system follows a clear processing pipeline from raw video to live dashboard:

```
📹 Parking Video / CCTV Feed
         │
         ▼
🖼️  OpenCV Frame Capture & Processing
         │
         ▼
🚘  Vehicle Detection (contour/background subtraction)
         │
         ▼
🅿️  Parking Slot Occupancy Analysis
   (Each predefined slot region is checked for vehicle presence)
         │
         ▼
📊  Analytics Engine
   (Counts occupied/free slots, calculates occupancy %)
         │
         ▼
🐍  Flask Backend
   ├── /video_feed  → Streams MJPEG video with overlays
   └── /api/stats   → Returns JSON parking analytics
         │
         ▼
💻  React Frontend Dashboard
   ├── Renders live video stream
   ├── Displays parking slot status
   └── Shows real-time stats & charts
```

### Detection Logic (detection.py)

The detection module works by:
1. **Loading the video feed** — either a live CCTV stream or a `.mp4` test file
2. **Defining parking slot regions** — each slot is a rectangular region of interest (ROI) mapped to real parking spaces in the frame
3. **Analyzing each ROI per frame** — pixel intensity, contour detection, or background subtraction determines if a vehicle is present
4. **Annotating the frame** — slots are color-coded (e.g., 🟢 green = free, 🔴 red = occupied) and overlaid on the video

### Analytics Engine (analytics.py)

The analytics module aggregates detection results each frame and maintains a running count of:
- **Total slots** defined in the system
- **Occupied slots** (vehicle detected)
- **Available slots** (no vehicle detected)
- **Occupancy rate** (% of slots in use)

This data is exposed as JSON through the Flask API for the frontend to poll and display.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                │
│                                                     │
│   React Dashboard                                   │
│   ├── Live Video Player  (fetches /video_feed)      │
│   ├── Slot Status Grid   (fetches /api/stats)       │
│   └── Analytics Charts                             │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP / MJPEG Stream
┌─────────────────────▼───────────────────────────────┐
│                  BACKEND (Render)                   │
│                                                     │
│   Flask + Gunicorn                                  │
│   ├── app.py         → Route handlers               │
│   ├── detection.py   → OpenCV frame processing      │
│   └── analytics.py   → Stats aggregation           │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              VIDEO SOURCE                           │
│   parking.mp4 (test) or Live CCTV stream            │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3** | Core backend language |
| **Flask** | Lightweight web framework for API and video streaming |
| **OpenCV** | Frame capture, vehicle detection, image processing |
| **NumPy** | Numerical operations on image arrays |
| **Gunicorn** | WSGI server for production deployment |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React** | Component-based UI framework |
| **Tailwind CSS / CSS** | Styling and responsive layout |
| **Fetch API** | Polling backend for live stats |

### Deployment
| Service | Role |
|---------|------|
| **Render** | Hosts the Flask backend (Python + Gunicorn) |
| **Vercel** | Hosts the React frontend (static build) |
| **GitHub** | Source code repository and version control |

---

## 📂 Project Structure

```
pbl_project/
│
├── app.py                  # Flask application entry point
│                           # Defines routes: /video_feed, /api/stats
│
├── detection.py            # Core computer vision logic
│                           # Loads video, defines slot ROIs, detects vehicles
│
├── analytics.py            # Parking statistics engine
│                           # Tracks occupied/free slots, computes occupancy %
│
├── parking.mp4             # Sample parking footage for local testing
│
├── requirements.txt        # Python dependencies
│
├── templates/
│   └── dashboard.html      # Optional server-side rendered dashboard (Jinja2)
│
├── frontend/               # React application (deployed separately on Vercel)
│   ├── src/
│   │   ├── App.jsx         # Root component
│   │   ├── components/     # Dashboard UI components
│   │   └── ...
│   ├── package.json
│   └── ...
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:
- Python 3.8 or higher
- pip
- Node.js + npm (for frontend development)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Naman2604/pbl_project.git
cd pbl_project
```

### 2. Set Up the Python Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

Key packages installed:
- `flask` — web framework
- `opencv-python` — computer vision
- `numpy` — array operations
- `gunicorn` — production server

### 4. Run the Backend Server

```bash
python app.py
```

The backend will start at:

```
http://localhost:5000
```

You can now access:
- **Live video feed:** `http://localhost:5000/video_feed`
- **Parking stats API:** `http://localhost:5000/api/stats`

### 5. Run the Frontend (Optional — Local Development)

```bash
cd frontend
npm install
npm start
```

The React dashboard will start at:

```
http://localhost:3000
```

> Make sure the frontend is configured to point to `http://localhost:5000` as the API base URL for local development.

---

## 📡 API Reference

### `GET /video_feed`

Streams a live MJPEG video feed of the parking lot with visual overlays showing slot status.

- **Response type:** `multipart/x-mixed-replace; boundary=frame`
- **Usage:** Drop directly into an `<img>` tag in HTML or the React frontend

```html
<img src="http://localhost:5000/video_feed" />
```

---

### `GET /api/stats`

Returns the current parking analytics as a JSON object.

- **Response type:** `application/json`

**Example Response:**

```json
{
  "total_slots": 20,
  "occupied": 13,
  "available": 7,
  "occupancy_rate": 65.0
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total_slots` | integer | Total number of parking slots tracked |
| `occupied` | integer | Number of slots currently occupied |
| `available` | integer | Number of slots currently free |
| `occupancy_rate` | float | Percentage of slots in use |

---

## 💻 Dashboard Features

The React frontend dashboard provides:

| Feature | Description |
|---------|-------------|
| 🎥 **Live Video Feed** | Displays the MJPEG stream with slot overlays from the backend |
| 🟢🔴 **Slot Status Grid** | Visual grid showing each slot's occupancy state in real time |
| 📊 **Analytics Panel** | Shows total, occupied, and available slots with occupancy percentage |
| 🔄 **Auto-refresh** | Polls `/api/stats` at regular intervals for up-to-date data |
| ☁️ **Cloud-ready** | Configured to connect to the Render-hosted backend when deployed |

---

## 🌐 Deployment

### Backend — Render

1. Push your code to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `gunicorn app:app`
5. Render will assign a public URL (e.g., `https://your-app.onrender.com`)

### Frontend — Vercel

1. Push the `frontend/` folder (or a separate repo) to GitHub
2. Import the project on [Vercel](https://vercel.com)
3. Set the environment variable for the backend URL:
   ```
   REACT_APP_API_URL=https://your-app.onrender.com
   ```
4. Vercel auto-builds and deploys on every push

---

## 🔮 Future Roadmap

| Feature | Description |
|---------|-------------|
| 🤖 **YOLOv8 Integration** | Replace basic detection with a deep learning model for higher accuracy |
| 📷 **Multi-camera Support** | Monitor multiple parking areas simultaneously |
| 🗄️ **Database Integration** | Store historical occupancy data in MongoDB for trend analysis |
| 📱 **Mobile Responsive UI** | Optimize dashboard for phones and tablets |
| 🅿️ **Parking Reservation** | Allow users to reserve slots in advance via the dashboard |
| 🔢 **License Plate Recognition** | Identify and log vehicles entering/exiting using OCR |
| 🔔 **Alerts & Notifications** | Send alerts when parking lot reaches capacity |
| 🔐 **Authentication** | Admin login to manage slot configurations |

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help improve the project:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Commit** your changes: `git commit -m "Add: your feature description"`
4. **Push** to your branch: `git push origin feature/your-feature-name`
5. **Open** a Pull Request

### Areas open for contribution:
- Improving vehicle detection accuracy
- Enhancing the UI dashboard
- Adding new API endpoints
- Integrating real-world CCTV streams
- Writing unit/integration tests
- Improving deployment pipeline and CI/CD

---

## 👨‍💻 Author

**Naman**
- 🎓 Final Year Engineering Student
- 🧠 Focus: AI, Computer Vision, Full-Stack Development
- 📦 GitHub: [github.com/Naman2604](https://github.com/Naman2604)

---

## 📜 License

This project is intended for **educational and research purposes only**.  
Feel free to use, modify, and build upon it with proper attribution.

---

<div align="center">
  ⭐ If you found this project helpful, please give it a star on GitHub!
</div>

