import React, { createContext, useContext, useState, useEffect } from "react";
import { apiClient } from "../lib/api";

export type Role = "manager" | "staff" | "guest";

export interface UserState {
  token: string | null;
  role: Role;
  email?: string;
  employee_id?: string;
}

interface AuthContextType {
  user: UserState | null;
  token: string | null;
  role: Role;
  loginGuest: (email: string, otp: string) => Promise<void>;
  requestGuestOTP: (email: string) => Promise<void>;
  loginStaff: (employee_id: string, pin: string) => Promise<void>;
  loginManager: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setRoleOverride: (role: Role) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("sr360_token"));
  const [role, setRole] = useState<Role>(() => {
    const savedRole = localStorage.getItem("sr360_role");
    if (savedRole === "manager" || savedRole === "staff" || savedRole === "guest") {
      return savedRole;
    }
    return "manager";
  });
  const [user, setUser] = useState<UserState | null>(() => {
    const savedUser = localStorage.getItem("sr360_user");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const requestGuestOTP = async (email: string) => {
    await apiClient.post("/auth/guest/request-otp", { email });
  };

  const loginGuest = async (email: string, otp: string) => {
    const res = await apiClient.post("/auth/guest/verify-otp", { email, otp });
    const access_token = res.data.access_token;
    const userObj: UserState = { token: access_token, role: "guest", email };
    setToken(access_token);
    setRole("guest");
    setUser(userObj);
    localStorage.setItem("sr360_token", access_token);
    localStorage.setItem("sr360_role", "guest");
    localStorage.setItem("sr360_user", JSON.stringify(userObj));
  };

  const loginStaff = async (employee_id: string, pin: string) => {
    const res = await apiClient.post("/auth/staff/login", { employee_id, pin });
    const access_token = res.data.access_token;
    const userObj: UserState = { token: access_token, role: "staff", employee_id };
    setToken(access_token);
    setRole("staff");
    setUser(userObj);
    localStorage.setItem("sr360_token", access_token);
    localStorage.setItem("sr360_role", "staff");
    localStorage.setItem("sr360_user", JSON.stringify(userObj));
  };

  const loginManager = async (email: string, password: string) => {
    const res = await apiClient.post("/auth/manager/login", { email, password });
    const access_token = res.data.access_token;
    const userObj: UserState = { token: access_token, role: "manager", email };
    setToken(access_token);
    setRole("manager");
    setUser(userObj);
    localStorage.setItem("sr360_token", access_token);
    localStorage.setItem("sr360_role", "manager");
    localStorage.setItem("sr360_user", JSON.stringify(userObj));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("sr360_token");
    localStorage.removeItem("sr360_role");
    localStorage.removeItem("sr360_user");
  };

  const setRoleOverride = (newRole: Role) => {
    setRole(newRole);
    localStorage.setItem("sr360_role", newRole);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role,
        loginGuest,
        requestGuestOTP,
        loginStaff,
        loginManager,
        logout,
        setRoleOverride,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
