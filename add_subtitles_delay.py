import re
import argparse
import os

def add_delay(file_path, file_extension, delay, create_new_file, prevent_underflow):
    # Read the content of the subtitle file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if file_extension == '.srt':
        # SRT Regex pattern to match timestamps in the format: HH:MM:SS,SSS --> hours:minutes:seconds,milliseconds
        timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
        separator = ','
    elif file_extension == '.vtt':
        # WebVTT Regex pattern to match timestamps in the format: HH:MM:SS.SSS --> hours:minutes:seconds.milliseconds
        timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})')
        separator = '.'

    # Function to add delay to a timestamp
    def add_delay_to_timestamp(timestamp:str, delay: int, separator: str):
        hours, minutes, seconds_milliseconds = timestamp.split(':')
        seconds, milliseconds = seconds_milliseconds.split(separator)
        
        total_milliseconds = int(hours) * 3600 * 1000 + int(minutes) * 60 * 1000 + int(seconds) * 1000 + int(milliseconds)
        total_milliseconds += delay

        # Ensure that the timestamp does not go negative if -z option is specified
        if prevent_underflow and total_milliseconds < 0:
            total_milliseconds = 0
        
        new_timestamp = "{:02}:{:02}:{:02}.{:03}".format(
            total_milliseconds // (3600 * 1000),
            (total_milliseconds % (3600 * 1000)) // (60 * 1000),
            (total_milliseconds % (60 * 1000)) // 1000,
            total_milliseconds % 1000
        )
        if file_extension == '.srt':
            new_timestamp = new_timestamp.replace('.', separator)
        elif file_extension == '.vtt':      # Actually no need to do this here as the separator is already a dot
            new_timestamp = new_timestamp.replace('.', separator)
        return new_timestamp
            
    # Modify timestamps with the specified delay
    for i in range(len(lines)):
        match = timestamp_pattern.match(lines[i])
        if match:
            start_timestamp, end_timestamp = match.groups()
            new_start_timestamp = add_delay_to_timestamp(start_timestamp, delay, separator)
            new_end_timestamp = add_delay_to_timestamp(end_timestamp, delay, separator)
            lines[i] = lines[i].replace(start_timestamp, new_start_timestamp).replace(end_timestamp, new_end_timestamp)

    # Save the modified content back to the subtitle file or create a new file
    if create_new_file:
        new_file_name = f'delay_{delay}ms_{os.path.basename(file_path)}'
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        with open(new_file_path, 'w', encoding='utf-8') as new_file:
            new_file.writelines(lines)
        print(f'Delay of {delay/1000}s or {delay}ms added. Modified subtitles saved to: {new_file_path}')
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        print(f'Delay of {delay/1000}s or {delay}ms added to the subtitle file: {file_path}')

def main():
    parser = argparse.ArgumentParser(description='Add delay to subtitle timestamps.')
    parser.add_argument('file_path', help='Path to the subtitle file')
    parser.add_argument('-s', '--seconds', type=float, help='Delay in seconds (decimal values up to three decimal points)')
    parser.add_argument('-m', '--milliseconds', type=int, help='Delay in milliseconds (integer value)')
    parser.add_argument('-n', '--new-file', action='store_true', help='Create a new file with modified subtitles')
    parser.add_argument('-z', '--prevent-underflow', action='store_true', help='Prevent timestamps from going negative')

    args = parser.parse_args()

    if not (args.seconds or args.milliseconds):
        print('Error: Please provide either -s or -m option to specify the delay.')
        print('Usage: python script_name.py <file_path> [-s <delay_in_seconds>] [-m <delay_in_milliseconds>] [-n] [-z]')
        return
    
    # Check if the file_path exists or not
    if not os.path.exists(args.file_path):
        print(f'Error: File not found: {args.file_path}')
        return
    
    if args.file_path.endswith('.srt'):
        file_extension = '.srt'
    elif args.file_path.endswith('.vtt'):
        file_extension = '.vtt'
    else:
        print('Error: Invalid file extension. Only .srt and .vtt files are supported.')
        return

    if args.milliseconds:
        delay = int(args.milliseconds)
    elif args.seconds:
        delay = int(args.seconds * 1000)

    add_delay(args.file_path, file_extension, delay, args.new_file, args.prevent_underflow)

if __name__ == "__main__":
    main()
