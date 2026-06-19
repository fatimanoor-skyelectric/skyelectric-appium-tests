# SkyElectric Mobile App — Appium Test Suite

Automated UI tests for the SkyElectric Android app using **Appium + Python + pytest**.

---

## Project Structure

```
skyelectric-appium-tests/
│
├── pages/                          # Page Object Model (POM) layer
│   ├── login_page.py               # Login screen interactions & OTP flow
│   └── navigation_page.py          # Bottom nav, logout, screen transitions
│
├── tests/                          # All test modules
│   ├── test_login.py               # Login validation (empty/invalid email, OTP, full flow)
│   ├── test_power_distribution.py  # Power Distribution screen tests
│   ├── test_navigation.py          # Navigation between screens
│   ├── test_solar_production.py    # Solar production screen tests
│   ├── test_grid_interaction.py    # Grid interaction screen tests
│   ├── test_battery_management.py  # Battery management screen tests
│   ├── test_menu_option.py         # Menu/settings option tests
│   ├── test_logout.py              # Logout flow tests
│   └── test_end_to_end.py          # End-to-end workflow tests (10 steps)
│
├── utils/
│   └── gmail_helper.py             # OTP extraction from Gmail inbox
│
├── conftest.py                     # Pytest fixtures, Appium session, state machine
├── config.py                       # App package, activity, and shared constants
├── app-skyelectric-production.apk  # Android APK under test
├── view.xml                        # UI dump reference (for locator debugging)
├── screen.png                      # Screen reference screenshot
└── .gitignore
```

---

## Prerequisites

| Tool | Notes |
|---|---|
| Python 3.x + venv | For running tests |
| Appium 2.x | `npm install -g appium` |
| UiAutomator2 driver | `appium driver install uiautomator2` |
| Android SDK / ADB | Must be on PATH |
| Android Emulator | `Pixel6_API34` AVD (or your own) |
| Gmail access | For OTP retrieval via `gmail_helper` |

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/fatimanoor-skyelectric/skyelectric-appium-tests.git
cd skyelectric-appium-tests

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt   # (or: pip install pytest appium-python-client pytest-html)
```

---

## Starting the Environment

Run these steps **in order** before executing any tests:

### 1. Start the Emulator

```bash
# List available AVDs
emulator -list-avds

# Launch the Pixel 6 emulator (recommended flags)
emulator -avd Pixel6_API34 -no-snapshot-load -no-boot-anim -gpu swiftshader_indirect -no-snapshot-save
```

### 2. Start the Appium Server

```bash
appium
```

### 3. Verify ADB Connection

```bash
adb kill-server
adb start-server
adb devices
# Expected output:
# emulator-5554   device
```

---
### Create a virtual device using Terminal command
avdmanager create avd -n Pixel_5 \
-k "system-images;android-34;google_apis;x86_64" \
-d "pixel_5"


## Running Tests

Always activate the virtual environment first:

```bash
source venv/bin/activate
```

### Run individual test cases

```bash
pytest tests/test_login.py::TestLogin::test_empty_email_shows_error -v -s
pytest tests/test_login.py::TestLogin::test_invalid_email_shows_error -v -s
pytest tests/test_login.py::TestLogin::test_wrong_otp_shows_error -v -s
```

### Run a full test module

```bash
pytest tests/test_login.py -v -s
```

### Run all tests

```bash
pytest -vs tests/test_*.py
```

### Run end-to-end tests

```bash
# All 10 E2E steps
pytest tests/test_end_to_end.py -v

# E2E tests only (by marker)
pytest -m e2e -v
```

---

## Generating Reports

```bash
# Full HTML report (self-contained, with screenshots on failure)
pytest -vs tests/ --html=reports/report.html --self-contained-html

# E2E report separately
pytest tests/test_end_to_end.py -v --html=reports/e2e_report.html
```

Reports are saved to the `reports/` directory. Failure screenshots are automatically captured under `reports/screenshots/`.

---

## Debugging & Utilities

### Find UI element locators (XML dump)

```bash
adb shell uiautomator dump /sdcard/ui_dump.xml && adb shell cat /sdcard/ui_dump.xml
```

### Tap a screen coordinate

```bash
adb shell input tap 540 1378
```

### Type text into a field

```bash
adb shell input text "fatimanoor@skyelectric.com"
```

### Check crash logs

```bash
adb logcat | grep -i uiautomator
adb logcat | grep -i crash
```

---

## Architecture Notes

### State Machine (`conftest.py`)

The test suite uses a smart state machine to handle the app's current screen before each test:

| State | Description | Action taken |
|---|---|---|
| `LOGIN` | Login / OTP screen | Performs full OTP login via Gmail |
| `PIN` | Security lock / biometric prompt | Enters PIN / dismisses lock |
| `POWER` | Power Distribution screen (main) | Already ready — no action needed |
| `UNKNOWN` | Transient / crash / loading | Restarts app and retries (max 2x) |

### Fixtures

| Fixture | Scope | Use when… |
|---|---|---|
| `driver` | session | Raw Appium driver (shared across all tests) |
| `logged_in_driver` | function | Test needs to be on the Power Distribution screen |
| `login_screen_driver` | function | Negative login tests (restarts app for clean state) |
| `navigation_page` | function | Test needs to navigate between screens |

### Page Objects

- **`LoginPage`** — email field, OTP entry, login button, PIN handling
- **`NavigationPage`** — bottom nav bar, logout, screen transitions

### Gmail OTP Helper

`utils/gmail_helper.py` fetches the OTP automatically from the inbox filtered by sender (`skyelectric`) and subject (`OTP`), waiting up to 90 seconds.

---

## Test Execution Order

Tests are sorted automatically by `conftest.py`:

1. `test_login` — negative tests first, then full login flow
2. `test_power_distribution`
3. `test_navigation`
4. `test_solar_production`
5. `test_grid_interaction`
6. `test_battery_management`
7. `test_menu_option`
8. `test_logout`

---

## Configuration

Key settings live in `config.py`:

```python
APP_PACKAGE  = "com.skyelectric.app"   # Android package name
APP_ACTIVITY = ".MainActivity"          # Launch activity
```

ADB path and test credentials are set at the top of `conftest.py`:

```python
ADB        = "/home/fatima/android-sdk/platform-tools/adb"
TEST_EMAIL = "fatimanoor@skyelectric.com"
```
