import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { config } from "@/config";
import { useAuthStore } from "@/store";
import { authService } from "@/services/endpoints";


const api = axios.create({
  baseURL: config.api.baseUrl,
  timeout: config.api.timeout,
  headers: { "Content-Type": "application/json" },
});

type RetriableRequestConfig = InternalAxiosRequestConfig & { _retryCount?: number };

type NormalizedError = {
  code: string;
  message: string;
  details?: unknown;
  traceId?: string;
};

let isRefreshing = false;
let refreshPromise: Promise<void> | null = null;

function getAccessToken() {
  if (typeof window === "undefined") return null;
  return useAuthStore.getState().tokens?.accessToken ?? null;
}

function setTokens(accessToken: string, refreshToken?: string) {
  // accessToken/refreshToken are only stored client-side to keep auth state in sync


  useAuthStore.setState({
    tokens: {
      accessToken,
      ...(refreshToken ? { refreshToken } : {}),
    },
  });
}

// ── Request Interceptor: Attach JWT + correlation IDs ────────────────
api.interceptors.request.use(
  (req: InternalAxiosRequestConfig) => {
    const accessToken = getAccessToken();
    if (accessToken && req.headers) {
      req.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Preserve backend middleware header if present in your environment.
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    if (apiKey && req.headers) {
      req.headers["X-API-Key"] = apiKey;
    }

    if (typeof window !== "undefined" && req.headers && !req.headers["X-Request-ID"]) {
      req.headers["X-Request-ID"] = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }

    return req;
  },
  (err) => Promise.reject(err)
);

async function refreshOnce() {
  if (isRefreshing && refreshPromise) return refreshPromise;

  const refreshToken = useAuthStore.getState().tokens?.refreshToken;
  if (!refreshToken) throw new Error("Missing refresh token");

  isRefreshing = true;
  refreshPromise = (async () => {
    const response = await authService.refresh(refreshToken);
    const nextAccessToken = response.data.access_token;
    const nextRefreshToken = response.data.refresh_token;
    setTokens(nextAccessToken, nextRefreshToken);
  })()
    .catch((e) => {
      useAuthStore.getState().logout();
      throw e;
    })
    .finally(() => {
      isRefreshing = false;
      refreshPromise = null;
    });

  return refreshPromise;
}

// ── Response Interceptor: refresh rotation on 401 ────────────────
api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const configWithRetry = error.config as RetriableRequestConfig & { headers?: any };
    const status = error.response?.status;

    if (configWithRetry && (configWithRetry._retryCount ?? 0) < 1 && status === 401) {
      configWithRetry._retryCount = (configWithRetry._retryCount ?? 0) + 1;

      try {
        await refreshOnce();
        const nextAccessToken = getAccessToken();
        if (nextAccessToken && configWithRetry.headers) {
          configWithRetry.headers.Authorization = `Bearer ${nextAccessToken}`;
        }
        return api(configWithRetry);
      } catch {
        if (typeof window !== "undefined") window.location.href = "/login";
      }
    }

    // Retry transient 5xx (separate from refresh path)
    if (configWithRetry && (configWithRetry._retryCount ?? 0) < 2 && status && status >= 500) {
      configWithRetry._retryCount = (configWithRetry._retryCount ?? 0) + 1;
      return api(configWithRetry);
    }

    const normalized: NormalizedError = {
      code: status ? `HTTP_${status}` : "NETWORK_ERROR",
      message: error.message,
      details: error.response?.data,
      traceId: (error.response?.headers as any)?.["x-trace-id"],
    };

    return Promise.reject(normalized);
  }
);


export default api;
