"""
Updater - checks GitHub Releases and updates a git checkout to the latest tag.

No UI imports: the GUI talks to this module through the Qt signals of the
worker classes below.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from packaging.version import InvalidVersion, Version
from PySide6.QtCore import QThread, Signal

from mfdp_app.version import GITHUB_REPO, __version__

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases"
_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)  # Windows: no console flash


class UpdateError(Exception):
    """User-presentable failure (message is shown as-is)."""


@dataclass
class ReleaseInfo:
    tag: str
    url: str
    notes: str


def _parse(tag: str) -> Optional[Version]:
    try:
        return Version(tag.lstrip("vV"))
    except InvalidVersion:
        return None


def is_newer(latest_tag: str, current: str = __version__) -> bool:
    latest, cur = _parse(latest_tag), _parse(current)
    return latest is not None and cur is not None and latest > cur


def check_latest_release(timeout: int = 8) -> Optional[ReleaseInfo]:
    """Return the latest published release, or None if there is none yet."""
    req = urllib.request.Request(_API_URL, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": f"mfdp/{__version__}",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code in (403, 429):
            raise UpdateError("GitHub istek limiti aşıldı, daha sonra tekrar deneyin.")
        raise UpdateError(f"GitHub hatası: {e.code}")
    except (urllib.error.URLError, TimeoutError, OSError):
        raise UpdateError("GitHub'a bağlanılamadı. İnternet bağlantınızı kontrol edin.")
    except ValueError:
        raise UpdateError("GitHub'dan geçersiz yanıt alındı.")

    tag = data.get("tag_name")
    if not tag:
        return None
    return ReleaseInfo(tag=tag, url=data.get("html_url") or RELEASES_URL,
                       notes=(data.get("body") or "").strip())


def _git(*args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", *args], cwd=PROJECT_ROOT, capture_output=True,
                              text=True, timeout=timeout, creationflags=_NO_WINDOW)
    except FileNotFoundError:
        raise UpdateError("Git bulunamadı.")
    except subprocess.TimeoutExpired:
        raise UpdateError("Git işlemi zaman aşımına uğradı.")


def can_self_update() -> Optional[str]:
    """Return None if in-app update is possible, else the reason why not."""
    if not os.path.exists(os.path.join(PROJECT_ROOT, ".git")):  # .git is a file in worktrees
        return "Bu kurulum git deposu değil."
    if _git("status", "--porcelain", "--untracked-files=no").stdout.strip():
        return "Yerel değişiklikleriniz var; üzerine yazmamak için güncelleme yapılmadı."
    return None


def apply_update(tag: str) -> None:
    """Fast-forward the checkout to `tag`; reinstall requirements if they changed."""
    reason = can_self_update()
    if reason:
        raise UpdateError(reason)

    old_head = _git("rev-parse", "HEAD").stdout.strip()
    fetch = _git("fetch", "--tags", "origin")
    if fetch.returncode != 0:
        raise UpdateError(f"git fetch başarısız:\n{fetch.stderr.strip()}")
    merge = _git("merge", "--ff-only", f"refs/tags/{tag}")
    if merge.returncode != 0:
        raise UpdateError("Güncelleme otomatik uygulanamadı (yerel geçmiş farklı).\n"
                          f"{merge.stderr.strip()}")

    changed = _git("diff", "--name-only", old_head, "HEAD", "--", "requirements.txt")
    if changed.stdout.strip():
        pip = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                             cwd=PROJECT_ROOT, capture_output=True, text=True,
                             creationflags=_NO_WINDOW)
        if pip.returncode != 0:
            raise UpdateError("Kod güncellendi ancak bağımlılıklar yüklenemedi:\n"
                              f"{pip.stderr.strip()[-400:]}")


def restart_app() -> None:
    subprocess.Popen([sys.executable, "-m", "mfdp_app.main"], cwd=PROJECT_ROOT,
                     creationflags=_NO_WINDOW)


class CheckWorker(QThread):
    result = Signal(object)   # ReleaseInfo or None
    failed = Signal(str)

    def run(self):
        try:
            self.result.emit(check_latest_release())
        except UpdateError as e:
            self.failed.emit(str(e))


class ApplyWorker(QThread):
    done = Signal()
    failed = Signal(str)

    def __init__(self, tag: str, parent=None):
        super().__init__(parent)
        self._tag = tag

    def run(self):
        try:
            apply_update(self._tag)
            self.done.emit()
        except UpdateError as e:
            self.failed.emit(str(e))
