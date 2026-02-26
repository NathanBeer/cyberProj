# 📱 QR Code Phishing Attack Analysis (MITRE ATT&CK Mapping)

This document analyzes a **QR code phishing campaign** and maps its behavior to the **MITRE ATT&CK framework**.
The attack shifts user interaction from desktop email environments to mobile devices, helping bypass traditional security controls.

---

## 1️⃣ Initial Access (TA0001)

### 🔹 Technique: T1566.002 – Phishing: Spearphishing Link

**Behavior:**

* Attackers embed malicious URLs inside QR codes.
* Victims scan the QR code using their mobile device.
* The scan redirects the victim to a phishing website designed to harvest credentials.

---

### 🔹 Technique: T1660 – Phishing via QR Code (Mobile Phishing)

**Behavior:**

* QR codes are used to bypass traditional email security scanning.
* The phishing interaction shifts from:

  * **Desktop** (email client)
  * ➜ **Mobile device** (QR scan)
* Security tools may not inspect the embedded QR destination URL before user interaction.

---

## 2️⃣ Execution (TA0002)

### 🔹 Technique: T1204.001 – User Execution: Malicious Link

**Behavior:**

* The attack requires explicit user interaction (scanning and tapping).
* The victim manually initiates the connection to the malicious site.
* In some cases, QR codes trigger deep links that open specific mobile apps.

---

## 3️⃣ Defense Evasion (TA0005)

### 🔹 Technique: T1027 – Obfuscated Files or Information

**Behavior:**

* Use of URL shorteners to conceal final malicious domains.
* Multi-step redirection chains to hide infrastructure.
* QR code encoding itself hides the visible URL from the user.

---

## 4️⃣ Credential Access (TA0006)

### 🔹 Technique: T1056.003 – Input Capture: Web Portal Capture

**Behavior:**

* Fake login pages mimic legitimate services (e.g., cloud or enterprise portals).
* Victims enter usernames and passwords into phishing forms.
* Stolen credentials are transmitted to attacker-controlled servers.

---

### 🔹 Technique: T1556 – Modify Authentication Process (MFA Bypass)

**Behavior:**

* Some phishing campaigns proxy authentication in real time.
* Attackers capture:

  * Session cookies
  * MFA tokens
* Enables account takeover even when MFA is enabled.

---

## 5️⃣ Command and Control (TA0011)

### 🔹 Technique: T1071.001 – Application Layer Protocol: Web Protocols

**Behavior:**

* Phishing pages communicate with attacker infrastructure over HTTP/HTTPS.
* Credential submissions are transmitted via encrypted web traffic.
* Redirect chains rely on standard web protocols to blend into normal traffic.

---

## 🔎 Key Takeaways

* QR code phishing (also called **"Quishing"**) is designed to evade traditional email security solutions.
* The attack relies heavily on **user interaction**.
* Mobile devices introduce visibility gaps in many enterprise security stacks.
* MFA alone is not sufficient protection when adversaries use real-time proxy phishing.

