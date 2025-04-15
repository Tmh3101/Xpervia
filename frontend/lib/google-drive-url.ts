const baseUrl = process.env.NEXT_PUBLIC_API_URL

export function getGoogleDriveImageUrl(fileId: string) {
    return `${baseUrl}proxy/image/${fileId}/`;
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
