export const pageNames: Record<string, string> = {
  arena: "Overview", results: "Results", cases: "Case explorer", abcd: "Support conversations",
  models: "Model guide", takeaways: "What we learned", sources: "Tests & scoring",
  chart: "Accuracy and speed", replay: "Workflow replays", run: "Run a new test", setup: "Setup",
};

export type NavigationEntry = {
  version: 1; id: string; depth: number; page: string; previousPage?: string;
  values: Record<string, unknown>; scrollY: number;
};
type Host = { history: Pick<History, "state" | "replaceState" | "pushState" | "back">;
  location: Pick<Location, "hash">; readonly scrollY: number };
const key = "jevArenaNavigation";
const pageFromHash = (hash: string) => Object.hasOwn(pageNames, hash.slice(1)) ? hash.slice(1) : "arena";
const isEntry = (entry: NavigationEntry | undefined): entry is NavigationEntry =>
  !!entry && entry.version === 1 && typeof entry.id === "string" && Object.hasOwn(pageNames, entry.page)
  && Number.isInteger(entry.depth) && entry.depth >= 0 && Number.isFinite(entry.scrollY)
  && !!entry.values && typeof entry.values === "object";
const makeEntry = (page: string): NavigationEntry => ({ version: 1, id: crypto.randomUUID(), depth: 0, page, values: {}, scrollY: 0 });

/** Only UI choices live in history; fetched evidence stays in the existing caches. */
export function createNavigation(host: Host, publish: (entry: NavigationEntry, restore: boolean) => void) {
  let current = isEntry(host.history.state?.[key]) ? host.history.state[key] as NavigationEntry : makeEntry(pageFromHash(host.location.hash));
  const write = (method: "pushState" | "replaceState") =>
    host.history[method]({ ...host.history.state, [key]: current }, "", `#${current.page}`);
  return {
    get current() { return current; },
    start() { write("replaceState"); },
    set<T>(name: string, update: T | ((old: T) => T), fallback: T) {
      const old = Object.hasOwn(current.values, name) ? current.values[name] as T : fallback;
      const next = typeof update === "function" ? (update as (old: T) => T)(old) : update;
      if (Object.is(old, next)) return;
      current = { ...current, values: { ...current.values, [name]: next } };
      write("replaceState"); publish(current, false);
    },
    saveScroll() {
      if (current.scrollY === host.scrollY) return;
      current = { ...current, scrollY: host.scrollY }; write("replaceState");
    },
    navigate(page: string, values: Record<string, unknown> = {}) {
      if (!Object.hasOwn(pageNames, page)) return;
      if (current.page === page) {
        current = { ...current, values: { ...current.values, ...values } };
        write("replaceState"); publish(current, false); return;
      }
      // Snapshot the source before applying destination filters.
      this.saveScroll();
      current = { ...makeEntry(page), depth: current.depth + 1, previousPage: current.page,
        values: { ...current.values, ...values } };
      write("pushState"); publish(current, true);
    },
    pop(state: unknown) {
      const candidate = (state as Record<string, NavigationEntry> | null)?.[key];
      current = isEntry(candidate) ? candidate : makeEntry(pageFromHash(host.location.hash));
      publish(current, true);
    },
    back() { if (current.depth > 0) host.history.back(); },
  };
}
