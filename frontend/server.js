const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4200;

app.use(express.static(path.join(__dirname, 'dist/frontend/browser')));

app.get('/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist/frontend/browser/index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Frontend server running on port ${PORT}`);
});
