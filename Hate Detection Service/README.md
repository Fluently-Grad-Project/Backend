```bash
python -m venv nlp_venv     
```

```bash
nlp_venv\Scripts\activate       
```

```bash
pip install -r requirements.txt
```


```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```