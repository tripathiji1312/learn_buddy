# LearnBuddy - Open Source Adaptive Learning Platform

 <!-- It's highly recommended to create a hero image/logo and upload it -->


**LearnBuddy is a free, open-source, AI-driven adaptive learning platform dedicated to making personalized education accessible to every child.**

Our mission is to build a tool that is not only intelligent and engaging but is also designed with inclusivity at its core. This project is for learners, educators, developers, and anyone passionate about the future of education.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub contributors](https://img.shields.io/github/contributors/tripathiji1312/learnbuddy.svg)](https://gitHub.com/tripathiji1312/learn_buddy/graphs/contributors/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

---

## ✨ Vision

In a world of diverse learning needs, one-size-fits-all education falls short. LearnBuddy was created to change that. We envision a future where every child, regardless of their physical, sensory, or cognitive abilities, has free access to a personal AI tutor that understands their pace, adapts to their style, and makes learning a joyful adventure.

This is a community-driven project. We believe that by working together, we can build a powerful, free alternative to commercial learning platforms.

## 🚀 Key Features

*   **🧠 Adaptive AI Engine**: A reinforcement learning model adapts question difficulty in real-time, ensuring every learner is perfectly challenged.
*   **🎮 Gamified Experience**: Learners earn XP, unlock achievements, and maintain "streaks," transforming learning into a motivating game.
*   **♿ Accessibility First**: Built from the ground up for universal access.
    *   **Interface**: High-contrast themes, adjustable text size, and dyslexia-friendly fonts.
    *   **Input**: Full keyboard navigation, voice command compatibility, and support for switch control devices.
    *   **Content**: Adjustable pacing, audio speed controls, and easy prompt repetition.
*   **🤖 NLP-Powered Evaluation**: Uses Sentence-Transformers to understand the semantic meaning of answers, allowing for flexible and intelligent grading.
*   **🛡️ Secure Admin Panel**: A comprehensive dashboard for platform management, user administration, and content curation.
*   **📦 Fully Containerized**: Easy to set up and deploy locally with Docker and Docker Compose.

---

## ❤️ Why Contribute?

Contributing to LearnBuddy means you're helping to build a more equitable and effective educational future. Whether you're a seasoned developer, a UX designer, an educator, or just starting your coding journey, your input is valuable.

*   **Make a Real-World Impact**: Your code will directly help children learn more effectively.
*   **Work with Modern Tech**: Get hands-on experience with FastAPI, PostgreSQL, AI/ML models, and Docker.
*   **Join a Welcoming Community**: We are committed to creating a supportive and collaborative environment.
*   **Build Your Portfolio**: Showcase your skills on a meaningful open-source project.

---

## 🚀 Getting Started

Follow these instructions to get the project up and running locally.

### Prerequisites

*   **Docker & Docker Compose**: [Install Docker Desktop](https://www.docker.com/products/docker-desktop).
*   **Git**: For cloning the repository.

### Installation & Setup

1.  **Fork & Clone the Repository**
    First, fork the project to your own GitHub account. Then, clone your fork locally:
    ```bash
    git clone https://github.com/YOUR-USERNAME/learnbuddy.git
    cd learnbuddy
    ```

2.  **Build and Run the Containers**
    This command will build the backend image and start the backend and database containers.
    ```bash
    docker-compose up --build -d
    ```

3.  **Seed the Database**
    This crucial step creates the database tables and populates them with sample data and the default admin user.
    ```bash
    docker-compose run --rm backend python scripts/seed_db.py
    ```
    You should see a "Database Seed Successful" message.

4.  **Start the Frontend**
    The easiest way to serve the frontend is with the **Live Server** extension in VS Code.
    *   Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension.
    *   Right-click on `index.html` and select **"Open with Live Server"**.
    *   Your browser will open to `http://127.0.0.1:5500`.

### Usage

*   **Learner App URL**: `http://127.0.0.1:5500/`
    *   **Test User**: `testuser` / `testpass`
*   **Admin Panel URL**: `http://127.0.0.1:5500/admin-login.html`
    *   **Admin User**: `admin` / `adminpassword`

---

## 🤝 How to Contribute

We welcome contributions of all kinds! Here’s how you can get started:

1.  **Join the Discussion**: Check out the [Issues tab](https://github.com/your-username/learnbuddy/issues) to find discussions, feature requests, and known bugs.
2.  **Pick an Issue**: Look for issues tagged with `good first issue` or `help wanted`.
3.  **Follow the Contribution Workflow**:
    *   Create a new branch for your feature (`git checkout -b feature/your-feature-name`).
    *   Make your changes.
    *   Commit your changes with a clear message (`git commit -m 'feat: Add your new feature'`).
    *   Push to your branch (`git push origin feature/your-feature-name`).
    *   Open a **Pull Request** back to the main repository.

Please read our `CONTRIBUTING.md` file for more detailed guidelines on our code of conduct and the process for submitting pull requests.

---

## 🗺️ Project Roadmap

We have big plans for LearnBuddy! Here's a look at what we're working on next. Contributions in these areas are highly encouraged!

*   [ ] **More Learning Modules**: Add new subjects like Reading Comprehension, Science, and History.
*   [ ] **Advanced Analytics**: Create detailed progress dashboards for parents and educators.
*   [ ] **"Study Buddies" Feature**: Implement collaborative challenges for learners.
*   [ ] **Internationalization (i18n)**: Translate the platform into multiple languages.
*   [ ] **Enhanced AI**: Evolve the recommendation engine to suggest new topics and identify learning gaps.
*   [ ] **CI/CD Pipeline**: Automate testing and deployment workflows.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.