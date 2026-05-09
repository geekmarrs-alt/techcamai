# TECHCAMAI: Edge-First AI Surveillance

TECHCAMAI is a professional-grade, edge-first AI camera monitoring platform designed for security operators. It runs locally on your network—typically on a Raspberry Pi—processing camera streams on-site to provide real-time alerts with immediate video evidence.

## Key Features

- **Local-First Processing**: No cloud dependency for the core monitoring loop. Your data stays on your network.
- **AI-Powered Detection**: Sophisticated motion and object detection tailored for security workflows.
- **Operator Console**: A high-performance dashboard designed specifically for active security monitoring and rapid alert triage.
- **Evidence-Forward**: Every alert is accompanied by a video clip, allowing operators to immediately verify incidents.
- **Easy Deployment**: Simplified setup using Docker Compose, optimized for Raspberry Pi and similar edge devices.

---

## Quick Start (Docker)

To get TECHCAMAI running on your local network:

1. **Install Docker and Docker Compose** on your host machine (e.g., Raspberry Pi 4/5, Ubuntu Server).
2. **Clone this repository** (Access restricted to authorized users).
3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env to set your SECRET_KEY and optional TECHCAMAI_LICENSE_KEY
   ```
4. **Launch the Stack**:
   ```bash
   docker compose up -d
   ```
5. **Access the Dashboard**: Open `http://<your-ip>:8000` in your browser.

---

## Hardware Requirements

- **Minimum**: Raspberry Pi 4 (4GB) or equivalent.
- **Recommended**: Raspberry Pi 5 (8GB) for multiple high-resolution streams.
- **Storage**: High-endurance microSD card or external SSD for video clip retention.

---

## Licensing

TECHCAMAI is proprietary software.

- **Developer Preview (Community)**: Free for evaluation and small-scale use (up to 4 cameras).
- **Operator Pro**: Unlocks unlimited cameras, email/webhook notifications, and advanced rule scheduling.
- **Enterprise**: Multi-site fleet management and dedicated support.

Use of this software is subject to the terms in the `LICENSE` file. Unauthorized distribution or resale is strictly prohibited.

---

## Support & Contact

- **Documentation**: See the `/docs` directory for technical deep-dives.
- **Issues**: Report bugs via the GitHub Issues tab.
- **Commercial Inquiries**: Email `support@techcamai.com` for licensing and enterprise fleet deployments.

---

**Proprietary Software — All Rights Reserved © 2026 TECHCAMAI**
