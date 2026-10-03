# Entertainment Releases for Home Assistant

A HACS-installable Home Assistant custom integration that creates a configurable movie and TV release feed using TMDB.

## Features

- Theatrical movie releases
- Digital movie releases
- TV shows airing
- Independent 1–30 day look-ahead windows for each category
- Configurable 1–24 hour refresh interval
- Home Assistant UI configuration
- Automatic integration reload when options change
- Pagination across TMDB discover results
- Filters theatrical results to the first theatrical release in the configured region
- Poster paths, ratings, overviews, release dates, and TMDB links in sensor attributes

## Default settings

- Theatrical releases: 7 days
- Digital releases: 1 day
- TV releases: 1 day
- Refresh interval: 6 hours

All settings can be changed from:

**Settings → Devices & services → Entertainment Releases → Configure**

## Installation with HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open the menu and choose **Custom repositories**.
4. Add:
   `https://github.com/taikowolfsbane/entertainment-release`
5. Choose **Integration** as the repository type.
6. Download **Entertainment Releases**.
7. Restart Home Assistant.
8. Go to **Settings → Devices & services → Add Integration**.
9. Search for **Entertainment Releases**.
10. Enter your own TMDB API Read Access Token and region.

Each user must provide their own TMDB credentials. No shared API token is included in this repository.

## Sensors

The integration currently creates:

- Movies in Theaters
- Movies Released Digitally
- TV Shows Airing

The sensor state is the number of matching titles. The `items` attribute contains structured release information.

## Data Source & Attribution

Entertainment Releases uses data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).

This product uses the TMDB API but is not endorsed or certified by TMDB.

Each user of this integration must obtain and configure their own TMDB API credentials. No shared TMDB API key or access token is included with this project.

This project is intended for personal, non-commercial use. Users are responsible for ensuring that their use of TMDB data complies with TMDB's API terms and policies.

If streaming-provider availability is displayed in a future version, that availability data may be provided through TMDB's partnership with JustWatch and should be attributed to JustWatch where applicable.

## Theatrical release filtering

For theatrical results, the integration validates each candidate against TMDB's regional release history. A title is kept only when the candidate date matches its earliest limited or standard theatrical release in the configured region. This is intended to remove later re-releases, anniversary runs, restorations, and similar return engagements.

If TMDB has no usable regional theatrical history for a candidate, the integration keeps the candidate rather than silently discarding it.

## Roadmap

- Episode-level TV releases
- Watch-provider availability
- Configurable streaming providers
- Streaming release-date correlation
- Dedicated Lovelace card
- Daily digest notifications
- Coming-soon views
