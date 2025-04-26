import csv, os, requests, shutil
from typing import Optional
from yt_dlp import YoutubeDL
from datetime import datetime

def dyc(url: str, output_path: Optional[str] = None) -> None:
    """
    Download YouTube content (single video or playlist) in MP4 format only. This is modified slightly from the original code from https://github.com/pH-7/Download-Simply-Videos-From-YouTube/blob/main/readme.md
    
    Args:
        url (str): URL of the YouTube video or playlist
        output_path (str, optional): Directory to save the downloads. Defaults to './downloads'
    """
    # Set default output path if none provided
    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'downloads')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Configure yt-dlp options for MP4 only
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
        'no_warnings': False,
        'extract_flat': False,
        # Disable all additional downloads
        'writesubtitles': False,
        'writethumbnail': False,
        'writeautomaticsub': False,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        # Clean up options
        'keepvideo': False,
        'clean_infojson': True
    }

    # Set different output templates for playlists and single videos
   
    ydl_opts['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')
    print("Detected single video URL. Downloading video...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Download content
            ydl.download([url])
            print(f"\nDownload completed successfully! Files saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def convert_to_seconds(time: str) -> int:
    '''
    Converts time in hh:mm:ss to time in seconds: Used specifically for this script
    '''

    return (int(time[0:1]) * 3600) + (int(time[2:4]) * 60) + int(time[5:])

#Grabs Data from Google Sheet
sheet_id = "1wwRU0JyZE4x-4acpdzguyb2a_EV-8n_7lP-IHHPHhHQ"
worksheet_name = "Sheet1"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&id={sheet_id}&gid=0"
response = requests.get(csv_url)
with open("temp.csv", 'wb') as f:
    f.write(response.content)

#Sets the folder path, used to grab downloaded files later
folder_path = os.path.os.path.dirname(os.path.abspath(__file__))
folder_path_downloads = f'{folder_path}\downloads'
folder_path_output = f'{folder_path}\{datetime.now()}'
os.makedirs(folder_path_downloads, exist_ok=True)
os.makedirs(folder_path_output, exist_ok=True)

#grabs csv file for use to find songs
data = "temp.csv"

#Opens csv file
with open(data, newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)

    #For every file in the csv (skipping the header)
    for row in reader:

        print(row)
        
        #Download the Given Link
        dyc(row[3])

        #Grab the File that was just Downloaded
        current_file = None
        for file in os.listdir(folder_path_downloads):
            current_file = file
        
        #Sets up name for Outputs (Dealing with Fade in and out stuff)
        name = row[0]
        if row[4] == 'TRUE':
            name += 'FadeOut'

        #Trim the File with ffmpeg
        os.system(f'ffmpeg -i "{folder_path_downloads}\{current_file}" -ss {row[1]} -to {row[2]} -q:a 2 -vn "{folder_path_output}\{name}.mp3"')

        #Delete the file out of the downloads folder
        os.remove(f'{folder_path_downloads}\{current_file}')

        #This Handles the File if there is a fade
        if row[4] == 'TRUE':
            os.system(f'ffmpeg -i "{folder_path_output}\{name}.mp3" -af "afade=type=out:st={convert_to_seconds(row[2]) - int(row[5])}:d={int(row[5])-1.5:.1f}" -c:a libmp3lame "{folder_path_output}\{row[0]}.mp3"')
            os.remove(f'{folder_path_output}\{name}.mp3')

#File Cleanup
os.remove(f'{folder_path}\\temp.csv')
shutil.rmtree(f'{folder_path}\downloads')