# TikTok StreamKey Generator for OBS Studio

![Version: 2.0.7](https://img.shields.io/badge/version-3.0.0-blue.svg)   ![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)

> Effortlessly grab a TikTok Live stream key via your Streamlabs login, ready to use with OBS Studio — with or without 1k+ followers!

## Description
This modern, cross-platform GUI tool lets you generate a TikTok Live Stream Key using the official Streamlabs API. It’s tailored for creators who have Streamlabs TikTok LIVE access and want an easy, all-in-one workflow with no command-line hassles.

- **No 1k follower requirement on TikTok** — apply for access through Streamlabs and go live with any account that’s approved
- **100% free software**; you can build, inspect, or modify the source under the GNU GPL v3

---

## Features
- Secure stream key and RTMP URL retrieval for TikTok LIVE (via Streamlabs)
- Easy Windows installer or one-file build
- Sleek, dark modern GUI (PySide6 based)
- Token loader: fetch from your PC (if logged into Streamlabs) or in-browser TikTok login
- Account info checker & stream title/category setup
- Game category search/suggestions
- Stream key copy-to-clipboard for worry-free OBS setup
- Save/load configuration (title/game/audience/token) in one click
- "Go Live" and "End Live" button control
- Optional mature content flag
- Open-source & privacy-respecting

---

## Prerequisites
- **Streamlabs TikTok LIVE access** ([request here](https://tiktok.com/falcon/live_g/live_access_pc_apply/result/index.html?id=GL6399433079641606942&lang=en-US))
- TikTok account
- Windows 10/11 (64-bit recommended)
- [Optional] Streamlabs Desktop installed, logged in with your TikTok account *for easiest token retrieval*.

> **You do NOT need 1,000 TikTok followers!** Streamlabs grants access based on their own approval process.

---

## Installation / Running

### Download ready-to-use EXE
Get the latest release [here](../../releases/latest) and simply run it. **No Python installation required.**

### Run from source (for development)
1. Clone this repo:
    ```bash
    git clone https://github.com/Adivise/TikTokStreamKey.git
    cd TikTokStreamKey
    ```
2. [Optional but recommended] Create and activate a virtual environment:
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
3. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
4. Run:
    ```bash
    python app.py
    ```
---

## Usage
1. Run the application.
2. Click **"Load from PC"** if you have Streamlabs Desktop and are logged in; otherwise, use **"Load from Web"** to log in via browser.
3. Once a token loads (top left), confirm your TikTok username and account info populate below.
4. Enter a stream title and search/select a game category. Optionally flag for mature content.
5. Click **"Go Live"**.
6. Copy the **Stream URL** and **Stream Key**, and use in OBS Studio (or other RTMP software).
7. To end the stream, click **"End Live"**.

- All configs (token/title/category/audience) can be saved/reloaded.
- Use the **Copy** buttons for fast paste into OBS.

---

## Build Guide (Windows)
See [BUILD.md](BUILD.md) for full details. Quick start:

- Activate virtualenv, install requirements, then run:
    ```bash
    python -m nuitka --standalone --onefile --windows-icon-from-ico=streamkey.ico --enable-plugin=pyside6 --output-dir=dist app.py
    ```
- The built EXE will be in the `dist` folder.
- Troubleshoot common build issues via [REQUIREMENTS_GUIDE.md](Guides/REQUIREMENTS_GUIDE.md) and [BUILD_TROUBLESHOOTING.md](Guides/BUILD_TROUBLESHOOTING.md).

---

## Screenshots

If you want a preview of the app, here it is:

![App Screenshot](https://media.discordapp.net/attachments/1432797361574248480/1448530401558659072/image.png?ex=693b9890&is=693a4710&hm=b6c7ca669e8b712019571f3a939e9cbc2ff4545788b71cc0e2dbfa3bb0b7dda4&=&format=webp&quality=lossless)

---

## FAQ
- **Do I need Streamlabs Desktop?**  
  *No, but it makes token loading automatic! Otherwise, log in through your browser inside the app.*
- **Does it work on Mac or Linux?**  
  *The EXE is Windows-only, but source runs cross-platform (token auto-load only works on supported platforms).* 
- **Do I need 1k TikTok followers?**
  *No, Streamlabs grants access on their own terms — see above link to request.*
- **I get 'Maximum number of attempts reached' or Selenium errors?**
  *See FAQ in this README for manual cookie loading.*

For more, check the full FAQ below.

---

## Donation & Credits

If you find this tool helpful, please consider supporting development:

- Original Author: **[loukious](https://github.com/loukious)** [Support Original](https://buymeacoffee.com/loukious)
- Maintainer: **[Adivise](https://github.com/Adivise)** [Support Maintainer](https://buymeacoffee.com/suntury)

---

## License
This project is licensed under the **GNU General Public License v3.0**. See [LICENSE.txt](LICENSE) for more details.
