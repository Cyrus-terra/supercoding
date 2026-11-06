import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createSearch } from './search.mjs';

function setup() {
  const requests = [];
  const controller = createSearch(() => new Promise((resolve, reject) => {
    requests.push({ resolve, reject });
  }));
  return { ...controller, requests };
}

test('older success cannot replace newer results', async () => {
  const { state, search, requests } = setup();
  const old = search('old');
  const latest = search('latest');
  requests[1].resolve(['latest']);
  await latest;
  requests[0].resolve(['old']);
  await old;
  assert.deepEqual(state.results, ['latest']);
  assert.equal(state.loading, false);
});

test('older finally cannot clear current loading', async () => {
  const { state, search, requests } = setup();
  const old = search('old');
  const latest = search('latest');
  requests[0].resolve(['old']);
  await old;
  assert.equal(state.loading, true);
  requests[1].resolve(['latest']);
  await latest;
  assert.deepEqual(state.results, ['latest']);
  assert.equal(state.loading, false);
});

test('older failure cannot replace current error state', async () => {
  const { state, search, requests } = setup();
  const old = search('old');
  const latest = search('latest');
  requests[1].resolve(['latest']);
  await latest;
  requests[0].reject(new Error('old failure'));
  await old;
  assert.equal(state.error, null);
  assert.deepEqual(state.results, ['latest']);
});

test('current failure is shown and a later search recovers', async () => {
  const { state, search, requests } = setup();
  const failed = search('failed');
  const error = new Error('current failure');
  requests[0].reject(error);
  await failed;
  assert.equal(state.error, error);
  assert.equal(state.loading, false);
  const recovered = search('recovered');
  assert.equal(state.error, null);
  requests[1].resolve(['recovered']);
  await recovered;
  assert.deepEqual(state.results, ['recovered']);
  assert.equal(state.loading, false);
});
