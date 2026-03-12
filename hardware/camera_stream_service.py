#!/usr/bin/env python3
"""
Raspberry Pi 4 RTSP Streamer to MediaMTX

Streams both external and internal USB cameras reliably via RTSP/H264.

Requirements:
    sudo apt-get update
    sudo apt-get install -y ffmpeg v4l-utils

Usage:
    python3 pi_streamer.py start               # Start all cameras
    python3 pi_streamer.py start pi_cam_external   # Start specific camera
    python3 pi_streamer.py stop                # Stop all streams
    python3 pi_streamer.py status              # Show status

Environment Variables:
    MEDIAMTX_HOST - MediaMTX server IP/hostname (default: 69.62.125.223)
    MEDIAMTX_PORT - MediaMTX RTSP port (default: 8554)
    STREAM_KEY   - Stream key for authentication
"""
import os
import subprocess
import sys
import time
import signal

# ================= CONFIG =================
MEDIAMTX_HOST = os.environ.get("MEDIAMTX_HOST", "69.62.125.223")
MEDIAMTX_PORT = int(os.environ.get("MEDIAMTX_PORT", "8554"))
STREAM_KEY = os.environ.get("STREAM_KEY", "secret")

CAMERAS = {
    "pi_cam_external": {"device": "/dev/video0", "resolution": "640x480", "fps": 25},
    "pi_cam_internal": {"device": "/dev/video2", "resolution": "640x480", "fps": 25},
}

FFMPEG_PROCESSES = {}
# ==========================================


def get_rtsp_url(camera_id):
    if STREAM_KEY:
        return f"rtsp://{MEDIAMTX_HOST}:{MEDIAMTX_PORT}/{camera_id}?key={STREAM_KEY}"
    return f"rtsp://{MEDIAMTX_HOST}:{MEDIAMTX_PORT}/{camera_id}"


def check_camera(device):
    return os.path.exists(device)


def detect_camera_format(device):
    """
    Detects camera pixel format and returns "mjpeg" or "yuyv422" if available.
    """
    try:
        result = subprocess.run(
            ["v4l2-ctl", "--device", device, "--get-fmt-video"],
            capture_output=True,
            text=True,
            check=True,
        )
        stdout = result.stdout.lower()
        if "mjpeg" in stdout:
            return "mjpeg"
        elif "yuyv" in stdout:
            return "yuyv422"
    except Exception:
        pass
    return None


def start_stream(camera_id, config):
    if camera_id in FFMPEG_PROCESSES:
        proc = FFMPEG_PROCESSES[camera_id]
        if proc.poll() is None:
            print(f"[{camera_id}] already streaming")
            return

    device = config["device"]
    resolution = config["resolution"]
    fps = config["fps"]

    if not check_camera(device):
        print(f"[{camera_id}] camera not found: {device}")
        return

    camera_format = detect_camera_format(device)
    rtsp_url = get_rtsp_url(camera_id)

    print(f"[{camera_id}] starting stream -> {rtsp_url}")
    print(f"Device: {device}, Resolution: {resolution}@{fps}, Format: {camera_format or 'default'}")

    cmd = [
        "ffmpeg",
        "-loglevel", "error",
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-f", "v4l2",
        "-thread_queue_size", "4096",
    ]

    if camera_format:
        cmd += ["-input_format", camera_format]

    cmd += [
        "-framerate", str(fps),
        "-video_size", resolution,
        "-i", device,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-pix_fmt", "yuv420p",
        "-b:v", "1000k",
        "-maxrate", "1500k",
        "-bufsize", "2000k",
        "-g", str(fps * 2),
        "-keyint_min", str(fps),
        "-use_wallclock_as_timestamps", "1",
        "-flush_packets", "1",
        "-f", "rtsp",
        "-rtsp_transport", "tcp",
        rtsp_url,
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
        FFMPEG_PROCESSES[camera_id] = process
        print(f"[{camera_id}] started successfully (PID {process.pid})")
    except Exception as e:
        print(f"[{camera_id}] failed to start: {e}")


def stop_stream(camera_id):
    proc = FFMPEG_PROCESSES.get(camera_id)
    if not proc:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        print(f"[{camera_id}] stopped")
    except Exception:
        pass
    FFMPEG_PROCESSES.pop(camera_id, None)


def stop_all():
    for cam in list(FFMPEG_PROCESSES.keys()):
        stop_stream(cam)


def status():
    print("\n=========== CAMERA STATUS ===========\n")
    print(f"MediaMTX Server: {MEDIAMTX_HOST}:{MEDIAMTX_PORT}\n")
    for cam, cfg in CAMERAS.items():
        device = cfg["device"]
        proc = FFMPEG_PROCESSES.get(cam)
        s = "STREAMING" if proc and proc.poll() is None else "STOPPED"
        print(f"{cam}: {s}")
        print(f"  Device: {device} ({'OK' if check_camera(device) else 'MISSING'})")
        print(f"  URL: {get_rtsp_url(cam)}\n")
    print("====================================\n")


def monitor():
    while True:
        time.sleep(5)
        for cam, proc in list(FFMPEG_PROCESSES.items()):
            if proc.poll() is not None:
                print(f"[{cam}] stream crashed → restarting")
                start_stream(cam, CAMERAS[cam])


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop", "status", "restart"])
    parser.add_argument("camera", nargs="?")
    args = parser.parse_args()

    if args.action == "start":
        if args.camera:
            start_stream(args.camera, CAMERAS[args.camera])
        else:
            for cam, cfg in CAMERAS.items():
                start_stream(cam, cfg)
                time.sleep(1)
    elif args.action == "stop":
        if args.camera:
            stop_stream(args.camera)
        else:
            stop_all()
    elif args.action == "restart":
        stop_all()
        time.sleep(2)
        for cam, cfg in CAMERAS.items():
            start_stream(cam, cfg)
            time.sleep(1)
    elif args.action == "status":
        status()
        return

    monitor()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_all()