import os
import threading
from pathlib import Path
import concurrent.futures
import winreg

class SystemScanEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.results = {}
        self.targets = self._get_cleanup_targets()

    def _get_cleanup_targets(self):
        env = os.environ
        return {
            "Windows Temp Folder": r"C:\Windows\Temp",
            "User Temp Folder": env.get("TEMP"),
            "LocalAppData Temp": os.path.join(env.get("LOCALAPPDATA", ""), "Temp"),
            "Recycle Bin": r"C:\$Recycle.Bin",
            "Google Chrome Cache": os.path.join(env.get("LOCALAPPDATA", ""), r"Google\Chrome\User Data\Default\Cache"),
            "Microsoft Edge Cache": os.path.join(env.get("LOCALAPPDATA", ""), r"Microsoft\Edge\User Data\Default\Cache"),
            "Windows Prefetch": r"C:\Windows\Prefetch",
            "Thumbnail Cache": os.path.join(env.get("USERPROFILE", ""), r"AppData\Local\Microsoft\Windows\Explorer"),
            "Error Reporting Dumps": os.path.join(env.get("LOCALAPPDATA", ""), "CrashDumps"),
            "Windows Update Cache": r"C:\Windows\SoftwareDistribution\Download"
        }

    def run_scan(self):
        # Use a thread pool to scan directories
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            future_to_label = {
                executor.submit(self._scan_directory, label, path): label
                for label, path in self.targets.items() if path and os.path.exists(path)
            }

            for future in concurrent.futures.as_completed(future_to_label):
                label = future_to_label[future]
                try:
                    file_count, total_size = future.result()
                    if total_size > 0:
                        with self.lock:
                            self.results[label] = {
                                "path": self.targets[label],
                                "file_count": file_count,
                                "size_bytes": total_size,
                                "size_human": self._human_readable_size(total_size)
                            }
                except Exception as e:
                    print(f"[Error] Scanning {label}: {e}")

        # Add registry junk scan
        reg_count, reg_size, reg_entries = self._scan_registry_for_junk()
        if reg_count > 0:
            self.results["Registry Junk"] = {
                "path": "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
                "file_count": reg_count,
                "size_bytes": reg_size,
                "size_human": self._human_readable_size(reg_size),
                "details": reg_entries
            }

        return self.results

    def _scan_directory(self, label, path):
        total_size = 0
        file_count = 0
        seen_paths = set()

        for root, dirs, files in os.walk(path, topdown=True):
            if root in seen_paths:
                continue
            seen_paths.add(root)

            for f in files:
                try:
                    file_path = os.path.join(root, f)
                    if not os.path.isfile(file_path):
                        continue
                    size = os.path.getsize(file_path)
                    total_size += size
                    file_count += 1
                except (PermissionError, FileNotFoundError):
                    continue
                except Exception as e:
                    print(f"[Error] File access: {file_path} -> {e}")

        return file_count, total_size

    def _scan_registry_for_junk(self):
        """
        Scans user uninstall keys for orphaned or broken entries.
        """
        junk_entries = []
        size_estimate = 0

        uninstall_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, uninstall_path) as base_key:
                for i in range(winreg.QueryInfoKey(base_key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(base_key, i)
                        with winreg.OpenKey(base_key, subkey_name) as subkey:
                            try:
                                display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            except FileNotFoundError:
                                display_name = f"Unnamed Key {subkey_name}"

                            try:
                                install_location, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                if install_location and not os.path.exists(install_location):
                                    junk_entries.append(f"{display_name} → Missing path: {install_location}")
                                    size_estimate += 2048  # Simulated size
                            except FileNotFoundError:
                                continue
                    except OSError:
                        continue
        except Exception as e:
            print(f"[Registry Scan Error] {e}")

        return len(junk_entries), size_estimate, junk_entries

    def _human_readable_size(self, size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024
        return f"{size:.{decimal_places}f} PB"
