# ETF holdings fixtures

Hand-built samples that mimic the layout of the sponsor files (iShares CSV with a metadata block,
a non-breaking-space separator line, a header starting with `Ticker`, a cash row and a disclaimer).
Weights and share counts are invented; only the layout matters. The SSGA layout is exercised with
in-memory worksheet rows in `tests/test_listings_universe.py`.
