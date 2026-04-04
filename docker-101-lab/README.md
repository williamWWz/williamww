# Docker 101 Lab

This folder contains a small Node.js application and Dockerfile based on the core workflow from the Docker 101 tutorial.

## Files included
- `Dockerfile`
- `package.json`
- `src/index.js`
- `.dockerignore`

## Build the image
From inside the `docker-101-lab` folder, run:

```bash
docker build -t getting-started .
```

## Run the container
```bash
docker run -dp 3000:3000 getting-started
```

Then open:

```text
http://localhost:3000
```

## Verify running containers
```bash
docker ps
```

## Stop the container
Find the container ID with `docker ps`, then run:

```bash
docker stop <container-id>
```

## Update the app
To demonstrate the "Updating our App" section, edit this line in `src/index.js`:

```js
<p>Your task list is empty. Add one above!</p>
```

Change it to something new, for example:

```js
<p>The application was updated and rebuilt successfully.</p>
```

Then rebuild and run the updated image:

```bash
docker build -t getting-started .
docker stop <old-container-id>
docker run -dp 3000:3000 getting-started
```

## Notes
- This project is intended for the Docker 101 lab deliverable.
- The image listens on port `3000`.
- If port 3000 is already in use, stop the existing container before starting a new one.
