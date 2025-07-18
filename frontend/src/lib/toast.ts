import { toast } from 'sonner'

// Toast utility functions for consistent error handling
export const showToast = {
  // Success notifications
  success: (message: string, description?: string) => {
    toast.success(message, {
      description,
      duration: 4000,
    })
  },

  // Error notifications
  error: (message: string, description?: string) => {
    toast.error(message, {
      description,
      duration: 6000,
    })
  },

  // Warning notifications
  warning: (message: string, description?: string) => {
    toast.warning(message, {
      description,
      duration: 5000,
    })
  },

  // Info notifications
  info: (message: string, description?: string) => {
    toast.info(message, {
      description,
      duration: 4000,
    })
  },

  // API error handler
  apiError: (error: any, defaultMessage = 'An error occurred') => {
    let message = defaultMessage
    let description: string | undefined

    if (error.response?.data?.message) {
      message = error.response.data.message
    } else if (error.response?.data?.error) {
      message = error.response.data.error
    } else if (error.message) {
      message = error.message
    }

    // Add status code to description if available
    if (error.response?.status) {
      description = `Status: ${error.response.status}`
    }

    // Handle specific error types
    switch (error.response?.status) {
      case 401:
        message = 'Authentication required'
        description = 'Please log in to continue'
        break
      case 403:
        message = 'Access denied'
        description = "You don't have permission to perform this action"
        break
      case 404:
        message = 'Resource not found'
        description = 'The requested resource could not be found'
        break
      case 422:
        message = 'Validation error'
        description = 'Please check your input and try again'
        break
      case 500:
        message = 'Server error'
        description = 'Something went wrong on our end. Please try again later'
        break
      case 0:
        message = 'Network error'
        description =
          'Unable to connect to the server. Please check your internet connection'
        break
    }

    toast.error(message, {
      description,
      duration: 6000,
    })
  },

  // Loading toast (returns dismiss function)
  loading: (message: string) => {
    return toast.loading(message, {
      duration: Infinity,
    })
  },

  // Dismiss a specific toast
  dismiss: (toastId: string | number) => {
    toast.dismiss(toastId)
  },
}
