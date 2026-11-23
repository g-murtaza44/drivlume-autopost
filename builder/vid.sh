d=$1
ffmpeg -y -loglevel error -loop 1 -i $d/post.png -f lavfi -i anullsrc=r=44100:cl=stereo -filter_complex "[0:v]scale=2160:3840,zoompan=z='1+0.0002*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=210:s=1080x1920:fps=30,format=yuv420p[v]" -map "[v]" -map 1:a -t 7 -c:v libx264 -preset veryfast -crf 22 -c:a aac -b:a 96k -movflags +faststart $d/reel.mp4
