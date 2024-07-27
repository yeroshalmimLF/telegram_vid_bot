import subprocess


def url_to_filename(url: str):
    if url.startswith("https://x.com/") or url.startswith("https://twitter.com/"):
        url = url.split("?")[0]
        vid_id = url.split("/")[-1]
        vid_name = f"{vid_id}.mp4"
    elif url.startswith("https://www.instagram.com/reel/"):
        url = url.split("?")[0]
        vid_id = url.split("/")[-2]
        vid_name = f"{vid_id}.mp4"
    elif url.startswith("https://instagram.com/") or url.startswith("https://www.instagram.com/"):
        url = url.split("?")[0]
        vid_id = url.split("/")[-1]
        vid_name = f"{vid_id}.mp4"
    elif url.startswith("https://www.reddit.com"):
        url = url.split("?")[0]
        vid_id = [_ for _ in url.split("/") if _][-1]
        vid_name = f"{vid_id}.mp4"
    else:
        print(f"This is not a known link! {url}")
        vid_name = "ERROR.mp4"
    return f"videos/{vid_name}"


def filename_enumerated(vid_name: str, i: int):
    """
    vid_name: str example: "videos/1234567890.mp4"
    i: int example: 1

    returns: str example: "videos/1234567890_1.mp4"
    """
    vid_name_without_ext = vid_name[:-4]
    return f"{vid_name_without_ext}_{i}.mp4"


def get_vid_size(vid_name: str):
    resp = None
    try:
        resp = subprocess.run(
            f"ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x  {vid_name}",
            shell=True,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        return None, None
    resp = f"{resp.stdout.decode()}"
    if "x" not in resp:
        return None, None
    width, height = resp.split("x")
    return width, height


def convert_gif_to_mp4(gif_path: str, mp4_path: str):
    if not mp4_path:
        mp4_path = gif_path.replace(".gif", ".mp4")
    subprocess.run(
        f'ffmpeg -i {gif_path} -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" {mp4_path} -y',
        shell=True,
    )
    return mp4_path
