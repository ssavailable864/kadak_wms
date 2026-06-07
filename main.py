### 2. `main.py`
* **Yeh kya hai?** Yeh hamare pure software ka main gate (entry point) hai. Jab server chalu hoga, toh sabse pehle yahi file run hogi.
* **VS Code me kaise banayein?** Ek nayi file bana aur naam rakh `main.py`. Uske andar abhi ke liye yeh chota sa testing code likh de:
  ```python
  from fastapi import FastAPI

  app = FastAPI()

  @app.get("/")
  def home():
      return {"message": "Bhai, tera kadak WMS software live ho gaya local par!"}