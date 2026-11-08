// Pace received text without delaying the network reader or changing saved answers.
export function createAnswerReveal(onText: (text: string) => void) {
  let target = '', shown = '', timer: ReturnType<typeof setTimeout> | null = null;
  let resolve: (() => void) | null = null;
  let stopped = false;
  const tick = () => {
    timer = null;
    if (stopped) return;
    if (!target.startsWith(shown)) shown = ''; // Final summary can correct deltas.
    const rest = Array.from(target.slice(shown.length));
    shown += rest.slice(0, 6).join('');
    onText(shown);
    if (shown !== target) timer = setTimeout(tick, 24);
    else if (resolve) { const done = resolve; resolve = null; done(); }
  };
  const schedule = () => { if (!stopped && timer === null) timer = setTimeout(tick, 0); };
  return {
    update(text: string) { target = text; schedule(); },
    finish(text: string): Promise<void> {
      if (stopped) return Promise.resolve();
      target = text;
      return new Promise(done => { resolve = done; schedule(); });
    },
    cancel() {
      stopped = true;
      if (timer !== null) clearTimeout(timer);
      resolve?.(); resolve = null;
    },
  };
}
