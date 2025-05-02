# 🧹 PyCleaner - Windows Cleaning Utility

PyCleaner is a lightweight and user-friendly utility built with Python for scanning and cleaning up unnecessary files and orphaned registry entries on Windows systems. It helps users reclaim disk space and remove clutter from various system directories and browser caches.

---

## 🚀 Features

- ✅ Scans common junk locations: Temp folders, Recycle Bin, browser caches, crash dumps, and more.
- 🔍 Detects orphaned registry entries from uninstalled applications.
- 📊 Displays detailed scan results including file count and total size.
- ☑️ Allows users to select specific targets before cleaning.
- 🧼 Deletes selected files and registry keys with one click.
- 💡 Modern dark-themed GUI with progress feedback.

---

## 🖥️ Requirements

- Python 3.8+
- Windows OS
- Required packages:
  - `tkinter` (comes with standard Python on Windows)
  - No external dependencies

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/pycleaner.git
cd pycleaner
python main.py
```

---

## 📁 Project Structure

```plaintext
pycleaner/
├── main.py                      # Entry point of the application
├── src/
│   ├── gui.py                  # GUI components and interactions
│   ├── Delete.py              # Handles deletion logic (files & registry)
│   ├── SystemScanEngine.py    # Scanning engine for files and registry junk
```

---

## 🛠️ Usage

1. **Start the App**  
   Run `main.py` to launch the GUI.

2. **Select Scan Targets**  
   Check or uncheck directories you want to include in the scan.

3. **Run the Scan**  
   Click "🔍 Start Scan" and wait for results.

4. **Review Results**  
   Select which detected junk items you wish to delete.

5. **Clean Up**  
   Click "🧼 Delete Selected Items" to permanently remove the selected items.

---

## 🧠 How It Works

### `SystemScanEngine.py`
- Scans various system folders for temporary files.
- Looks for registry entries under:
  ```
  HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall
  ```
  and flags entries pointing to missing paths.

### `Delete.py`
- Deletes files and directories safely, checking permissions.
- Deletes orphaned registry keys identified by the scan.
- Tracks and reports total space freed and registry keys removed.

### `gui.py`
- Renders the GUI using `tkinter` and `ttk` with a custom dark theme.
- Provides checkboxes, buttons, status messages, and scan results.
- Runs scanning and cleanup in background threads to avoid freezing the UI.

---

## ⚠️ Disclaimer

This tool deletes files and registry keys permanently. While it targets only junk files and invalid registry entries, use with caution and at your own risk.

---

## 📄 License

[MIT License](LICENSE)

---

## 🙋‍♂️ Contribution

Contributions are welcome! Open an issue or submit a pull request.
