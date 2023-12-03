def url_to_filename(url: str):
    if url.startswith("https://x.com/") or url.startswith("https://twitter.com/"):
        url = url.split("?")[0]
        vid_id = url.split("/")[-1]
        vid_name = f"{vid_id}.mp4"
    elif url.startswith("https://www.instagram.com/reel/"):
        url = url.split("?")[0]
        vid_id = url.split("/")[-2]
        vid_name = f"{vid_id}.mp4"
    elif url.startswith("https://instagram.com/"):
        url = url.split("?")[0]
        vid_id = url.split("/")[-1]
        vid_name = f"{vid_id}.mp4"
    else:
        print(f"This is not a known link! {url}")
        vid_name = "ERROR.mp4"
    return f"videos/{vid_name}"
