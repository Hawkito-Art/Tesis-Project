import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useRef,
  type ReactNode,
} from "react";

type NotificationType = "success" | "error" | "warning" | "info";

interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  createdAt: Date;
}

interface NotificationContextValue {
  notifications: Notification[];
  addNotification: (n: Omit<Notification, "id" | "createdAt">) => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextValue | null>(null);

type ObserverHandler<T = unknown> = (payload: T) => void;

interface EventBusInstance {
  on<T = unknown>(event: string, handler: ObserverHandler<T>): () => void;
  off<T = unknown>(event: string, handler: ObserverHandler<T>): void;
  emit<T = unknown>(event: string, payload?: T): void;
  once<T = unknown>(event: string, handler: ObserverHandler<T>): void;
}

class EventBus implements EventBusInstance {
  private handlers = new Map<string, Set<ObserverHandler>>();
  private nextId = 0;

  on<T = unknown>(event: string, handler: ObserverHandler<T>): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler as ObserverHandler);
    return () => this.off(event, handler);
  }

  off<T = unknown>(event: string, handler: ObserverHandler<T>): void {
    this.handlers.get(event)?.delete(handler as ObserverHandler);
  }

  emit<T = unknown>(event: string, payload?: T): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.forEach((h) => {
        try {
          h(payload);
        } catch (err) {
          console.error(`[EventBus] Handler error for "${event}":`, err);
        }
      });
    }
  }

  once<T = unknown>(event: string, handler: ObserverHandler<T>): void {
    const wrapped: ObserverHandler<T> = (payload) => {
      handler(payload);
      this.off(event, wrapped);
    };
    this.on(event, wrapped);
  }
}

export const eventBus = new EventBus();

export const EVENTS = {
  INDICATOR_CREATED: "indicator:created",
  INDICATOR_UPDATED: "indicator:updated",
  INDICATOR_DELETED: "indicator:deleted",
  IMPORT_STARTED: "import:started",
  IMPORT_COMPLETED: "import:completed",
  IMPORT_FAILED: "import:failed",
  REPORT_GENERATED: "report:generated",
  ENTITY_UPDATED: "entity:updated",
  NOTIFICATION: "notification:show",
  AUTH_LOGOUT: "auth:logout",
  REALTIME_UPDATE: "realtime:update",
} as const;

interface NotificationProviderProps {
  children: ReactNode;
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback(
    (n: Omit<Notification, "id" | "createdAt">) => {
      const id = `notif-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      const notification: Notification = {
        ...n,
        id,
        createdAt: new Date(),
      };
      setNotifications((prev) => [...prev, notification]);

      eventBus.emit(EVENTS.NOTIFICATION, notification);

      const duration = n.duration ?? 5000;
      if (duration > 0) {
        setTimeout(() => {
          setNotifications((prev) => prev.filter((x) => x.id !== id));
        }, duration);
      }
    },
    []
  );

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  useEffect(() => {
    const handler = (payload: Notification) => {
      addNotification(payload);
    };
    const off = eventBus.on(EVENTS.NOTIFICATION, handler);
    return () => off();
  }, [addNotification]);

  return (
    <NotificationContext.Provider
      value={{ notifications, addNotification, removeNotification, clearAll }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const ctx = useContext(NotificationContext);
  if (!ctx) {
    throw new Error("useNotifications must be used within NotificationProvider");
  }
  return ctx;
}

export function useBusEvent<T = unknown>(event: string, handler: ObserverHandler<T>) {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    const wrapped: ObserverHandler<T> = (payload) => {
      handlerRef.current(payload);
    };
    const off = eventBus.on(event, wrapped);
    return () => off();
  }, [event]);
}

export function useIndicatorsSync() {
  const [indicators, setIndicators] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchIndicators = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/indicators/", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setIndicators(data.results ?? data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error cargando indicadores");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIndicators();
  }, [fetchIndicators]);

  useBusEvent(EVENTS.INDICATOR_CREATED, () => {
    fetchIndicators();
  });

  useBusEvent(EVENTS.INDICATOR_UPDATED, () => {
    fetchIndicators();
  });

  useBusEvent(EVENTS.INDICATOR_DELETED, () => {
    fetchIndicators();
  });

  return { indicators, loading, error, refetch: fetchIndicators };
}

export function useImportProgress() {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<"idle" | "running" | "done" | "error">("idle");
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    const onStart = () => {
      setProgress(0);
      setStatus("running");
      setMessage("Importación iniciada...");
    };

    const onProgress = (p: { progress: number; message?: string }) => {
      setProgress(p.progress);
      if (p.message) setMessage(p.message);
    };

    const onDone = (p: { records: number }) => {
      setProgress(100);
      setStatus("done");
      setMessage(`${p.records} registros importados.`);
    };

    const onError = (p: { error: string }) => {
      setStatus("error");
      setMessage(p.error);
    };

    const offStart = eventBus.on(EVENTS.IMPORT_STARTED, onStart);
    const offDone = eventBus.on(EVENTS.IMPORT_COMPLETED, onDone);
    const offError = eventBus.on(EVENTS.IMPORT_FAILED, onError);

    return () => {
      offStart();
      offDone();
      offError();
    };
  }, []);

  return { progress, status, message };
}

interface IndicatorListProps {
  entityId?: number;
}

export const IndicatorList: React.FC<IndicatorListProps> = ({ entityId }) => {
  const { indicators, loading, error, refetch } = useIndicatorsSync();
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    if (entityId) {
      refetch();
    }
  }, [entityId, refetch]);

  if (loading) return <div className="loading-skeleton">Cargando indicadores...</div>;
  if (error) return <div className="error-banner">{error}</div>;

  return (
    <div className="indicator-list">
      {indicators.map((item) => (
        <div key={item.id as string} className="indicator-card">
          <button
            className="indicator-header"
            onClick={() => setExpanded(item.id === expanded ? null : (item.id as string))}
          >
            <span>{item.name as string}</span>
            <span>{(item.value as number)?.toLocaleString() ?? "—"}</span>
          </button>
          {expanded === item.id && (
            <div className="indicator-detail">
              <p>Código: {item.code}</p>
              <p>Unidad: {item.unit}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default IndicatorList;
