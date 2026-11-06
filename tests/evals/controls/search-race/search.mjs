export function createSearch(fetchResults) {
  const state = { results: [], loading: false, error: null };
  let sequence = 0;

  async function search(keyword) {
    const current = ++sequence;
    state.loading = true;
    state.error = null;
    try {
      const results = await fetchResults(keyword);
      if (current === sequence) state.results = results;
    } catch (error) {
      if (current === sequence) state.error = error;
    } finally {
      if (current === sequence) state.loading = false;
    }
  }

  return { state, search };
}
