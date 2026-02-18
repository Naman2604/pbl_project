# 🚗 Smart Parking Detection System (AI + OpenCV + Flask + React)

A real-time AI-powered parking monitoring system that detects vehicles, identifies available parking slots, and streams live video to a dashboard.

This project integrates **computer vision, backend APIs, and a modern frontend dashboard** to simulate a production-ready smart parking solution.

---

## 📌 Project Overview

The system uses a parking CCTV/video feed and performs:

* 🚘 Vehicle detection using OpenCV
* 🅿️ Parking slot occupancy analysis
* 📊 Real-time analytics generation
* 🎥 Live video streaming via Flask backend
* 💻 Interactive dashboard frontend
* ☁️ Cloud deployment (Render + Vercel)

---

## 🧠 How It Works

```
Parking video / CCTV
        ↓
OpenCV frame processing
        ↓
Vehicle + slot detection
        ↓
Analytics engine updates stats
        ↓
Flask backend streams video (/video_feed)
        ↓
Frontend dashboard fetches:
   • Live video
   • Parking stats
```

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* OpenCV
* NumPy
* Gunicorn

### Frontend

* React
* Tailwind / CSS
* Dashboard UI

### Deployment

* Backend hosted on Render
* Frontend hosted on Vercel
* Source code on GitHub

---

## 📂 Project Structure

```
pbl_project/
│
├── app.py                 # Flask backend
├── detection.py           # Vehicle & slot detection logic
├── analytics.py           # Parking stats logic
├── parking.mp4            # Test parking footage
├── requirements.txt
│
├── templates/
│   └── dashboard.html
│
├── frontend/              # React frontend (Vercel deployed)
│
└── README.md
```

---

## ⚙️ Installation (Local Setup)

### 1️⃣ Clone repository

```bash
git clone https://github.com/Naman2604/pbl_project.git
cd pbl_project
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run backend

```bash
python app.py
```

Backend runs at:

```
http://localhost:5000
```

---

## 🎥 API Endpoints

### Live video stream

```
/video_feed
```

### Parking stats JSON

```
/api/stats
```

---

## 🌐 Deployment

### Backend

* Hosted on Render
* Runs Flask + Gunicorn
* Streams AI-processed video

### Frontend

* Hosted on Vercel
* Connects to backend APIs
* Displays live CCTV feed & analytics

---

## 📊 Features

* Real-time parking slot detection
* Live MJPEG video streaming
* Dashboard analytics
* Cloud deployment ready
* Modular detection pipeline
* Works with CCTV / recorded footage

---

## 🚀 Future Improvements

* YOLOv8 vehicle detection
* Multi-camera support
* Database integration (MongoDB)
* Mobile responsive UI
* Smart parking reservation system
* License plate recognition

---

## 👨‍💻 Author

**Naman**

AI / Computer Vision Project
Final Year Engineering Project – Smart Parking System

---

## ⭐ Contribution

Feel free to fork this repo and improve:

* Detection accuracy
* UI dashboard
* Deployment pipeline
* Real-world CCTV integration

---

## 📜 License

This project is for educational and research purposes.
