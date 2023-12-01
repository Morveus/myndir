# myndir: a simple self-hosted photo gallery

Work in Progress 
(but already functional, see https://photos.morve.us/ ) 

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
