const apiKey = process.env.NEXT_PUBLIC_GOOGLE_DRIVE_API_KEY;

export function getGoogleDriveImageUrl(fileId: string) {
    return `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media&key=${apiKey}`;
}

export function getGoogleDriveVideoUrl(fileId: string) {
    return `https://drive.google.com/file/d/${fileId}/preview`
}

export function getGoogleDriveDownloadFileUrl(fileId: string) {
    return `https://drive.google.com/uc?export=download&id=${fileId}`
}

export function getGoogleDriveFileUrl(fileId: string) {
    return `https://drive.google.com/file/d/${fileId}/preview`
}
