# GAPK Tool
A lightweight, interactive Python wrapper around the official [apkeep](https://github.com/efforg/apkeep) Docker image.
This tool streamlines the process of generating Google Play AAS tokens and downloading `APKs` directly to your local machine.

---

## Introduction

GAPK Tool is designed for security analysts, penetration testers, or any professional who needs to obtain APKs from the Google Play Store in an automated, reproducible manner. It uses the official [apkeep](https://github.com/efforg/apkeep) under the hood and provides three simple commands:

* **`configure`**: Save your Google account email & AAS token.
* **`generate`**: Generate a fresh AAS token by passing an OAuth token to the Docker image.
* **`download`**: Download any Play Store APK by application ID or URL.

---

## Prerequisites

Before you begin, ensure the following are in place:

1. **Administrative Privileges**
   You will need `sudo` or Administrator access for Docker installation and running the `docker` commands in certain scenarios.

2. **Python 3.8+**
   This script has been tested on Python 3.8 and above. Verify by running:

   ```
   python3 --version
   ```

3. **Git (optional but recommended)**
   If you plan to clone the repository:

   ```
   git --version
   ```

   If Git is not installed, see [Cloning or Downloading the Repository](#cloning-or-downloading-the-repository) below.

4. **Stable Internet Connection**
   Both Docker image pulls and actual APK downloads require reliable connectivity.

> **Opinion**: *You must install Docker through official channels only. Using untrusted package sources risks system integrity.*

---

## Cloning or Downloading the Repository

> **Opinion**: Cloning via `git` ensures you receive future updates effortlessly. Only download a zip/tarball if you have restrictions on using Git.

1. **Clone with Git**

   ```bash
   git clone https://github.com/JuSTinMrp/GAPK.git
   cd GAPK
   ```

2. **Alternatively, Download as ZIP**

   * Navigate to the repository’s main page in your web browser.
   * Click **“Code” → “Download ZIP”**.
   * Unzip and `cd` into the extracted folder:

     ```bash
     unzip apkeep-automation-master.zip
     cd GAPK
     ```

3. **Ensure `main.py` is Executable**

   ```bash
   chmod +x main.py
   ```

---

## Basic Command Structure

   ```
   ./main.py <command>
   ```

   * If you omit `./`, you can also run:

     ```
     python3 main.py <command>
     ```

   * **Commands**:

     * `configure` – interactively save your email & AAS token.
     * `generate` – interactively generate an AAS token (requires OAuth token).
     * `download` – download an APK (requires prior configuration).

## Download Options:

To download directly from the Google Play Store, first you'll have to obtain an OAuth token by visiting the Google [embedded setup page](https://accounts.google.com/EmbeddedSetup) and:

- Opening the browser debugging console on `Network` tab
- Logging in
- If the "Google Terms of Services" pop up, click `I agree` (it can hang up on this step but it's not important)
- Select the last request from `accounts.google.com` in the `Network` tab
- Select the `Cookies` tab of this request
- One of the response cookie is `oauth_token`
- Copy the `value` field (it must start with `oauth2_4/`)
<br>

  1. `Enter Play Store URL or application ID (e.g. com.facebook.katana):`

     * **Option A**: Raw package name: `com.whatsapp`
     * **Option B**: Full Play Store link:

       ```
       https://play.google.com/store/apps/details?id=com.whatsapp&hl=en
       ```
     * The script will automatically extract `id=com.whatsapp` if you supply a URL.

---

> **NOTE**: This tool must be treated as a **professional pentesting utility**. Do **not** share your AAS or OAuth tokens, and always abide by Google’s terms of service. **USE TEST ACCOUNTS FOR THIS PURPOSE**.