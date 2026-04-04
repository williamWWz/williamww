const express = require('express');

const app = express();
const port = 3000;

app.get('/', (_req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Docker 101 Lab</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
          }
          .card {
            max-width: 760px;
            padding: 24px;
            border: 1px solid #ddd;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
          }
          code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
          }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Docker 101 Tutorial Lab</h1>
          <p>This image was built from the <code>docker-101-lab</code> Dockerfile.</p>
          <p>Your task list is empty. Add one above!</p>
          <p>This app listens on port <code>3000</code>.</p>
        </div>
      </body>
    </html>
  `);
});

app.listen(port, () => {
  console.log(`Docker 101 lab app listening on port ${port}`);
});
