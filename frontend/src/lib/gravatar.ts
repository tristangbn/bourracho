import md5 from 'blueimp-md5'

/**
 * Generate a Gravatar URL for a given email/username
 * @param email - The email address or username to generate Gravatar for
 * @param size - The size of the avatar in pixels (default: 200)
 * @returns The Gravatar URL
 */
export function getGravatarUrl(email: string, size: number = 200): string {
  const normalizedEmail = email.trim().toLowerCase()
  const hash = md5(normalizedEmail)
  // Use '404' as default to return 404 if no Gravatar exists, allowing us to show initials
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=404`
}

/**
 * Generate a Gravatar URL with specific options
 * @param email - The email address or username
 * @param options - Gravatar options
 * @returns The Gravatar URL
 */
export function getGravatarUrlWithOptions(
  email: string,
  options: {
    size?: number
    default?: string
    rating?: 'g' | 'pg' | 'r' | 'x'
    forceDefault?: boolean
  } = {}
): string {
  const {
    size = 200,
    default: defaultImage = '404', // Use 404 to detect missing Gravatars
    rating = 'g',
    forceDefault = false,
  } = options

  const normalizedEmail = email.trim().toLowerCase()
  const hash = md5(normalizedEmail)

  const params = new URLSearchParams({
    s: size.toString(),
    d: defaultImage,
    r: rating,
  })

  if (forceDefault) {
    params.append('f', 'y')
  }

  return `https://www.gravatar.com/avatar/${hash}?${params.toString()}`
}

/**
 * Get user initials from username or email
 * @param username - The username or email
 * @returns The first two characters in uppercase
 */
export function getUserInitials(username: string): string {
  const cleanUsername = username.trim()
  if (cleanUsername.length === 0) return '??'

  // If it's an email, use the part before @
  const namePart = cleanUsername.includes('@')
    ? cleanUsername.split('@')[0]
    : cleanUsername

  return namePart.substring(0, 2).toUpperCase()
}
