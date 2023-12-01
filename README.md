# myndir: a simple self-hosted photo gallery

Work in Progress 
(but already functional, see https://photos.morve.us/ ) 

# Why
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
- The photos get resized
- Minimalistic "good enough for now" design 
- They get displayed in a webpage
- Very short start delay

# What's to come to meet my needs:
- Changing the title and the favicon
- Displaying pictures when clicked
- Fixing the ratio in CSS (ratio is not accounted for, for now)
- Allowing (or not) users to download the original file
- Social links

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

(don't forget to change `/path/to/local/gallery` for your actual photos folder) 
