export const routePermissions: Record<string, RegExp[]> = {
    guest: [
      /^\/$/,                                // Trang chủ
      /^\/courses\/[^\/]+$/,                 // Chi tiết khóa học
    ],
    student: [
      /^\/$/,                                // Trang chủ
      /^\/courses\/[^\/]+$/,
      /^\/student\/my-courses$/,
      /^\/profile\/student\/[^\/]+$/,
      /^\/student\/lessons\/[^\/]+$/,
      /^\/student\/lessons\/[^\/]+\/[^\/]+$/,
    ],
    teacher: [
      /^\/teacher$/,
      /^\/teacher\/courses\/[^\/]+\/detail$/,
      /^\/teacher\/courses\/[^\/]+\/lessons\/[^\/]+$/,
      /^\/profile\/teacher\/[^\/]+$/,
    ],
    admin: [
      /^\/admin$/,
      /^\/admin\/users$/,
      /^\/admin\/courses$/,
      /^\/admin\/statistics\/users$/,
      /^\/admin\/statistics\/revenue$/,
    ]
  }
  