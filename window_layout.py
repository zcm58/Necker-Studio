"""Place operator windows inside the active monitor's usable desktop."""
import sys


def window_geometry(width, height, work_area, center=None):
    left, top, right, bottom = work_area
    # Reserve margins plus the native border, title bar and menu.
    mx, my, dw, dh = 32, 32, 20, 72
    width = min(width, max(1, right - left - 2 * mx - dw))
    height = min(height, max(1, bottom - top - 2 * my - dh))
    cx, cy = center or ((left + right) / 2, (top + bottom) / 2)
    x = min(max(round(cx - (width + dw) / 2), left + mx), right - mx - width - dw)
    y = min(max(round(cy - (height + dh) / 2), top + my), bottom - my - height - dh)
    return width, height, x, y


def work_area(window):
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes

        class MonitorInfo(ctypes.Structure):
            _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', wintypes.RECT),
                        ('rcWork', wintypes.RECT), ('dwFlags', wintypes.DWORD)]

        user32 = ctypes.WinDLL('user32', use_last_error=True)
        user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
        user32.MonitorFromWindow.restype = wintypes.HANDLE
        user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
        user32.GetMonitorInfoW.restype = wintypes.BOOL
        parent = getattr(window, 'master', None)
        owner = parent.winfo_toplevel() if parent is not None else window
        owner.update_idletasks()
        monitor = user32.MonitorFromWindow(owner.winfo_id(), 2)
        info = MonitorInfo(cbSize=ctypes.sizeof(MonitorInfo))
        if user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            rect = info.rcWork
            return rect.left, rect.top, rect.right, rect.bottom
    return 0, 0, window.winfo_screenwidth(), window.winfo_screenheight()


def fit_window(window, width, height):
    area = work_area(window)
    parent = getattr(window, 'master', None)
    center = None
    if parent is not None:
        parent = parent.winfo_toplevel()
        center = (parent.winfo_rootx() + parent.winfo_width() / 2,
                  parent.winfo_rooty() + parent.winfo_height() / 2)
    width, height, x, y = window_geometry(width, height, area, center)
    window.geometry(f'{width}x{height}+{x}+{y}')
    window.minsize(min(680, width), min(470, height))
