# Project Conclusion: US Top 50 Playlist Performance Analysis

## Project Overview

This project analyzed historical Spotify US Top 50 playlist data to
understand song popularity, chart performance, song longevity, and
artist presence over time. The analysis is descriptive and focuses on
historical trends rather than prediction or recommendation.

## Dataset

-   **Period covered:** 18 May 2024 -- 27 November 2025
-   **Cleaned records:** 27,750 daily chart entries
-   **Songs represented:** 977
-   **Artist entries:** 297
-   **Daily coverage:** 50 tracks per day
-   **Data quality:** 50 duplicate rows were removed; dates and ranking
    values were validated.

## Key Findings

-   **Song longevity:** "Something in the Orange" by Zach Bryan had the
    longest observed chart presence at 536 days.
-   **Artist presence:** Taylor Swift had the most unique songs (96) and
    the largest share of playlist appearances (7.26%).
-   **Popularity and ranking:** Popularity and chart rank had a very
    weak relationship (correlation: -0.094). A high popularity score did
    not necessarily mean a song held a high chart position.
-   **Peak rank and longevity:** Best rank and days on chart had a
    moderate negative relationship (correlation: -0.342), suggesting
    songs reaching stronger peak positions tended to remain longer,
    though this was not guaranteed.
-   **Content type:** Singles had the highest average popularity
    (90.13), followed by albums (86.68). Compilation tracks had a lower
    average (78.38), but the compilation sample was small.
-   **Explicit content:** Explicit tracks made up 47.94% of entries.
    Average popularity was similar for explicit and non-explicit tracks.
-   **Track duration:** Duration had almost no relationship with
    popularity or chart rank.
-   **Chart movement:** Songs sometimes changed position sharply between
    consecutive daily snapshots, showing that playlist rankings can be
    volatile.

## Business implications and recommendations

1.  **Track longevity alongside peak rank.** Use days on chart, average
    rank, and best rank together to distinguish sustained performers
    from short-lived peaks.
2.  **Monitor artist presence through multiple measures.** Unique songs,
    distinct days, and playlist-record share reveal different aspects of
    artist visibility.
3.  **Avoid using popularity as a proxy for rank.** The observed
    correlation of -0.094 is too weak to support that interpretation.
4.  **Treat the single-versus-album result as an observed pattern.**
    Investigate it by artist, time period, and release context before
    making campaign or release-strategy decisions.
5.  **Do not over-interpret small group differences.** Explicit-content
    averages are close, and the compilation category contains only eight
    unique songs.
6.  **Use rank-movement alerts for monitoring.** The reported movements
    of up to 48 positions suggest that large changes can be worth
    investigating, while checking whether the movement spans consecutive
    calendar days.
7.  **Keep descriptive findings separate from causal claims.** The
    dataset does not include all potential drivers of playlist
    placement, such as marketing activity, promotion, release dates, or
    streaming counts.

## Overall Conclusion

The analysis shows that playlist success is influenced by more than
popularity scores alone. Strong peak rankings were associated with
longer chart presence, while artist activity and repeated appearances
varied substantially over time. Taylor Swift led in both unique songs
and overall playlist share, while Zach Bryan showed particularly strong
longevity. Singles performed better on average than album and
compilation tracks in this dataset.

The findings describe patterns in the observed playlist data; they do
not establish causes or predict future chart performance.

## Notes

Results depend on the available observation period and the definitions
used for song identity, artist attribution, chart movement, and
performance metrics. Songs already present at the start or still present
at the end of the dataset may have incomplete observed chart lifetimes.
Artist names in collaborations may also affect artist-level counts.

