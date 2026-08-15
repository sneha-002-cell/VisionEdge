import axios from "axios";

const auth = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

export async function login(data) {
  return auth.post("/auth/login", data);
}

export async function register(data) {
  return auth.post("/auth/register", data);
}