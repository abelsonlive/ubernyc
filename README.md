# setup the docker image:
```
docker build -t ubernyc .
```

# start the daemon + tail logs
```
JOB=$(docker run -d ubernyc sudo /home/ubernyc/bin/run-docker)
docker logs $JOB
```