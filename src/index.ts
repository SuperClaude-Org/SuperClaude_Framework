import express from "express";
import logger from "./logger.js";
import app from "./app.js";

const PORT = process.env.PORT || 8080;

const server = express()
  .use(app)
  .listen(PORT, () => {
    logger.info({ port: PORT }, "Server started");
  });

process.on("SIGTERM", () => {
  logger.info("SIGTERM signal received: closing HTTP server");
  server.close(() => {
    logger.info("HTTP server closed");
  });
});