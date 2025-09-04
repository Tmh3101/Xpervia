export const routePermissions: Record<string, RegExp[]> = {
  guest: [
    /^\/$/,
    /^\/courses\/[^\/]+$/,
    /^\/auth\/request-reset-password$/,
    /^\/auth\/reset-password$/,
  ],
  student: [
    /^\/$/,
    /^\/courses\/[^\/]+$/,
    /^\/student\/my-courses$/,
    /^\/student\/favorites$/,
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
  ],
};
