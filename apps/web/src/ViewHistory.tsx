import { createContext, useContext, useEffect, useLayoutEffect, useRef, useState, useCallback, type ReactNode, type Dispatch, type SetStateAction } from "react";
import { createNavigation, pageNames, type NavigationEntry } from "./navigation";

type Controller = ReturnType<typeof createNavigation>;
const Context = createContext<{ controller: Controller; entry: NavigationEntry } | null>(null);

export function NavigationProvider({ children }: { children: ReactNode }) {
  const restoring = useRef(true);
  const [controller] = useState(() => createNavigation(window, (entry, restore) => {
    if (restore) restoring.current = true;
    setEntry(entry);
  }));
  const [entry, setEntry] = useState(controller.current);

  useEffect(() => {
    controller.start();
    const previous = window.history.scrollRestoration;
    window.history.scrollRestoration = "manual";
    const pop = (event: PopStateEvent) => controller.pop(event.state);
    let timer: ReturnType<typeof setTimeout>;
    const scroll = () => {
      clearTimeout(timer);
      if (!restoring.current) timer = setTimeout(() => { if (!restoring.current) controller.saveScroll(); }, 150);
    };
    const save = () => { if (!restoring.current) controller.saveScroll(); };
    window.addEventListener("popstate", pop);
    window.addEventListener("scroll", scroll, { passive: true });
    window.addEventListener("pagehide", save);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("popstate", pop);
      window.removeEventListener("scroll", scroll);
      window.removeEventListener("pagehide", save);
      window.history.scrollRestoration = previous;
    };
  }, [controller]);

  useLayoutEffect(() => {
    let frame = 0;
    const stop = () => { restoring.current = false; observer.disconnect(); cancelAnimationFrame(frame); };
    const restore = () => {
      if (!restoring.current) return;
      window.scrollTo({ top: entry.scrollY, behavior: "instant" });
      if (Math.abs(window.scrollY - entry.scrollY) < 2) stop();
    };
    // Results can arrive after the page mounts. Restore again when that content gives the page its height.
    const observer = new ResizeObserver(() => { cancelAnimationFrame(frame); frame = requestAnimationFrame(restore); });
    observer.observe(document.getElementById("root")!);
    frame = requestAnimationFrame(restore);
    window.addEventListener("wheel", stop, { passive: true });
    window.addEventListener("touchstart", stop, { passive: true });
    window.addEventListener("keydown", stop);
    return () => {
      observer.disconnect(); cancelAnimationFrame(frame);
      window.removeEventListener("wheel", stop);
      window.removeEventListener("touchstart", stop);
      window.removeEventListener("keydown", stop);
    };
  }, [entry.id]);

  return <Context.Provider value={{ controller, entry }}>{children}</Context.Provider>;
}

export function useNavigation() {
  const context = useContext(Context);
  if (!context) throw new Error("NavigationProvider is required");
  const { controller, entry } = context;
  return { page: entry.page, navigate: controller.navigate.bind(controller), back: () => controller.back(),
    canGoBack: entry.depth > 0, backLabel: pageNames[entry.previousPage || ""] || "previous view" };
}

export function useViewState<T>(name: string, fallback: T): [T, Dispatch<SetStateAction<T>>] {
  const context = useContext(Context);
  if (!context) throw new Error("NavigationProvider is required");
  const { controller, entry } = context;
  const initial = useRef({ name, value: fallback });
  if (initial.current.name !== name) initial.current = { name, value: fallback };
  const set = useCallback((update: SetStateAction<T>) => controller.set(name, update, initial.current.value), [controller, name]);
  return [Object.hasOwn(entry.values, name) ? entry.values[name] as T : initial.current.value, set];
}
