# Packaged market data provenance

- Series: S&P 500 [SP500], daily closing price index, not seasonally adjusted, no dividends.
- Original provider: S&P Dow Jones Indices LLC.
- Distributor: FRED, Federal Reserve Bank of St. Louis.
- Series notes: https://fred.stlouisfed.org/series/SP500
- Exact CSV request: https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2020-02-01&coed=2020-04-30
- Download date: 2026-10-30.
- Packaged path: `src/atlas/data/sp500_2020.csv`.
- SHA-256: `92ff16beefb4f87dddf221faac16812121a5420f8671542fc164f90df55af6e5`.
- Bytes: 1,225. CSV stored unchanged from the downloaded response.
- 64 weekday rows, 62 numeric closes. February 17 and April 10 are blank; weekends
  are absent. Analysis drops missing closes and never fills, interpolates or fabricates values.
- Full requested Feb–Apr 2020 window is bundled, so launches never request live prices.

The downloaded values were cross-checked against FRED's public table:
https://fred.stlouisfed.org/data/SP500 (February 19: 3386.15; March 23: 2237.40;
April 30: 2912.43). Those dates are actual observation dates, independent of demo date.

FRED's series notes attribute copyright to S&P Dow Jones Indices LLC and specify
restrictions on reproduction. Attribution does not grant an open-data license. This
small historical evaluation fixture is not presented as freely licensed market data;
review the provider's terms before redistributing or using it commercially. Code licensing
does not relicense the index observations. No fallback or invented series was needed.
