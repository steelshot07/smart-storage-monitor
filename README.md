# Smart Storage Health Monitor

A full-stack storage health monitoring app with ML-based failure prediction.

## Stack
- Frontend: React + Vite
- Backend: FastAPI + Python
- ML: scikit-learn trained on Backblaze hard drive dataset
- SMART data: smartmontools

## Requirements
- Python 3.9+
- Node.js 18+
- smartmontools installed and in PATH

## Setup

### Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python train.py              # trains the ML model
uvicorn main:app --reload    # run as Administrator

### Frontend
cd frontend
npm install
npm run dev
