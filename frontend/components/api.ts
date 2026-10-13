export const API_URL=(process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000').replace(/\/$/,'');
export function errorMessage(value:unknown):string{return value instanceof Error?value.message:'Something went wrong. Please try again.'}
