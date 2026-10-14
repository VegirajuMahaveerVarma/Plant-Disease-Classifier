# AgriVision AI 🌿

Full-stack plant disease classification starter built with Next.js, FastAPI, PyTorch, and PostgreSQL.

> **Important:** No trained weights or measured performance metrics are included. Until you train a model and configure its checkpoint, the API responds that the model is unavailable instead of inventing predictions. This is an educational prototype, not an agricultural diagnosis.

## Stack and features
- Next.js App Router, React, TypeScript, Tailwind CSS
- FastAPI with image validation and ML inference
- PyTorch/torchvision ResNet18 training and evaluation scripts
- SQLite for local setup; PostgreSQL supported with DATABASE_URL
- Responsive dashboard, image upload, prediction results, scan history, CSV export, disease library, service/model status
- API smoke tests and GitHub Actions CI

## Python version
This guide is adapted for **Python 3.14**. The dependency files use version ranges rather than requiring Python 3.11. PyTorch and torchvision must provide compatible wheels for your Python version and platform; if pip reports that no compatible distribution exists, use a Python version supported by the selected PyTorch release rather than forcing an install.

## Local setup (Windows CMD)

### Backend
Run these commands in CMD:
```bat
cd /d D:\Projects\Plant-Disease-Classifier\backend
py -3.14 -m venv .venv
.venv\Scripts\activate
python --version
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```
API docs at http://localhost:8000/docs. Keep this terminal open while testing.

### Frontend (new CMD window)
```bat
cd /d D:\Projects\Plant-Disease-Classifier\frontend
copy .env.example .env.local
npm install
npm run dev
```
Open http://localhost:3000.

### Optional PostgreSQL
```bat
cd /d D:\Projects\Plant-Disease-Classifier
docker compose up -d db
```
Set `DATABASE_URL=postgresql+psycopg://agrivision:agrivision_dev_only@localhost:5432/agrivision` in `backend/.env`. These credentials are for local development only; change them before use beyond local testing.

## Train a real model
Download PlantVillage separately from https://github.com/spMohanty/PlantVillage-Dataset and organize it as an ImageFolder dataset:
```
data/plantvillage/
  Tomato___Early_blight/
  Tomato___healthy/
  ... one folder per class
```
From the repository root in CMD:
```bat
cd /d D:\Projects\Plant-Disease-Classifier
py -3.14 -m venv .venv-ml
.venv-ml\Scripts\activate
python -m pip install --upgrade pip
pip install -r ml\requirements.txt
python ml\train.py --data-dir data\plantvillage --output-dir backend\models --epochs 5
```
If installation reports that torch or torchvision has no compatible distribution, stop and use a Python version supported by the available PyTorch wheels. Do not install packages globally to work around the error.

Set `MODEL_PATH=models/plant_disease_resnet18.pt` and `CLASS_NAMES_PATH=models/class_names.json` in `backend/.env`, then restart the API. Actual metrics are written by your run; no results are claimed in advance.

To evaluate a separately prepared ImageFolder test set:
```bat
python ml\evaluate.py --data-dir data\field-test --checkpoint backend\models\plant_disease_resnet18.pt --output reports\field-evaluation.json
```
The test set's class folder names and ordering must match the checkpoint. Do not use training images as an independent test set.

## API
- `GET /health` — database and model readiness
- `GET /api/v1/diseases` — educational reference entries
- `POST /api/v1/predict` — upload image; returns prediction or 503 until model is configured
- `GET /api/v1/scans` — scan records
- `DELETE /api/v1/scans/{scan_id}` — delete record

## Security status
**No user authentication is implemented yet.** Scan history is shared by clients of the same database. Keep the app local-only until authentication, per-user authorization, rate limiting, production migrations, and deployment settings are added. Original image bytes are processed in memory and are not saved as files.

See [docs/model-card.md](docs/model-card.md) for intended use and limitations. MIT license.
