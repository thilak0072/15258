// logging-middleware/logger.js
import axios from 'axios';

const LOG_ENDPOINT = 'http://20.244.56.144/evaluation-service/logs';
let ACCESS_TOKEN = process.env.AUTH_TOKEN || '';

export function initLogger(token) {
  ACCESS_TOKEN = token;
}

export async function log(stack, level, pkg, message) {
  if (!ACCESS_TOKEN) return;
  try {
    await axios.post(LOG_ENDPOINT, {
      stack, level, package: pkg, message
    }, {
      headers: { Authorization: `Bearer ${ACCESS_TOKEN}` }
    });
  } catch (e) {
    console.error('Log failed:', e.toString());
  }
}
