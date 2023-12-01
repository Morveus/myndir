# myndir: a simple self-hosted photo gallery

👷🧑‍🏭 Work in Progress ⌨️⚒️

<img width="1157" alt="image" src="https://github.com/Morveus/myndir/assets/2972468/e5a8dc6a-59d2-4e32-b50a-473baaab186a">

(but already functional, see https://photos.morve.us/ ) 

# Context
I have a camera capable of uploading pictures through FTP/SSH, so I wrote a simple tool allowing me to create "sessions" (let's say "Trees") from my smartphone, so every picture snapped from the camera lands in a named folder on my home NAS.

Then a script picks the folder up, spins up a pod on my Kubernetes cluster and creates a DNS entry: "trees.mydomain.com", effectively creating a quick gallery in real time from RAW pictures, as long as I have Internet connectivity where I'm shooting.

This project is the "gallery container" part, and will work for any JPEG, PNGs... you throw at it.

# Why another gallery project
I was looking for a very simple an lightweight photo gallery matching those criteria:
- Easy to deploy
- No database (I hate SQLite) 
- As few dependencies as possible
- Only based on one mounted folder
- Quick to redeploy
- That updates automatically when I add a photo to the folder
- That resizes my pictures before serving them in the gallery
- Without a config file/env file, or at least a very small straightforward one if required

I've tried a lot of awesome open source projects but there was always something bothering me (either some SQLite database, or a very long redeployment delay which isn't my cup of tea in a Kubernetes cluster)  I decided to write my own. 

# What's working:
- Simply mount your photos folder
- The photos get resized automatically
- Minimalistic "good enough for now" design 
- Simple webpage to display the pictures
- Very short (re)start/redeploy delay
- New pictures are processed and added in every minute

# What's to come to meet my needs:
🟠 Changing the title and the favicon

🟠 Sorting pictures by their creation date

🔴 Displaying pictures when clicked

🟢 Fixing the ratio in CSS (ratio is not accounted for, for now)

🔴 Allowing (or not) users to download the original file

🔴 Social links

🟢 Prettier display (I love what https://github.com/waschinski/photo-stream has done) 

# Deployment 

Using Docker CLI:
```sh
docker run -d --name myndir -p 3000:3000 -v /path/to/local/gallery:/app/source morveus/myndir:latest`
```

Using Docker Compose:
```sh
git clone https://github.com/Morveus/myndir
cd myndir
docker-compose up
```

Don't forget to change `/path/to/local/gallery` for your actual photos folder.

If you want MUCH faster startup times after the first pictures generation, add this to the command line to use persistent storage for your thumbnails:
```sh
-v /path/to/local/output-files:/app/optimized
```
(or edit the docker-compose.yaml to mount this folder).

# Running manually

```sh
git clone https://github.com/Morveus/myndir
cd myndir
pip install -r requirements.txt
python app.py
```
