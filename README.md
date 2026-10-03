# Entertainment Releases for Home Assistant

A HACS-installable Home Assistant custom integration for a daily movie and TV release feed.

## Current features

- Movies released theatrically today
- Movies released digitally today
- TV shows airing today
- Configured entirely through Home Assistant's UI
- One shared Entertainment Releases device
- Automatic refresh every 6 hours
- Structured title metadata in sensor attributes

> Streaming provider availability and the exact date a title was added to a provider are not the same thing. This project will not call something "new on Netflix today" until that date can be established reliably.

## HACS installation

1. Create a GitHub repository and upload the contents of this project.
2. In Home Assistant open HACS.
3. Open **Integrations**.
4. Open the menu and choose **Custom repositories**.
5. Paste your GitHub repository URL.
6. Select **Integration**.
7. Add the repository.
8. Find **Entertainment Releases** in HACS and choose **Download**.
9. Restart Home Assistant.
10. Open **Settings → Devices & services → Add integration**.
11. Search for **Entertainment Releases**.
12. Enter your TMDB API Read Access Token.

HACS will install the integration into:

`/config/custom_components/entertainment_releases/`

You do not need to create that directory yourself.

## TMDB

Create a TMDB account and obtain an API Read Access Token (Bearer token):

https://developer.themoviedb.org/docs/authentication-application

## Sensors

- Movies in Theaters Today
- Movies Released Digitally Today
- TV Shows Airing Today

The sensor state is the number of matching titles. The `items` attribute contains the title data.

## Roadmap

- Episode-level TV releases
- Watch-provider availability
- Configurable streaming providers
- Streaming release-date correlation
- Posters and richer metadata
- Daily digest
- Coming tomorrow / this week
- Dedicated Lovelace card
- Home Assistant notifications
- Tonight's Picks

## Data Source & Attribution

Entertainment Releases uses data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).

This product uses the TMDB API but is not endorsed or certified by TMDB.

Each user of this integration must obtain and configure their own TMDB API credentials. No shared TMDB API key or access token is included with this project.

This project is intended for personal, non-commercial use. Users are responsible for ensuring that their use of TMDB data complies with TMDB's API terms and policies.

If streaming-provider availability is displayed, that availability data may be provided through TMDB's partnership with JustWatch and should be attributed to JustWatch where applicable.
