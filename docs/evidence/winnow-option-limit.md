# Winnow option-limit incident and correction

The frozen Full v2 run advertised 255 choices for Winnow, inheriting Arena's default. The pinned native server actually accepts 2–64 alternatives. This was a harness capability-discovery error.

Evidence: upstream pinned source `native/protocol.h` rejects inputs outside 2–64; `native/engine.h` defines 64 label tokens; its `scripts/check_http.py` expects HTTP 400 for 65 choices. The pinned native checkout is preserved with the local run dependencies.

Exactly 500 main predictions failed with HTTP 400, all BANKING77 with 77 choices. Each follow-up condition repeated 13 of those cases, giving 26 further failures. These are unsupported native capacity, not wrong selected labels or nondeterminism. No label-reduction workaround was used.

The historical manifest, raw records and primary denominators remain unchanged. The shared 4,635-reference comparison already excludes BANKING77 because Plumb/SemIf cannot accept that label space. It is unaffected. The explicitly post-hoc sensitivity on 5,171 capacity-compatible references gives Jev 4,818 strict / 4,852 label matches and Winnow 4,813 for both. This is descriptive, not a replacement primary leaderboard.

After candidate work finished, Arena's future registry was corrected to `max_options=64`. A boundary regression test verifies 64 options reach the worker and 65 are rejected before a request. The targeted wire, scoring, export and boundary tests passed: **25/25**. No historical predictions were repeated or rewritten.
