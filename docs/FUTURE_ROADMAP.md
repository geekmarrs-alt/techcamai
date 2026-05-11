# TECHCAMAI: Future Roadmap & Major Feature Suggestions

Following the full system assessment and rebuild, the core infrastructure is now stable. To transition from an MVP to a market-leading AI CCTV system, I recommend the following feature additions:

## 1. Edge AI Inference (YOLO/TensorRT)
*   **Goal:** Replace the current motion-digest fallback with real-time object detection.
*   **Details:** Integrate `ultralytics` YOLOv8 or YOLOv11. For the Raspberry Pi 5 / Windows target, use TensorRT or OpenVINO to ensure 15+ FPS detection without high CPU latency.
*   **Impact:** Eliminate false positives from wind, shadows, or light changes.

## 2. Face Recognition & LPR (License Plate Recognition)
*   **Goal:** Add identity-based alerting.
*   **Details:** Implement a local vector database (like Milvus or ChromaDB) to store face encodings. Alert when "Unknown" faces are detected in high-security zones.
*   **Impact:** Turn the system into an access control monitor.

## 3. Two-Way Audio Integration
*   **Goal:** Allow operators to talk back through cameras.
*   **Details:** Implement WebRTC for low-latency audio streaming from the Browser -> API -> Camera (via ONVIF/ISAPI).
*   **Impact:** Deter intruders in real-time.

## 4. Multi-Node "Mesh" Worker Support
*   **Goal:** Scale to 50+ cameras.
*   **Details:** Update the API to manage multiple Workers across different physical locations. Workers should "check in" to the central API to receive assignments.
*   **Impact:** Supports commercial/industrial deployments.

## 5. Cloud/Mobile Push Notifications
*   **Goal:** Untether the operator from the desktop.
*   **Details:** Integrate Firebase Cloud Messaging (FCM) or Gotify for instant mobile alerts with snapshot previews.
*   **Impact:** Essential for home security use cases.

## 6. Advanced Wi-Fi Triangulation
*   **Goal:** Improve "Blind Spot" monitoring.
*   **Details:** Use the current Wi-Fi tracking foundation to correlate signal strength (RSSI) from multiple ESP32/Pi nodes to plot XY coordinates of devices on a floor plan.
*   **Impact:** Track movement even where cameras can't see.
