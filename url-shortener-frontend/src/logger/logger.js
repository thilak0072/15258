import axios from "axios";

const LOGGING_API = "http://20.244.56.144/evaluation-service/logs";
const ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"; // replace with your actual token

export const log = async (stack, level, pkg, message) => {
  try {
    await axios.post(
      LOGGING_API,
      {
        stack,
        level,
        package: pkg,
        message,
      },
      {
        headers: {
          Authorization: `Bearer ${ACCESS_TOKEN}`,
        },
      }
    );
  } catch (error) {
    console.error("Logging failed", error.response?.data || error.message);
  }
};
