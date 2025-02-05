require("dotenv").config();
const { google } = require("googleapis");
const express = require("express");
const multer = require("multer");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = 3000;

// Configure OAuth2 Client
const oauth2Client = new google.auth.OAuth2(
    process.env.CLIENT_ID,
    process.env.CLIENT_SECRET,
    process.env.REDIRECT_URI
);

// Set Refresh Token (to avoid re-authentication every time)
oauth2Client.setCredentials({ refresh_token: process.env.REFRESH_TOKEN });

// Initialize Google Drive API
const drive = google.drive({ version: "v3", auth: oauth2Client });

// Configure to serve static files from the "public" directory
app.use(express.static(path.join(__dirname, "public")));

// OAuth authentication URL
app.get("/auth", async (req, res) => {
    const url = oauth2Client.generateAuthUrl({
        access_type: "offline",
        scope: [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
        ],
        prompt: "consent", // Ensure refresh_token is always granted on the first time
    });
    const open = await import("open");
    open.default(url);
    res.send("Please visit the URL to authenticate: " + url);
});

// Handle OAuth callback
app.get("/oauth2callback", async (req, res) => {
    try {
        const { code } = req.query;
        const { tokens } = await oauth2Client.getToken(code);
        oauth2Client.setCredentials(tokens);

        // Update REFRESH_TOKEN after OAuth authentication
        if (tokens.refresh_token) {
            updateEnv("REFRESH_TOKEN", tokens.refresh_token);
            console.log("Refresh Token has been updated in .env!");
        }

            res.send("Authentication successful! You can close this window.");
    } catch (error) {
        console.error("Error during OAuth authentication:", error);
        res.status(500).send("Error during OAuth authentication.");
    }
});

// Configure multer to handle file uploads
const upload = multer({ dest: "uploads/" });

app.post("/upload", upload.single("file"), async (req, res) => {
    try {
        const fileMetadata = {
            name: req.file.originalname,
            parents: [process.env.FOLDER_ID], // Save to a specific folder in Google Drive
        };

        const media = {
            mimeType: req.file.mimetype,
            body: fs.createReadStream(req.file.path),
        };

        const file = await drive.files.create({
            resource: fileMetadata,
            media: media,
            fields: "id",
        });

        // Delete temporary file after upload
        fs.unlinkSync(req.file.path);

        res.json({ fileId: file.data.id });
    } catch (error) {
        console.error("Error uploading file to Google Drive:", error);
        res.status(500).json({ error: "Error uploading file to Google Drive" });
    }
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});

const updateEnv = (key, value) => {
    const envPath = ".env";
    let envContent = fs.existsSync(envPath) ? fs.readFileSync(envPath, "utf8") : "";

    const regex = new RegExp(`^${key}=.*`, "m");
    if (envContent.match(regex)) {
        // If key exists, replace the value
        envContent = envContent.replace(regex, `${key}=${value}`);
    } else {
        // If key does not exist, add new
        envContent += `\n${key}=${value}`;
    }

    fs.writeFileSync(envPath, envContent);
};