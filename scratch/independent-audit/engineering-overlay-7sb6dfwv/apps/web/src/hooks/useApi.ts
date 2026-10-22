import { useEffect, useState } from "react";

export function useApi<T>(loader: () => Promise<T>, dependencies: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    loader()
      .then((value) => { if (active) setData(value); })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : "Something went wrong");
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
    // Callers provide stable primitive dependencies for intentionally reloading requests.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return { data, error, loading };
}

