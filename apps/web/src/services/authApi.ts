import { apiClient } from "./apiClient";
import type { AuthUser, SignupRequest } from "../types/auth";

export function signup(payload: SignupRequest) {
  return apiClient<AuthUser>("/auth/signup", {
    method: "POST",
    body: payload,
  });
}