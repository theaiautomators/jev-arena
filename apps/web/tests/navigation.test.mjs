import assert from 'node:assert/strict';
import test from 'node:test';
import { createNavigation } from '../src/navigation.ts';

function fixture(hash = '') {
  const entries = [{ state: { unrelated: 'preserve me' }, hash }];
  let index = 0;
  const host = { scrollY: 0, location: { hash }, history: {
    get state() { return entries[index].state; },
    replaceState(state, _, hash) { entries[index] = { state: structuredClone(state), hash }; host.location.hash = hash; },
    pushState(state, _, hash) { entries.splice(++index); entries.push({ state: structuredClone(state), hash }); host.location.hash = hash; },
    back() { move(-1); },
  }};
  const published = [];
  const nav = createNavigation(host, (entry, restore) => published.push({ entry, restore }));
  function move(delta) { index += delta; host.location.hash = entries[index].hash; nav.pop(entries[index].state); }
  nav.start();
  return { host, nav, published, entries, move };
}

test('Back restores the exact Results snapshot; Forward restores the explored cases', () => {
  const { host, nav, move } = fixture();
  nav.navigate('results');
  nav.set('runId', 'saved-run', null);
  nav.set('analysis:saved-run:group', 'Classification::BANKING77', '::');
  nav.set('analysis:saved-run:model', 'jev', '');
  nav.set('analysis:saved-run:scope', 'supported', 'shared');
  nav.set('analysis:saved-run:metric', 'strict', 'label');
  host.scrollY = 810;
  nav.navigate('cases', { caseDataset: 'arena', 'cases:saved-run:filters': { family: 'BANKING77', model: 'jev', offset: 0 } });
  assert.equal(nav.current.previousPage, 'results');
  nav.set('cases:saved-run:filters', old => ({ ...old, offset: 30 }), {});
  nav.set('cases:saved-run:chosen', 'case-42', '');
  nav.back();
  assert.equal(nav.current.page, 'results');
  assert.equal(nav.current.scrollY, 810);
  assert.deepEqual(nav.current.values, { runId: 'saved-run', 'analysis:saved-run:group': 'Classification::BANKING77',
    'analysis:saved-run:model': 'jev', 'analysis:saved-run:scope': 'supported', 'analysis:saved-run:metric': 'strict' });
  move(1);
  assert.equal(nav.current.page, 'cases');
  assert.equal(nav.current.values['cases:saved-run:filters'].offset, 30);
  assert.equal(nav.current.values['cases:saved-run:chosen'], 'case-42');
});

test('ABCD and its filters survive Back and reloading a history entry', () => {
  const { host, nav } = fixture('#results');
  nav.set('resultsAssessment', 'abcd', 'arena');
  nav.set('abcd:condition', 'retrieved_policy', 'full_handbook');
  nav.set('abcd:task', 'action', 'combined');
  nav.set('abcd:model', 'nimble', '');
  nav.navigate('cases', { caseDataset: 'abcd' });
  nav.back();
  const reloaded = createNavigation(host, () => {});
  assert.equal(reloaded.current.page, 'results');
  assert.equal(reloaded.current.values.resultsAssessment, 'abcd');
  assert.equal(reloaded.current.values['abcd:condition'], 'retrieved_policy');
  assert.equal(reloaded.current.values['abcd:task'], 'action');
  assert.equal(reloaded.current.values['abcd:model'], 'nimble');
  assert.equal(host.history.state.unrelated, 'preserve me');
});

test('Filters and same-page navigation replace history; a new destination after Back replaces the forward branch', () => {
  const { nav, entries, move } = fixture();
  nav.navigate('results');
  nav.set('model', 'jev', '');
  nav.navigate('results', { model: 'laya' });
  assert.equal(entries.length, 2);
  nav.navigate('cases');
  move(-1);
  nav.navigate('models');
  assert.equal(entries.length, 3);
  assert.equal(nav.current.previousPage, 'results');
  assert.equal(nav.current.depth, 2);
});

test('Direct links have a safe root and unrelated hashes do not become pages', () => {
  const direct = fixture('#cases');
  assert.equal(direct.nav.current.page, 'cases');
  direct.nav.back();
  assert.equal(direct.nav.current.depth, 0);
  assert.equal(fixture('#taia-main').nav.current.page, 'arena');
});
