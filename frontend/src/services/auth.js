import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export async function login(data) {
  return API.post("/auth/login", data);
}

export async function register(data) {
  return API.post("/auth/register", data);
}