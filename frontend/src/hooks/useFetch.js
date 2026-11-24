import { useEffect, useState } from 'react';

/**
 * Small data-fetching helper: exposes loading / data / error and a reload function.
 * `deps` behaves like useEffect dependencies; fetcher identity is intentionally ignored.
 */
export function useFetch(fetcher, deps = []) {
  const [tick, setTick] = useState(0);
  const [state, setState] = useState({ data: null, loading: true, error: null });

  useEffect(() => {
    let cancelled = false;
    setState({ data: null, loading: true, error: null });

    Promise.resolve()
      .then(fetcher)
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((error) => {
        if (!cancelled) setState({ data: null, loading: false, error });
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  return { ...state, reload: () => setTick((value) => value + 1) };
}
