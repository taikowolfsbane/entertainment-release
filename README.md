# Entertainment Releases for Home Assistant

A HACS-installable Home Assistant custom integration that builds a useful movie and TV release feed using TMDB.

## v0.3.0 highlights

### Theatrical movies
- Configurable 1–30 day future window
- Region-aware theatrical dates
- First theatrical/limited-theatrical release validation to remove later re-releases
- Original-language filtering
- Configurable minimum TMDB user score
- Upcoming unrated titles are retained so legitimate future releases are not hidden
- Sorted by release date, then popularity

### Digital movies
- Configurable 1–30 day window
- Shows a movie only on its **first digital release date** in the configured region
- Prior theatrical releases do not disqualify the movie
- Later digital reissues do not appear as new digital releases
- Original-language filtering

### TV
- Configurable 1–30 day window
- Subscription-streaming provider filtering
- Defaults to common U.S. services such as Netflix, Prime Video, Hulu, Disney+, Apple TV+, Peacock, Paramount+, and Max
- Scripted series and miniseries only by default
- Original-language filtering
- Optional genre selection
- Multiple streaming providers use OR logic
- Multiple genres use OR logic
- Provider group and genre group combine with AND logic

### General
- Configurable 1–24 hour refresh interval
- TMDB pagination
- Poster URLs included in sensor attributes
- Existing entity unique IDs preserved across upgrade

## Default settings

- Theatrical: 7 days
- Digital: 1 day
- TV: 1 day
- Refresh: 6 hours
- Movie original language: English (`en`)
- Minimum theatrical user score: 1.0
- TV original language: English (`en`)
- TV types: Scripted and Miniseries
- TV provider filtering: enabled with common U.S. subscription services

Change settings from:

**Settings → Devices & services → Entertainment Releases → Configure**

## Installation with HACS

Repository:

`https://github.com/taikowolfsbane/entertainment-release`

Each user must supply their own TMDB API Read Access Token.

## Sensors

- Movies in Theaters
- Movies Released Digitally
- TV Shows Airing

The sensor state is the number of matching titles. Detailed results are stored in the `items` attribute.

## Data Source & Attribution

Entertainment Releases uses data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).

This product uses the TMDB API but is not endorsed or certified by TMDB.

Each user must obtain and configure their own TMDB API credentials. No shared TMDB API key or access token is included with this project.

This project is intended for personal, non-commercial use. Users are responsible for ensuring that their use of TMDB data complies with TMDB's API terms and policies.

Streaming-provider availability data is powered by TMDB's partnership with JustWatch. **JustWatch attribution is required** when using that provider data.

## Notes

TMDB data can occasionally be incomplete or corrected after the fact. When release-history data is missing, the integration favors retaining a candidate instead of silently hiding a potentially legitimate release.

TV provider availability identifies where a show is currently available through TMDB/JustWatch; it does not by itself prove the exact date a service added that show. This integration combines provider availability with the show's air-date window to create a more useful daily streaming-oriented TV feed.
