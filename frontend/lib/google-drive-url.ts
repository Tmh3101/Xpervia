export function getGoogleDriveImageUrl(fileId: string) {
    return `https://drive.google.com/thumbnail?id=${fileId}&sz=w1920`
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
