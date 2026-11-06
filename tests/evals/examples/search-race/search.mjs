export function createSearch(fetchResults) {
  const state = { results: [], loading: false, error: null };

  async function search(keyword) {
    state.loading = true;
    state.error = null;
    try {
      state.results = await fetchResults(keyword);
    } catch (error) {
      state.error = error;
    } finally {
      state.loading = false;
    }
  }

  return { state, search };
}
