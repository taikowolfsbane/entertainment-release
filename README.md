# Entertainment Releases

A custom Home Assistant integration for tracking upcoming movie and TV releases using data from [The Movie Database (TMDB)](https://www.themoviedb.org/).

Entertainment Releases turns TMDB Discover data into useful Home Assistant sensors that can be displayed in dashboards, Markdown cards, automations, and other Home Assistant views.

The integration currently supports:

- New and upcoming theatrical movie releases
- New regional Digital movie releases
- Optional movie provider and rent/buy/stream availability filtering
- TV shows airing within a configurable date range
- Season and episode details for TV releases
- Country and region filtering
- Release-type filtering
- Genre filtering
- Multi-certification filtering
- Language filtering
- Minimum user score and vote-count filters
- Runtime filtering
- Streaming-service filtering for TV
- Configurable watch-availability types for TV
- Multiple TV origin countries
- TV show-type filtering
- TV keyword exclusions
- Optional theatrical re-release filtering
- Sorting theatrical results by popularity or release date
- Configurable 1–30 day release windows
- Configurable refresh interval

Each Home Assistant installation uses its own TMDB API Read Access Token.

---

## Installation

### Install with HACS

Entertainment Releases can be installed as a custom repository in HACS.

Repository:

`https://github.com/taikowolfsbane/entertainment-release`

1. Open **HACS** in Home Assistant.
2. Open **Integrations**.
3. Select the three-dot menu in the upper-right corner.
4. Choose **Custom repositories**.
5. Enter:

   `https://github.com/taikowolfsbane/entertainment-release`

6. Select **Integration** as the repository type.
7. Add the repository.
8. Search for **Entertainment Releases** in HACS.
9. Install the integration.
10. Restart Home Assistant.

After restarting, continue with the setup steps below.

---

## TMDB API Setup

Entertainment Releases requires a free TMDB account and a TMDB API Read Access Token.

1. Create or sign in to your TMDB account.
2. Open your TMDB account settings.
3. Go to the API section.
4. Request API access if you have not already done so.
5. Copy your **API Read Access Token**.

The integration expects the longer **API Read Access Token / Bearer Token**, not only the shorter legacy v3 API key.

Each user supplies their own TMDB credentials. No shared API key or access token is included with this project.

---

## Add the Integration to Home Assistant

After installing through HACS and restarting Home Assistant:

1. Go to **Settings → Devices & services**.
2. Select **Add Integration**.
3. Search for **Entertainment Releases**.
4. Enter your TMDB API Read Access Token.
5. Enter your default region, such as:

   `US`

6. Complete setup.

After setup, open:

**Settings → Devices & services → Entertainment Releases → Configure**

to customize each release category.

---

# Configuration

Configuration is split into separate pages so each type of content can be tuned independently.

## Theatrical Releases

The theatrical page controls the movies shown in the **New & Upcoming Theatrical Releases** sensor. This feed covers movies releasing today through the configured number of future days; it is not intended to represent every movie currently playing in theaters.

Available filters include:

- **Country**
- **Release Type**
  - Premiere
  - Theatrical (Limited)
  - Theatrical
  - Digital
  - Physical
  - TV
- **Days**
  - 1–30 days
- **Genres**
- **Certifications**
  - NR
  - G
  - PG
  - PG-13
  - R
  - NC-17
- **Original Language**
- **Minimum User Score**
- **Minimum User Votes**
- **Minimum Runtime**
- **Maximum Runtime**
- **Exclude Theatrical Re-releases**
- **Sort by Release Date**

### Exclude Theatrical Re-releases

When enabled, older movies returning to theaters are filtered out when TMDB's returned primary release date falls outside the configured theatrical date window.

This is useful for excluding anniversary screenings, restorations, and other theatrical re-releases.

Because this uses TMDB's primary movie release date, some legitimate later theatrical rollouts can also be filtered out. Disable the option if you want TMDB's Discover results without this additional check.

### Theatrical Sorting

**Sort by Release Date enabled**

Movies are ordered from the soonest release date to the latest.

**Sort by Release Date disabled**

Movies are ordered by TMDB popularity, with the most popular titles shown first.

---

## New Digital Releases

The digital page is designed to answer a simple question:

**Which movies have a new TMDB Digital release date in my selected region?**

Entertainment Releases always uses TMDB release type **Digital (type 4)** for
this sensor. The release type is no longer user-selectable on this page.

Available filters include:

- **Release / Watch Region**
- **Digital Release Window**
  - 1–30 days
- **Services**
- **Availability Types**
  - Subscription
  - Free
  - Ads
  - Rent
  - Buy
- **Genres**
- **Certifications**
- **Original Language**
- **Minimum User Score**
- **Minimum User Votes**
- **Minimum Runtime**
- **Maximum Runtime**

### How the Digital Date Works

TMDB's Discover API supports using `region` together with
`with_release_type=4`.

When these are combined, TMDB uses the matching regional Digital release date
for the Discover result. Entertainment Releases then limits that date to the
configured window.

For example, a movie may have:

- Theatrical release: August 14
- Digital release: October 6

If the integration is configured for the United States and October 6 falls
inside the selected Digital Release Window, the movie can appear in the New
Digital Releases sensor with October 6 as its release date.

### Services and Availability Types

The Services filter is optional.

If no services are selected, the integration shows qualifying new Digital
releases regardless of provider.

If services are selected, a movie must also currently be available from at
least one selected provider in the configured watch region.

Availability Types can include:

- Subscription
- Free
- Ads
- Rent
- Buy

The default is:

- Subscription
- Rent
- Buy

Multiple services and multiple availability types use OR logic within their
respective groups.

This approach does **not** claim that a movie was added to a specific service
for the first time on that date. The date represents TMDB's regional Digital
release date, while provider data represents current availability.


---

## Certification Filtering

Theatrical and Digital releases support selecting multiple certifications.

For example:

`PG, PG-13, R`

behaves like:

`PG OR PG-13 OR R`

TMDB's Discover API accepts one certification per request, so Entertainment Releases runs one otherwise-identical TMDB query for each selected certification, then merges and deduplicates the results by TMDB movie ID.

Leaving the certification selection empty disables certification filtering.

---

## Genre Filtering

Multiple genres use OR logic.

For example, selecting:

- Action
- Comedy
- Science Fiction

means:

`Action OR Comedy OR Science Fiction`

rather than requiring a title to match every selected genre.

---

## TV Shows

The TV configuration page controls the shows shown in the TV sensor.

Available filters include:

- **Watch Region**
- **Origin Countries**
- **Days**
- **Streaming Services**
- **Availability Types**
- **Genres**
- **Show Types**
- **Original Language**
- **Minimum User Score**
- **Minimum User Votes**
- **Minimum Runtime**
- **Maximum Runtime**
- **Exclude Keywords**

### Watch Region

**Watch Region** controls where TMDB checks streaming-provider availability.

This is a single selection.

Example:

`United States`

If you live in the U.S. and want to know where a show can be watched in the U.S., keep the watch region set to United States even if the show itself originated in another country.

### Origin Countries

**Origin Countries** controls where the show itself originated.

This is a multi-select.

For example:

- United States
- United Kingdom

allows both U.S. and British shows to appear while still using **United States** as the watch region.

This is useful for shows such as British productions that are available on U.S. streaming services.

Leaving Origin Countries empty removes the origin-country restriction.

### Streaming Services

Entertainment Releases uses TMDB's watch-provider data to narrow TV results to selected services.

Common U.S. providers include:

- Netflix
- Amazon Prime Video
- Hulu
- Disney+
- Apple TV+
- Peacock
- Paramount+
- Max

Multiple selected providers use OR logic.

For example:

`Netflix OR Hulu OR Max`

### Availability Types

TV results can also be filtered by how a show is available in the selected watch region.

Available options are:

- **Subscription**
- **Free**
- **Ads**
- **Rent**
- **Buy**

Multiple selections use OR logic.

For example:

`Subscription OR Rent OR Buy`

The default is **Subscription**.

### Show Types

TV results can be filtered by TMDB show type, including:

- Documentary
- News
- Miniseries
- Reality
- Scripted
- Talk Show
- Video

The default selection is:

- Miniseries
- Scripted

This helps reduce noise from news, talk shows, reality shows, and similar programming.

### Exclude Keywords

The TV page includes an **Exclude Keywords** field.

Enter comma-separated TMDB keyword names, for example:

`Cooking, late-night show, concert`

When the configuration is saved, Entertainment Releases resolves those names through TMDB's keyword search endpoint and applies the resulting IDs through TMDB's native `without_keywords` filter.

A show is excluded if it matches any configured keyword.

This is useful for excluding categories that are difficult to eliminate using genre or show-type filters alone.

---

## General Settings

The General Settings page currently includes:

- **Refresh Interval**

The refresh interval can be configured from **1 to 24 hours**.

The default is:

`6 hours`

Home Assistant performs an immediate refresh when the integration is loaded and then refreshes again at the configured interval.

---

# Home Assistant Sensors

Entertainment Releases creates three sensors.

Depending on your Home Assistant entity registry, the entity IDs may appear similar to:

- `sensor.entertainment_releases_movies_in_theaters_today` — New & Upcoming Theatrical Releases
- `sensor.entertainment_releases_movies_released_digitally_today`
- `sensor.entertainment_releases_tv_shows_airing_today`

Existing entity unique IDs are preserved during upgrades so dashboards should not need to be rebuilt when updating the integration.

The sensor state is the number of matching releases.

Detailed release information is stored in the sensor's `items` attribute.

---

## Movie Attributes

Movie entries may include:

- TMDB ID
- Title
- Overview
- Poster path
- Poster URL
- Backdrop path
- Release date
- User score
- Vote count
- Popularity
- Genre IDs
- Original language
- TMDB URL

Example:

```yaml
id: 123456
title: Example Movie
release_date: "2026-10-03"
vote_average: 7.4
vote_count: 125
popularity: 48.2
poster_path: /example.jpg
poster_url: https://image.tmdb.org/t/p/w342/example.jpg
```

---

## TV Attributes

TV entries may include:

- TMDB ID
- Name
- Overview
- Poster path
- Poster URL
- Backdrop path
- First air date
- User score
- Vote count
- Popularity
- Genre IDs
- Origin countries
- Original language
- TMDB URL

---


## TV Episode Details

For each TV series returned by TMDB Discover, Entertainment Releases also
looks up the episode or episodes whose air dates fall inside the configured
TV date window.

Each TV item includes an `episodes` list.

Example:

```yaml
name: Transformers: CYBERWORLD
episode_count: 1
season_number: 2
episode_number: 4
episode_name: Energon Surge
episode_air_date: "2026-10-03"
episode_code: S02E04
episodes:
  - season_number: 2
    episode_number: 4
    episode_code: S02E04
    name: Energon Surge
    air_date: "2026-10-03"
    runtime: 6
```

The top-level `season_number`, `episode_number`, `episode_name`,
`episode_air_date`, and `episode_code` fields are convenience values for the
first matching episode.

If multiple episodes air inside the selected window, all of them are included
in the `episodes` list.

### Example TV Markdown

```jinja
{% set shows = state_attr('sensor.entertainment_releases_tv_shows_airing_today', 'items') or [] %}

{% if shows %}
  {% for show in shows %}

{% if show.poster_path %}
![{{ show.name }}](https://image.tmdb.org/t/p/w342{{ show.poster_path }})
{% endif %}

**{{ show.name }}**

{% if show.episodes %}
  {% for episode in show.episodes %}
📺 **{{ episode.episode_code }} — {{ episode.name }}**  
{% set air_date = strptime(episode.air_date, '%Y-%m-%d') %}
📅 **Air Date:** {{ air_date.strftime('%B %-d, %Y') }}  
{% if episode.runtime %}⏱️ **Runtime:** {{ episode.runtime }} min  {% endif %}

  {% endfor %}
{% endif %}

⭐ **User Score:** {{ (show.vote_average * 10) | round(0) | int }}%

{{ show.overview }}

---

  {% endfor %}
{% else %}

No TV releases found.

{% endif %}
```


# Example Home Assistant Markdown Card

The `items` attribute can be rendered in a Home Assistant Markdown card.

Example for theatrical releases:

```jinja
{% set movies = state_attr('sensor.entertainment_releases_movies_in_theaters_today', 'items') or [] %}

{% if movies %}
  {% for movie in movies %}

{% if movie.poster_path %}
![{{ movie.title }}](https://image.tmdb.org/t/p/w342{{ movie.poster_path }})
{% endif %}

{% set release_date = strptime(movie.release_date, '%Y-%m-%d') %}

**{{ movie.title }}**  
⭐ **User Score:** {{ (movie.vote_average * 10) | round(0) | int }}%  
📅 **Release Date:** {{ release_date.strftime('%B %-d, %Y') }}  

{{ movie.overview }}

---

  {% endfor %}
{% else %}

No theatrical releases found.

{% endif %}
```

This converts a TMDB score such as:

`5.9`

into:

`59%`

and converts:

`2026-10-03`

into:

`October 3, 2026`

---

# How Filtering Works

Entertainment Releases intentionally relies on TMDB's Discover API wherever possible instead of attempting to create its own movie-ranking or release-classification system.

The selected Home Assistant options are translated into TMDB Discover parameters.

Examples include:

- `region`
- `with_release_type`
- `with_genres`
- `certification`
- `with_original_language`
- `vote_average.gte`
- `vote_count.gte`
- `with_runtime.gte`
- `with_runtime.lte`
- `watch_region`
- `with_origin_country`
- `with_watch_providers`
- `with_watch_monetization_types`
- `with_type`
- `without_keywords`

Where TMDB does not provide native OR behavior for a field used as a single value, Entertainment Releases may run multiple otherwise-identical requests and merge/deduplicate the results.

Examples include:

- Multiple movie certifications
- Multiple TV origin countries

---

# Updating

When a new version is published:

1. Open **HACS**.
2. Open **Entertainment Releases**.
3. Install the available update.
4. Restart Home Assistant if prompted.

Your existing Home Assistant entity registry entries and sensor unique IDs are intended to remain stable across updates.

---

# Troubleshooting

## Integration cannot connect to TMDB

Verify that you entered the **TMDB API Read Access Token**, not only the shorter v3 API key.

## A release is missing

Check the same filters on TMDB Discover first.

Possible causes include:

- TMDB has not added the release yet.
- The title does not match the selected region.
- The release type differs from the selected type.
- The title does not meet the configured score or vote-count threshold.
- The title has a different original language.
- The runtime is outside the selected range.
- The certification does not match.
- **Exclude Theatrical Re-releases** filtered it out.

## A TV show is missing

Check:

- Watch Region
- Origin Countries
- Streaming Services
- Availability Types
- Genres
- Show Types
- Original Language
- Minimum User Score
- Minimum User Votes
- Runtime
- Exclude Keywords
- Whether TMDB lists an episode airing inside the configured date window

Remember that **Watch Region** and **Origin Countries** are different:

- Watch Region = where you want to watch the show
- Origin Countries = where the show was produced/originated

## Too many TV shows are appearing

Try narrowing the TV configuration using:

- Streaming services
- Availability types
- Show types
- Genres
- Original language
- Minimum vote count
- Excluded keywords

For example:

`Cooking, late-night show, concert`

can remove unwanted programming that still matches the other TV filters.

## Keyword exclusions do not match as expected

TMDB keyword filtering is based on TMDB's own keyword metadata.

Use wording that closely matches TMDB's keyword names for the most predictable results.

---

# Privacy and Credentials

Entertainment Releases does not include or distribute a shared TMDB credential.

Your TMDB API token is entered into your own Home Assistant installation and stored with the integration configuration.

Do not commit your personal API token to GitHub or place it directly in the public repository.

---

# Data Source & Attribution

Entertainment Releases uses data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).

**This product uses the TMDB API but is not endorsed or certified by TMDB.**

Each user must obtain and configure their own TMDB API credentials.

Streaming-provider availability data surfaced through TMDB is powered by TMDB's partnership with JustWatch.

**JustWatch attribution is required when using watch-provider data.**

---

# Project Status

Entertainment Releases is a community Home Assistant integration and is under active development.

Current functionality focuses on creating useful, configurable release feeds for Home Assistant dashboards while keeping the filtering behavior as close as practical to TMDB's own Discover system.

Issues, feature requests, and contributions can be submitted through the GitHub repository:

`https://github.com/taikowolfsbane/entertainment-release`
