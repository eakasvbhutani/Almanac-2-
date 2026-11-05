Generator: python3 teen.py (needs pillow, ffmpeg, and NotoColorEmoji.ttf from googlefonts/noto-emoji placed in fonts/)
Music: python3 music3.py → beat3.wav (needs numpy, scipy); then ffmpeg -i teen_invite.mp4 -i beat3.wav -c:v copy -c:a aac -shortest teen_invite_music.mp4
