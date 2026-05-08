# 💬 NexChat

A real-time chat application built with Python Flask, Socket.IO, MySQL, and Vanilla JS.
Deployed on AWS with Docker, Kubernetes, Terraform, Ansible, Jenkins, Grafana, and ELK Stack.

---

## 🚀 Phase 1 — Local Setup

### Prerequisites
- Python 3.10+
- MySQL installed and running

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/nexchat-app.git
cd nexchat-app
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up MySQL database
```bash
mysql -u root -p < setup.sql
```

### 5. Configure environment
```bash
cp .env.example .env
# Edit .env and set your DB_PASSWORD
```

### 6. Run the app
```bash
python app.py
```

Open http://localhost:5000 in your browser 🎉

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask + Flask-SocketIO |
| Frontend | HTML + CSS + Vanilla JS |
| Database | MySQL (local) / AWS RDS MySQL (production) |
| Real-time | Socket.IO (WebSockets) |
| Auth | Session-based with password hashing |

---

## 📦 Coming Next (DevOps Phases)

- **Phase 2** — Docker + Docker Compose
- **Phase 3** — Terraform (AWS VPC, EC2, RDS, EKS, S3)
- **Phase 4** — Ansible (server config)
- **Phase 5** — Jenkins CI/CD pipeline
- **Phase 6** — Kubernetes on AWS EKS
- **Phase 7** — Grafana + Prometheus monitoring
- **Phase 8** — ELK Stack logging
- **Phase 9** — SSL + Route53 + CloudFront

---

## ✨ Features

- ✅ User signup / login with avatar selection
- ✅ 1-on-1 private chat
- ✅ Group chat rooms (create your own)
- ✅ Real-time messaging (no page refresh)
- ✅ Typing indicators
- ✅ Online / offline status
- ✅ Chat history saved in MySQL
- ✅ Clean dark UI

---

Built by [Your Name] — Portfolio Project
