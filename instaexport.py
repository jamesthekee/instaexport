import json
from pathlib import Path
import sys


def time_parser(timestring):
    datetime, timezone = timestring.split("+")
    date, exact_time = datetime.split("T")
    time, microsecs = exact_time.split(".")
    return date, time, microsecs, timezone


def export_dms(input_file, output_dir, username):
    with open(input_file, "r", encoding="utf8") as file:
        string = file.read()
        conversations = json.loads(string)

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        for current in conversations:
            export_conversation(current, output_dir)


def export_conversation(cur, output_dir):
    participants = cur["participants"]
    messages = cur["conversation"]
    cur_date = None

    # Remove username's name from the list
    # as it's obvious they're part of it
    if username:
        participants.remove(username)
    name = ", ".join(participants)

    with open(f"{output_dir}/{name}.txt", "w", encoding="utf8") as f:
        print(f"DMS with {name}", file=f)

        for msg in reversed(messages):
            datetimestring = msg["created_at"]
            date, time, microsecs, timezone = time_parser(datetimestring)

            # Print newlines showing change of date
            if cur_date != date:
                print(f"\n{date}\n", file=f)
            cur_date = date

            sender = msg["sender"]
            content = ""

            if "text" in msg:
                content = msg["text"]

            elif "heart" in msg:
                content = msg["heart"]

            elif "media" in msg:
                content = msg["media"]
            elif "media_url" in msg:
                content = msg["media_url"]
            elif "animated_media_images" in msg:
                content = msg["animated_media_images"]["downsized_large"]["url"]
            elif "voice_media" in msg:
                content = msg["voice_media"]

            elif "live_video_invite" in msg:
                content = msg["live_video_invite"]
            elif "media_owner" in msg:
                owner = msg["media_owner"]
                caption = msg["media_share_caption"]
                url = msg["media_share_url"]

                content = f"[{caption}]\n({url})"

            elif "video_call_action" in msg:
                content = msg["video_call_action"]
            elif "action" in msg:
                # Adding people to chats, renaming, removing people
                content = msg["action"]
            else:
                print(f"BUNGA: {msg.keys()}")

            prefix = f"{time} {sender}: "

            # If multi-line message padd it correctly
            if isinstance(content, str) and "\n" in content:
                temp = content.split("\n")
                thing = "\n" + " " * len(prefix)
                content = thing.join(temp)

            # Print message
            print(f"{prefix}{content}", file=f)

            # Print prefix line showing likes
            if "likes" in msg:
                likers = [x["username"] for x in msg["likes"]]
                print(f"    ❤Liked by {', '.join(likers)}❤", file=f)


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        username = sys.argv[2]
        directory = "direct_messages"
        export_dms(filename, directory, username)
    except IndexError:
        print("Arguments are: {input_file} {your username or empty string}")