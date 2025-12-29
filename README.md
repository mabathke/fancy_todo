# Todo Backend

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:
```bat
.venv\Scripts\activate
```

## Run

```bash
uvicorn app.main:app --reload
```

API:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
