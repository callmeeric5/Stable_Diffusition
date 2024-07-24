# Stable_Diffusition

This application is the MVP of action learning. 

## Install

```
pip install -r requirements.txt
```

## Prerequisites
```
brew install postgresql # if havn't install postgresql
brew services run postgresql #run the postgresql
psql -U postgres

# Create db & user
CREATE DATABASE stable_diffusion;
CREATE USER admin WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE stable_diffusion TO admin;
```

Create `.streamlit/secrets.toml` and write your DB and API url inside, like:
```
DATABASE_URL = "postgresql://admin:admin@localhost/stable_diffusion"
API_URL = "http://localhost:8000"
```
## Run
```
cd Stable_Diffusition

streamlit run 1_🏠_Home.py
python app.py
```

## Demo
### Welocme
![img.png](img/welcome.png)

### Home
![img.png](img/home.png)
### Gallery
![img.png](img/gallery.png)