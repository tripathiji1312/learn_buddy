# LearnBuddy 🎓

<div align="center">
  
  ![LearnBuddy Logo](https://img.shields.io/badge/🎓-LearnBuddy-blue?style=for-the-badge&labelColor=darkblue&color=lightblue)
  
  **A free, open-source, AI-driven adaptive learning platform dedicated to making personalized education accessible to every child.**
  
  [![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
  [![Contributors](https://img.shields.io/github/contributors/tripathiji1312/learn_buddy?style=for-the-badge&color=brightgreen)](https://github.com/tripathiji1312/learn_buddy/graphs/contributors)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](http://makeapullrequest.com)
  [![GitHub Stars](https://img.shields.io/github/stars/tripathiji1312/learn_buddy?style=for-the-badge&color=gold)](https://github.com/tripathiji1312/learn_buddy/stargazers)
  [![GitHub Forks](https://img.shields.io/github/forks/tripathiji1312/learn_buddy?style=for-the-badge&color=orange)](https://github.com/tripathiji1312/learn_buddy/network)
  
  ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
  ![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
  ![AI](https://img.shields.io/badge/AI%20Powered-FF6B6B?style=for-the-badge&logo=brain&logoColor=white)
  
</div>

---

## ✨ Our Vision

> 🌟 *"In a world of diverse learning needs, one-size-fits-all education falls short."*

LearnBuddy was created to change that. We envision a future where every child, regardless of their physical, sensory, or cognitive abilities, has **free access** to a personal AI tutor that understands their pace, adapts to their style, and makes learning a joyful adventure.

<div align="center">
  
  ![Vision](https://img.shields.io/badge/🌍-Accessible%20Education%20for%20All-purple?style=for-the-badge)
  ![Community](https://img.shields.io/badge/🤝-Community%20Driven-green?style=for-the-badge)
  ![Open Source](https://img.shields.io/badge/🔓-100%25%20Open%20Source-orange?style=for-the-badge)
  
</div>

This is a **community-driven project**. We believe that by working together, we can build a powerful, free alternative to commercial learning platforms.

---

## 🚀 Key Features

<div align="center">

| 🎯 Feature | 📝 Description |
|------------|----------------|
| **🧠 Adaptive AI Engine** | A reinforcement learning model adapts question difficulty in real-time, ensuring every learner is perfectly challenged |
| **🎮 Gamified Experience** | Learners earn XP, unlock achievements, and maintain "streaks," transforming learning into a motivating game |
| **♿ Accessibility First** | Built from the ground up for universal access with features like high-contrast themes, keyboard navigation, and voice commands |
| **🤖 NLP-Powered Evaluation** | Uses Sentence-Transformers to understand the semantic meaning of answers for flexible and intelligent grading |
| **🛡️ Secure Admin Panel** | A comprehensive dashboard for platform management, user administration, and content curation |
| **📦 Fully Containerized** | Easy to set up and deploy locally with Docker and Docker Compose |

</div>

---

## 🎯 Quick Demo

<div align="center">
  
  ![Demo](https://img.shields.io/badge/🎬-Live%20Demo%20Coming%20Soon-red?style=for-the-badge)
  
  *Experience LearnBuddy in action - personalized learning that adapts to you!*
  
</div>

---

## ❤️ Why Contribute?

Contributing to LearnBuddy means you're helping to build a more **equitable** and **effective** educational future. Whether you're a seasoned developer, a UX designer, an educator, or just starting your coding journey, your input is valuable.

<div align="center">

| 🌟 Benefit | 💡 Impact |
|------------|-----------|
| **🌍 Make a Real-World Impact** | Your code will directly help children learn more effectively |
| **⚡ Work with Modern Tech** | Get hands-on experience with FastAPI, PostgreSQL, AI/ML models, and Docker |
| **🤝 Join a Welcoming Community** | We are committed to creating a supportive and collaborative environment |
| **📈 Build Your Portfolio** | Showcase your skills on a meaningful open-source project |

</div>

---

## 🚀 Getting Started

<div align="center">
  
  ![Getting Started](https://img.shields.io/badge/⚡-Quick%20Setup%20in%205%20Minutes-brightgreen?style=for-the-badge)
  
</div>

### 📋 Prerequisites

- ![Docker](https://img.shields.io/badge/Docker-Required-blue?logo=docker) **Docker & Docker Compose**: [Install Docker Desktop](https://www.docker.com/products/docker-desktop)
- ![Git](https://img.shields.io/badge/Git-Required-orange?logo=git) **Git**: For cloning the repository

### 🛠️ Installation & Setup

**1️⃣ Fork & Clone the Repository**
```bash
git clone https://github.com/YOUR-USERNAME/learnbuddy.git
cd learnbuddy
```

**2️⃣ Build and Run the Containers**
```bash
docker-compose up --build -d
```

**3️⃣ Seed the Database**
```bash
docker-compose run --rm backend python scripts/seed_db.py
```

**4️⃣ Start the Frontend**
- Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension in VS Code
- Right-click on `index.html` and select **"Open with Live Server"**

### 🌐 Usage

<div align="center">

| 🎯 Service | 🔗 URL | 👤 Credentials |
|------------|--------|----------------|
| **🎓 Learner App** | `http://127.0.0.1:5500/` | `testuser` / `testpass` |
| **⚙️ Admin Panel** | `http://127.0.0.1:5500/admin-login.html` | `admin` / `adminpassword` |

</div>

---

## 🤝 How to Contribute

<div align="center">
  
  ![Contribution Welcome](https://img.shields.io/badge/🎉-All%20Contributions%20Welcome-success?style=for-the-badge)
  
</div>

We welcome contributions of all kinds! Here's how you can get started:

### 🎯 Contribution Steps

1. **💬 Join the Discussion**: Check out the [Issues tab](https://github.com/tripathiji1312/learn_buddy/issues)
2. **🏷️ Pick an Issue**: Look for issues tagged with `good first issue` or `help wanted`
3. **🔄 Follow the Contribution Workflow**:
   ```bash
   # Create a new branch
   git checkout -b feature/your-feature-name
   
   # Commit your changes
   git commit -m 'feat: Add your new feature'
   
   # Push to your branch
   git push origin feature/your-feature-name
   
   # Open a Pull Request
   ```

<div align="center">
  
  [![Good First Issues](https://img.shields.io/github/issues/tripathiji1312/learn_buddy/good%20first%20issue?style=for-the-badge&color=purple&label=Good%20First%20Issues)](https://github.com/tripathiji1312/learn_buddy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
  [![Help Wanted](https://img.shields.io/github/issues/tripathiji1312/learn_buddy/help%20wanted?style=for-the-badge&color=red&label=Help%20Wanted)](https://github.com/tripathiji1312/learn_buddy/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
  
</div>

Please read our `CONTRIBUTING.md` file for more detailed guidelines.

---

## 🗺️ Project Roadmap

<div align="center">
  
  ![Roadmap](https://img.shields.io/badge/🚀-Exciting%20Features%20Coming-blue?style=for-the-badge)
  
</div>

### 🎯 Phase 1: Core Features
- [ ] **📚 More Learning Modules**: Reading Comprehension, Science, and History
- [ ] **📊 Advanced Analytics**: Detailed progress dashboards for parents and educators
- [ ] **👥 "Study Buddies" Feature**: Collaborative challenges for learners

### 🎯 Phase 2: Global Expansion
- [ ] **🌍 Internationalization (i18n)**: Translate the platform into multiple languages
- [ ] **🤖 Enhanced AI**: Evolve the recommendation engine to suggest new topics and identify learning gaps

### 🎯 Phase 3: Platform Maturity
- [ ] **⚙️ CI/CD Pipeline**: Automate testing and deployment workflows
- [ ] **📱 Mobile App**: Native mobile applications for iOS and Android
- [ ] **🔊 Voice Integration**: Voice-based learning and interaction

---

## 📊 Project Stats

<div align="center">
  
  ![GitHub repo size](https://img.shields.io/github/repo-size/tripathiji1312/learn_buddy?style=for-the-badge&color=blue)
  ![GitHub code size](https://img.shields.io/github/languages/code-size/tripathiji1312/learn_buddy?style=for-the-badge&color=green)
  ![GitHub last commit](https://img.shields.io/github/last-commit/tripathiji1312/learn_buddy?style=for-the-badge&color=red)
  ![GitHub issues](https://img.shields.io/github/issues/tripathiji1312/learn_buddy?style=for-the-badge&color=orange)
  ![GitHub pull requests](https://img.shields.io/github/issues-pr/tripathiji1312/learn_buddy?style=for-the-badge&color=purple)
  
</div>

---

## 🛠️ Tech Stack

<div align="center">
  
  **Backend**
  
  ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
  ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
  
  **Frontend**
  
  ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
  ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
  ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
  
  **AI/ML**
  
  ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
  ![Transformers](https://img.shields.io/badge/🤗%20Transformers-FFD21E?style=for-the-badge)
  
  **DevOps**
  
  ![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
  ![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
  
</div>

---

## 🏆 Contributors

<div align="center">
  
  ![Contributors](https://img.shields.io/badge/🙏-Thank%20You%20Contributors-red?style=for-the-badge)
  
  <a href="https://github.com/tripathiji1312/learn_buddy/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=tripathiji1312/learn_buddy" />
  </a>
  
  *Made with [contrib.rocks](https://contrib.rocks)*
  
</div>

---

## 📞 Connect With Us

<div align="center">
  
  [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/tripathiji1312/learn_buddy)
  [![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](#)
  [![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](#)
  
</div>

---

## 📜 License

<div align="center">
  
  ![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
  
  This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
  
  *Free to use, modify, and distribute! 🎉*
  
</div>

---

<div align="center">
  
  ### 💝 Show Your Support
  
  If you find LearnBuddy helpful, please consider giving it a ⭐ on GitHub!
  
  ![Star](https://img.shields.io/badge/⭐-Star%20This%20Repo-yellow?style=for-the-badge)
  
  **Made with ❤️ by the LearnBuddy Community**
  
  ---
  
  *"Education is the most powerful weapon which you can use to change the world." - Nelson Mandela*
  
</div>
