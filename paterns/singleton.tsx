import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useMemo,
  type ReactNode,
} from "react";

const STORAGE_PREFIX = "tesis_";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface RequestConfig {
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  timeout?: number;
}

interface ApiResponse<T = unknown> {
  data: T | null;
  error: string | null;
  status: number;
}

interface RetryConfig {
  attempts: number;
  delay: number;
  retryOn: number[];
}

const DEFAULT_RETRY: RetryConfig = { attempts: 3, delay: 500, retryOn: [408, 429, 500, 502, 503, 504] };

interface StorageManager {
  get<T>(key: string, fallback?: T): T | null;
  set<T>(key: string, value: T): void;
  remove(key: string): void;
  clear(): void;
}

class LocalStorageManager implements StorageManager {
  get<T>(key: string, fallback?: T): T | null {
    try {
      const raw = localStorage.getItem(STORAGE_PREFIX + key);
      if (raw === null) return fallback ?? null;
      return JSON.parse(raw) as T;
    } catch {
      return fallback ?? null;
    }
  }

  set<T>(key: string, value: T): void {
    try {
      localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value));
    } catch (err) {
      console.warn("[Storage] Failed to save:", key, err);
    }
  }

  remove(key: string): void {
    localStorage.removeItem(STORAGE_PREFIX + key);
  }

  clear(): void {
    Object.keys(localStorage)
      .filter((k) => k.startsWith(STORAGE_PREFIX))
      .forEach((k) => localStorage.removeItem(k));
  }
}

export const storage = new LocalStorageManager();

type TokenRefreshHandler = () => Promise<string>;

interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  userId: number | null;
  username: string | null;
}

class AuthManager {
  private _token: string | null = null;
  private _userId: number | null = null;
  private _username: string | null = null;
  private _listeners = new Set<(state: AuthState) => void>();
  private _refreshPromise: Promise<string> | null = null;

  constructor() {
    const saved = storage.get<AuthState>("auth");
    if (saved?.token) {
      this._token = saved.token;
      this._userId = saved.userId ?? null;
      this._username = saved.username ?? null;
    }
  }

  get state(): AuthState {
    return {
      isAuthenticated: this._token !== null,
      token: this._token,
      userId: this._userId,
      username: this._username,
    };
  }

  get token(): string | null {
    return this._token;
  }

  get userId(): number | null {
    return this._userId;
  }

