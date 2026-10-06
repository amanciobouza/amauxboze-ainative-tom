import { useCallback, useEffect, useState } from "react";

export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method,
    headers:
      body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok)
    throw new Error(
      result.error?.message || `Anfrage fehlgeschlagen (${response.status})`,
    );
  return result as T;
}

export function useResource<T>(path: string | null, interval = 6000) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refresh, setRefresh] = useState(0);
  const reload = useCallback(() => setRefresh((v) => v + 1), []);
  useEffect(() => {
    let alive = true;
    setLoading(true);
    setData(null);
    setError(null);
    if (path === null) {
      setLoading(false);
      return;
    }
    const load = () =>
      api<T>(path)
        .then((value) => {
          if (alive) {
            setData(value);
            setError(null);
            setLoading(false);
          }
        })
        .catch((e) => {
          if (alive) {
            setError(e.message);
            setLoading(false);
          }
        });
    void load();
    const timer = interval ? setInterval(load, interval) : null;
    return () => {
      alive = false;
      if (timer) clearInterval(timer);
    };
  }, [path, interval, refresh]);
  return { data, error, loading, reload };
}

export const identity = () => crypto.randomUUID();
