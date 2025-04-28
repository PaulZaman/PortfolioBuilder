# 📈 Intelligent Portfolio Optimization Platform - Backend (API)

FastAPI backend for authentication, user profile management, and integration with Firebase services.

---

## 🚀 How to Launch the Backend

### Create venv and Activate

Make sure you are in the api directory of the project.

```bash
# Create a virtual environment
python -m venv venv
```
Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Server
```bash
uvicorn app.main:app --reload
```