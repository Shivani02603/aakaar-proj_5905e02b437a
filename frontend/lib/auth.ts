export const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token')
  }
  return null
}

export const setToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', token)
  }
}

export const removeToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token')
  }
}

export const isAuthenticated = (): boolean => {
  const token = getToken()
  if (!token) return false
  
  try {
    const payload = parseJwt(token)
    if (!payload.exp) return true
    return Date.now() < payload.exp * 1000
  } catch {
    return false
  }
}

export const getUser = (): { id: string; email: string; name: string } | null => {
  const token = getToken()
  if (!token) return null
  
  try {
    const payload = parseJwt(token)
    return {
      id: payload.sub || '',
      email: payload.email || '',
      name: payload.name || ''
    }
  } catch {
    return null
  }
}

export const parseJwt = (token: string): any => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Failed to parse JWT:', error)
    return {}
  }
}