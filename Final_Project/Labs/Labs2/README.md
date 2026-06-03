# Deep Learning for Cyber Security: Unsupervised Anomaly Detection via Autoencoders (AE)

## 1. Research & Project Overview
This laboratory project implements an advanced network intrusion detection system (NIDS) utilizing an unsupervised **Deep Learning Autoencoder (AE)** architecture. The system is built using the **Keras 3 API** running dynamically over a **PyTorch execution engine** backend. 

### The Cybersecurity Paradigm Shift: Unsupervised vs. Supervised
Traditional cybersecurity defense tools (like signature-based firewalls or supervised machine learning classifiers) suffer from a critical vulnerability: **they can only detect known attack patterns**. In modern cloud environments and web applications, malicious threat actors constantly deploy modified payloads or zero-day exploits. 

This pipeline leverages **Unsupervised Anomaly Detection** to bypass this limitation:
* **The Strategy:** The neural network is trained exclusively on safe, validated network behaviors (`is_attack == 0`). 
* **The Logic:** Instead of defining what an attack looks like, the AI constructs a dense mathematical model of what **"Normal System Behavior"** looks like. 
* **The Alert Mechanism:** When anomalous traffic flows through the trained bottleneck, the network fails to compress and reconstruct it properly, resulting in a spike in **Reconstruction Error (Mean Squared Error)** which triggers an automated security alert.

---

## 2. System Architecture & Bottleneck Mechanics

The core detection engine uses an hourglass-shaped configuration consisting of three distinct logical layers:

1. **The Encoder Subnetwork:** Ingests high-dimensional network telemetry features ($D_{\text{in}} = 41$) and compresses them through progressively narrower hidden layers utilizing non-linear `swish` activation functions.
2. **The Latent Bottleneck Space:** A hyper-compressed hidden layer ($D_{\text{latent}} = 10$). This layer forces the network to preserve only the most critical, foundational structural correlations of safe network packets.
3. **The Decoder Subnetwork:** Symmetrically expands the latent representation back to the original vector dimensions, attempting to output a clean clone of the input data.