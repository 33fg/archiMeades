/**
 * Amplify configuration - Cognito auth.
 * WO-16: Authentication Integration with Amplify
 * Configures Amplify when Cognito env vars are set; otherwise auth uses mock mode.
 */

import { Amplify } from 'aws-amplify'

const userPoolId = import.meta.env.VITE_COGNITO_USER_POOL_ID
const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID
export const isAmplifyConfigured = Boolean(
  userPoolId && clientId && typeof userPoolId === 'string' && typeof clientId === 'string'
)

if (isAmplifyConfigured) {
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId,
        userPoolClientId: clientId,
        loginWith: {
          email: true,
        },
      },
    },
  })
}