  subscribe(listener: (state: AuthState) => void): () => void {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  private _notify() {
    this._listeners.forEach((l) => l(this.state));
  }

  setAuth(token: string, userId: number, username: string): void {
    this._token = token;
    this._userId = userId;
    this._username = username;
    storage.set("auth", { isAuthenticated: true, token, userId, username });
    this._notify();
  }

  refreshToken(handler: TokenRefreshHandler): Promise<string> {
    if (this._refreshPromise) return this._refreshPromise;

    this._refreshPromise = handler()
      .then((token) => {
        this._token = token;
        storage.set("auth", { ...this.state, token });
        this._notify();
        return token;
      })
      .finally(() => {
        this._refreshPromise = null;
      });

    return this._refreshPromise;
  }

  clearAuth(): void {
    this._token = null;
    this._userId = null;
    this._username = null;
    storage.remove("auth");
    this._notify();
  }
}

export const authManager = new AuthManager();

interface AuthContextValue {
  state: AuthState;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: (handler: TokenRefreshHandler) => Promise<string>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: ReactNode;
  loginEndpoint?: string;
}

export function AuthProvider({ children, loginEndpoint = "/api/auth/login/" }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>(() => authManager.state);

  useEffect(() => {
    const off = authManager.subscribe(setState);
    return () => off();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const resp = await fetch(loginEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      throw new Error(body.detail ?? `Login failed: ${resp.status}`);
    }

    const data = await resp.json();
    authManager.setAuth(data.access, data.user?.id ?? 0, username);
  }, [loginEndpoint]);

  const logout = useCallback(() => {
    authManager.clearAuth();
  }, []);

  const refreshToken = useCallback((handler: TokenRefreshHandler) => {
    return authManager.refreshToken(handler);
  }, []);

  return (
    <AuthContext.Provider value={{ state, login, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

type RequestInterceptor = (url: string, config: RequestConfig) => RequestConfig | Promise<RequestConfig>;
type ResponseInterceptor = <T>(resp: ApiResponse<T>) => ApiResponse<T>;

class ApiClient {
  private baseUrl: string;
  private interceptors = { request: [] as RequestInterceptor[], response: [] as ResponseInterceptor[] };
  private retryConfig: RetryConfig;

  constructor(baseUrl = "/api/v1/", retry: RetryConfig = DEFAULT_RETRY) {
    this.baseUrl = baseUrl;
    this.retryConfig = retry;
  }

  addRequestInterceptor(fn: RequestInterceptor): () => void {
    this.interceptors.request.push(fn);
    return () => {
      const idx = this.interceptors.request.indexOf(fn);
      if (idx !== -1) this.interceptors.request.splice(idx, 1);
    };
  }

  addResponseInterceptor(fn: ResponseInterceptor): () => void {
    this.interceptors.response.push(fn);
    return () => {
      const idx = this.interceptors.response.indexOf(fn);
      if (idx !== -1) this.interceptors.response.splice(idx, 1);
    };
  }

  private async _applyRequestInterceptors(
    url: string,
    config: RequestConfig
  ): Promise<RequestConfig> {
    let result = { ...config };
    for (const fn of this.interceptors.request) {
      result = await fn(url, result);
    }
    return result;
  }

  private _applyResponseInterceptors<T>(resp: ApiResponse<T>): ApiResponse<T> {
    let result = { ...resp };
    for (const fn of this.interceptors.response) {
      result = fn(result);
    }
    return result;
  }

  private async _request<T>(
    path: string,
    config: RequestConfig,
    retryCount = 0
  ): Promise<ApiResponse<T>> {
    const url = this.baseUrl + path;
    const finalConfig = await this._applyRequestInterceptors(url, config);

    if (finalConfig.timeout) {
      finalConfig.signal = new AbortController().signal;
      setTimeout(() => {
        (finalConfig.signal as AbortSignal).abort();
      }, finalConfig.timeout);
    }

    try {
      const resp = await fetch(url, {
        method: config.method,
        headers: config.headers,
        body: config.body ? JSON.stringify(config.body) : undefined,
        signal: config.signal,
      } as RequestInit);

      if (
        this.retryConfig.retryOn.includes(resp.status) &&
        retryCount < this.retryConfig.attempts
      ) {
        await new Promise((r) => setTimeout(r, this.retryConfig.delay * (retryCount + 1)));
        return this._request<T>(path, config, retryCount + 1);
      }

      const data = resp.status === 204 ? null : await resp.json().catch(() => null);

      return this._applyResponseInterceptors({
        data,
        status: resp.status,
        error: resp.ok ? null : (data?.detail ?? `HTTP ${resp.status}`),
      });
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        return this._applyResponseInterceptors({ data: null, status: 408, error: "Timeout" });
      }
      return this._applyResponseInterceptors({ data: null, status: 0, error: String(err) });
    }
  }

  async get<T>(path: string, config?: Omit<RequestConfig, "method">): Promise<ApiResponse<T>> {
    return this._request<T>(path, { ...config, method: "GET" });
  }

  async post<T>(path: string, body: unknown, config?: Omit<RequestConfig, "method">): Promise<ApiResponse<T>> {
    return this._request<T>(path, { ...config, method: "POST", body });
  }

  async put<T>(path: string, body: unknown, config?: Omit<RequestConfig, "method">): Promise<ApiResponse<T>> {
    return this._request<T>(path, { ...config, method: "PUT", body });
  }

  async patch<T>(path: string, body: unknown, config?: Omit<RequestConfig, "method">): Promise<ApiResponse<T>> {
    return this._request<T>(path, { ...config, method: "PATCH", body });
  }

  async delete<T>(path: string, config?: Omit<RequestConfig, "method">): Promise<ApiResponse<T>> {
    return this._request<T>(path, { ...config, method: "DELETE" });
  }
}

export const apiClient = new ApiClient("/api/v1/");

apiClient.addRequestInterceptor((url, config) => {
  const token = authManager.token;
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  if (config.body !== undefined && !(config.body instanceof FormData)) {
    config.headers = {
      ...config.headers,
      "Content-Type": "application/json",
    };
  }
  return config;
});

apiClient.addResponseInterceptor((resp) => {
  if (resp.status === 401) {
    authManager.clearAuth();
    window.location.href = "/login";
  }
  return resp;
});

apiClient.addResponseInterceptor((resp) => {
  if (resp.status === 403) {
    console.warn("[ApiClient] Acceso denegado");
  }
  return resp;
});

interface ApiServiceOptions {
  client?: ApiClient;
  basePath?: string;
}

function createApiService<T>(
  endpoints: Record<string, string>,
  { client = apiClient, basePath = "" }: ApiServiceOptions = {}
) {
  const api = {} as Record<string, (...args: unknown[]) => Promise<ApiResponse<T>>>;

  for (const [name, path] of Object.entries(endpoints)) {
    api[name] = async (...args: unknown[]): Promise<ApiResponse<T>> => {
      const method = (args[0] as HttpMethod) ?? "GET";
      const url = path.replace(/\{(\w+)\}/g, (_, k) => String(args[args.length - 1]?.[k] ?? k));
      const body = ["POST", "PUT", "PATCH"].includes(method) ? args[1] : undefined;
      return (client as unknown as Record<string, (...a: unknown[]) => Promise<ApiResponse<T>>>)[method.toLowerCase()](
        basePath + url,
        body
      );
    };
  }

  return api;
}

export const indicatorsApi = createApiService<{
  id: number;
  code: string;
  name: string;
  unit: string;
  value: number;
}>({
  list: "indicators/",
  retrieve: "indicators/{id}/",
  create: "indicators/",
  update: "indicators/{id}/",
  partialUpdate: "indicators/{id}/",
  delete: "indicators/{id}/",
});

export const reportsApi = createApiService<{
  id: number;
  entity: number;
  period: number;
  report_type: string;
  status: string;
}>({
  list: "reports/",
  generate: "reports/generate/",
  retrieve: "reports/{id}/",
});

export function useIndicators() {
  const [items, setItems] = useState<{ id: number; code: string; name: string; unit: string; value: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    const resp = await apiClient.get<{ results?: unknown[]; count?: number }>("indicators/");
    if (resp.error) {
      setError(resp.error);
    } else {
      setItems((resp.data?.results ?? resp.data ?? []) as typeof items);
    }
    setLoading(false);
  }, []);

  const create = useCallback(async (payload: Record<string, unknown>) => {
    const resp = await apiClient.post("indicators/", payload);
    if (!resp.error) {
      await fetchAll();
    }
    return resp;
  }, [fetchAll]);

  const remove = useCallback(async (id: number) => {
    const resp = await apiClient.delete(`indicators/${id}/`);
    if (!resp.error) {
      setItems((prev) => prev.filter((i) => i.id !== id));
    }
    return resp;
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return { items, loading, error, fetchAll, create, remove };
}

export function useAuthWrapped<P, R>(
  fn: (params: P) => Promise<ApiResponse<R>>
) {
  return useCallback(
    (params: P) => {
      if (!authManager.token) {
        return Promise.resolve({ data: null, error: "No autenticado", status: 401 });
      }
      return fn(params);
    },
    [fn]
  );
}

interface ApiProviderProps {
  children: ReactNode;
}

export function ApiProvider({ children }: ApiProviderProps) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const onOnline = () => setIsOnline(true);
    const onOffline = () => setIsOnline(false);
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}

export default apiClient;
