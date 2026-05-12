import { apiClient } from "./apiClient";
import type { AuthUser, LoginRequest, SignupRequest } from "../types/auth";

export function signup(payload: SignupRequest) {
  return apiClient<AuthUser>("/auth/signup", {
    method: "POST",
    body: payload,
  });
}

export function login(payload: LoginRequest) {
    return apiClient<AuthUser>("/auth/login", {
        method: "POST",
        body: payload,
    });
}