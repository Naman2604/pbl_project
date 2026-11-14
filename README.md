
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

- Detect vehicles using **YOLOv8** (Ultralytics) with **OpenCV** for video handling
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
🚘  Vehicle Detection (YOLOv8)
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
1. **Detecting vehicles** — YOLOv8 finds cars, motorcycles, buses and trucks in each frame
2. **Loading parking slots** — slot rectangles come from `slots.json`, which `calibrate_slots.py` generates automatically from the video (a spot where a car stays parked is a slot)
3. **Matching vehicles to slots** — each vehicle is assigned to at most one slot, the one it overlaps most (IoU)
4. **Smoothing** — a slot only flips between free and occupied after the new state is seen 5 detections in a row, so the numbers don't flicker when YOLO misses a car for one frame
5. **Annotating the frame** — slots are overlaid on the video (🟢 free, 🔴 occupied) with a summary bar

A background thread in `app.py` does all of this ~3 times per second and keeps the newest annotated frame in memory, so the stats stay live even when nobody has the video open.

> **Camera view matters.** Slots are fixed rectangles, so they only fit one camera view. The bundled `parking.mp4` changes camera angle after about frame 4650, so `slots.json` records `frame_start`/`frame_end` and the app loops only that range. If you use your own video, run `python calibrate_slots.py` (see below).

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
| **YOLOv8 (Ultralytics)** | Vehicle detection |
| **OpenCV** | Video reading, drawing overlays, JPEG encoding |
| **NumPy** | Numerical operations on image arrays |
| **Gunicorn** | WSGI server for production deployment |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js / React** | Dashboard UI framework |
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
├── app.py                  # Flask app: background video thread + routes
│                           # /video_feed, /api/stats, /api/slots, /health
│
├── detection.py            # YOLOv8 vehicle detection + slot occupancy logic
├── calibrate_slots.py      # Finds the parking slots in a video -> slots.json
├── slots.json              # Slot rectangles + the video frame range they apply to
├── analytics.py            # Thread-safe parking statistics
│
├── parking.mp4             # Sample parking footage
├── yolov8n.pt              # YOLOv8 nano weights
├── requirements.txt        # Python dependencies
│
├── frontend/               # Next.js dashboard (deployed separately on Vercel)
│   ├── components/dashboard/   # Cards, CCTV panel, live parking grid, charts
│   ├── hooks/use-polling.ts    # Polls the backend without overlapping requests
│   ├── lib/api.ts              # Backend URL (NEXT_PUBLIC_API_URL)
│   └── .env.example
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

(`slots.json` is already included for `parking.mp4`. For your own video run
`python calibrate_slots.py --video your.mp4` first, open the generated
`slots_preview.jpg` to check the boxes, and use `--end N` to stop before any
camera cut.)

The backend will start at:

```
http://localhost:5000
```

You can now access:
- **Live video feed:** `http://localhost:5000/video_feed`
- **Parking stats API:** `http://localhost:5000/api/stats`
- **Per-slot status:** `http://localhost:5000/api/slots`
- **Health check:** `http://localhost:5000/health`

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
| `updated_at` | float | Unix time of the last detection |

`total` and `occupancy` are also returned as deprecated aliases of `total_slots` and `occupancy_rate`.

---

### `GET /api/slots`

Returns the live state of every tracked slot, in the same order as the labels on the video (`P1`, `P2`, ...).

```json
[{"id": "P1", "occupied": true}, {"id": "P2", "occupied": false}]
```

---

### `GET /health`

Always returns HTTP 200 with `status` (`ok` or `starting_or_degraded`), `video_open`, `slots_loaded`, `seconds_since_last_frame` and `last_error`. Use it first when something looks wrong.

---

## 💻 Dashboard Features

The React frontend dashboard provides:

| Feature | Description |
|---------|-------------|
| 🎥 **Live Video Feed** | Displays the MJPEG stream with slot overlays from the backend |
| 🟢🔴 **Slot Status Grid** | Visual grid showing each slot's occupancy state in real time |
| 📊 **Analytics Panel** | Shows total, occupied, and available slots with occupancy percentage |
| 🔄 **Auto-refresh** | Polls `/api/stats` and `/api/slots` every second; shows a notice and retries if the backend is unreachable |
| ☁️ **Cloud-ready** | Configured to connect to the Render-hosted backend when deployed |

---

> **Note:** the hourly-usage chart, zone utilization chart and AI-insights panel still use sample data from `frontend/lib/mock-data.ts`. The stat cards, the slot grid and the video are live.

---

## 🌐 Deployment

### Backend — Render

1. Push your code to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `gunicorn app:app --workers 1 --threads 16 --timeout 120`
   - Keep `--workers 1` (the detector and stats live in one process) and use several `--threads`: every open video stream occupies one thread, so a plain `gunicorn app:app` (one worker, one thread) would block `/api/stats` while the video is open.
   - YOLO needs RAM (PyTorch alone uses several hundred MB). Render's free 512 MB plan may run out of memory; if the service keeps restarting, use a larger instance. Free instances also sleep when idle and take about a minute to wake up.
5. Render will assign a public URL (e.g., `https://your-app.onrender.com`)

### Frontend — Vercel

1. Push the `frontend/` folder (or a separate repo) to GitHub
2. Import the project on [Vercel](https://vercel.com)
3. Set the environment variable for the backend URL:
   ```
   NEXT_PUBLIC_API_URL=https://your-app.onrender.com
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

