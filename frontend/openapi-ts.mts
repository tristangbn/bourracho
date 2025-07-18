import { createClient } from '@hey-api/openapi-ts'

await createClient({
  input: 'http://localhost:8000/api/openapi.json',
  output: 'src/api/generated',
  plugins: [{ name: '@hey-api/client-axios', throwOnError: true }],
})
