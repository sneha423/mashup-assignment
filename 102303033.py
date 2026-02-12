import sys
from mashup_core.mashup import create_mashup


def print_usage():
    print(
        "Usage: python 1015579.py "
        "<SingerName> <NumberOfVideos> <AudioDurationInSeconds> <OutputFileName>"
    )
    print('Example: python 1015579.py "Sharry Maan" 20 30 mashup.mp3')


def main():
    # Expect 5 items in sys.argv: script + 4 params
    if len(sys.argv) != 5:
        print("Error: Incorrect number of parameters.")
        print_usage()
        sys.exit(1)

    singer_name = sys.argv[1]
    num_videos_arg = sys.argv[2]
    duration_arg = sys.argv[3]
    output_file = sys.argv[4]

    # Validate numeric arguments
    try:
        num_videos = int(num_videos_arg)
        duration = int(duration_arg)
    except ValueError:
        print("Error: <NumberOfVideos> and <AudioDurationInSeconds> must be integers.")
        print_usage()
        sys.exit(1)

    # Additional constraints (N>10, Y>20) – assignment requirement. [file:1]
    if num_videos <= 10:
        print("Error: <NumberOfVideos> must be greater than 10.")
        sys.exit(1)

    if duration <= 20:
        print("Error: <AudioDurationInSeconds> must be greater than 20.")
        sys.exit(1)

    try:
        print("Creating mashup, please wait...")
        final_path = create_mashup(singer_name, num_videos, duration, output_file)
        print(f"Mashup created successfully: {final_path}")
    except Exception as e:
        print(f"An error occurred while creating mashup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
