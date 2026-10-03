# Entertainment Releases for Home Assistant

## v0.4.3: Clearer configuration pages and theatrical sorting

- Added clearer titles and descriptions to every configuration page.
- Renamed the re-release toggle to **Exclude Theatrical Re-releases**.
- Added **Sort by Release Date** to the Theatrical Releases page.
  - On: release date ascending (soonest first).
  - Off: popularity descending (most popular first).
- Existing theatrical filters, multi-certification OR behavior, and entity IDs are unchanged.

## v0.4.2: Certification OR filtering

The Theatrical and Digital pages now support selecting multiple certifications.

Because TMDB's Discover API documents `certification` as a single value, the
integration implements true OR behavior by running one otherwise-identical
Discover query per selected certification and then merging/deduplicating the
results by TMDB movie ID.

Example:

- PG
- PG-13
- R

means:

`PG OR PG-13 OR R`

Leaving the certification selection empty means no certification filter is sent.

## v0.4.1: Optional re-release filtering

The Theatrical Releases page now includes **Exclude re-releases**.

When enabled, the integration first runs the selected TMDB Discover filters,
then keeps only titles whose TMDB primary `release_date` falls between today
and the configured theatrical look-ahead date.

This is intentionally simple and predictable:

- ON: older movies returning to theaters are filtered out.
- OFF: Home Assistant mirrors TMDB Discover results without that extra date check.

Because this uses TMDB's primary movie release date, a later wide theatrical
release can also be excluded if the movie's primary release date was earlier.
Disable the toggle if you want those cases included.

A HACS-installable Home Assistant custom integration that exposes configurable TMDB Discover feeds for movies and TV.

## v0.4.0: TMDB-first filtering

Version 0.4.0 removes custom movie-release interpretation. Movie results now come directly from TMDB Discover using the filters selected in Home Assistant.

Configure from:

**Settings → Devices & services → Entertainment Releases → Configure**

The flow has four pages:

1. Theatrical Releases
2. Digital Releases
3. TV Shows
4. General Settings

Movie pages support Country, Release Type, Days, Genres, Certification, Original Language, Minimum User Score, Minimum User Votes, and Runtime.

Multiple release types and genres use OR logic. Certifications support multi-select OR behavior by issuing one TMDB Discover request per selected certification and merging the results.

TV supports Country, Days, Streaming Services, Genres, Show Types, Original Language, Minimum User Score, Minimum User Votes, and Runtime.

## Data Source & Attribution

Entertainment Releases uses data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).

This product uses the TMDB API but is not endorsed or certified by TMDB.

Each user must obtain and configure their own TMDB API credentials. No shared TMDB API key or access token is included.

Streaming-provider availability is powered by TMDB's partnership with JustWatch. JustWatch attribution is required when provider data is used.
