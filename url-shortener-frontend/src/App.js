import React, { useState } from "react";
import axios from "axios";
import { TextField, Button, Typography, Box, Grid, Paper } from "@mui/material";
import { log } from "./logger/logger"; // Logger middleware

const MAX_URLS = 5;
const BACKEND_BASE_URL = "http://localhost:8000"; // Adjust to your FastAPI port

const isValidURL = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

const App = () => {
  const [urlInputs, setUrlInputs] = useState([
    { longUrl: "", validity: "", shortcode: "", result: null, error: null },
  ]);

  const handleChange = (index, field, value) => {
    const updated = [...urlInputs];
    updated[index][field] = value;
    setUrlInputs(updated);
  };

  const handleAddInput = () => {
    if (urlInputs.length < MAX_URLS) {
      setUrlInputs([
        ...urlInputs,
        { longUrl: "", validity: "", shortcode: "", result: null, error: null },
      ]);
    }
  };

  const handleSubmit = async (index) => {
    const entry = urlInputs[index];
    const payload = {
      url: entry.longUrl,
      validity: entry.validity ? parseInt(entry.validity) : 30,
    };
    if (entry.shortcode) payload.shortcode = entry.shortcode;

    if (!isValidURL(entry.longUrl)) {
      const updated = [...urlInputs];
      updated[index].error = "Invalid URL format.";
      setUrlInputs(updated);
      await log("frontend", "error", "component", "Invalid URL format entered");
      return;
    }

    try {
      const response = await axios.post(`${BACKEND_BASE_URL}/shorturls`, payload);
      const updated = [...urlInputs];
      updated[index].result = response.data;
      updated[index].error = null;
      setUrlInputs(updated);
      await log("frontend", "info", "component", `Shortened URL created: ${response.data.shortLink}`);
    } catch (err) {
      const updated = [...urlInputs];
      updated[index].error = err.response?.data?.detail || "Request failed";
      setUrlInputs(updated);
      await log("frontend", "error", "component", `API error: ${err.message}`);
    }
  };

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        URL Shortener
      </Typography>
      {urlInputs.map((entry, index) => (
        <Paper key={index} sx={{ mb: 3, p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={5}>
              <TextField
                label="Long URL"
                fullWidth
                value={entry.longUrl}
                onChange={(e) => handleChange(index, "longUrl", e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                label="Validity (min)"
                fullWidth
                value={entry.validity}
                type="number"
                onChange={(e) => handleChange(index, "validity", e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                label="Shortcode"
                fullWidth
                value={entry.shortcode}
                onChange={(e) => handleChange(index, "shortcode", e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button variant="contained" onClick={() => handleSubmit(index)} fullWidth>
                Shorten
              </Button>
            </Grid>
            {entry.error && (
              <Grid item xs={12}>
                <Typography color="error">{entry.error}</Typography>
              </Grid>
            )}
            {entry.result && (
              <Grid item xs={12}>
                <Typography variant="body1">
                  Short URL: <a href={entry.result.shortLink}>{entry.result.shortLink}</a>
                </Typography>
                <Typography variant="body2">Expiry: {entry.result.expiry}</Typography>
              </Grid>
            )}
          </Grid>
        </Paper>
      ))}
      {urlInputs.length < MAX_URLS && (
        <Button onClick={handleAddInput} variant="outlined">
          + Add Another URL
        </Button>
      )}
    </Box>
  );
};

export default App;
