// if environment variavle set, use it , otherwise default to localhost
//in dev, not setting env variable since vite alrweady handles that 
export const BASE_URL = import.meta.env.VITE_BASE_URL || "http://localhost:8000"
