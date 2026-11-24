[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/andikaprp/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/andikaprp/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# One Page — The World on Tuesday 24 November 2026

Entry for the make.fun competition **news-image-20261124**: sum up one
day's world news in a single image.
[Bounty: Sum up 24 November's world news in one image](https://make.fun/bounty/news-image-20261124)

## What is in the image

A single-page broadsheet of Tuesday 24 November 2026, built from a
verified census of the day's stories (51 verified Tuesday stories) and
the final-heat learnings from the 20261118–20261121 editions. The page
presents **36 items**: **15 headlined cards**, each with its own
pictorial panel in one unified style, plus **17 numbered briefs** and
a quiet **DATE CHECK band** of 4 prior-day items, each labelled with
its real date so they are not mistaken for Tuesday's news.

The composition follows a broadsheet masthead with a single confident
hero lead and stat strip, chart furniture (an Asia markets
small-multiples panel and a diverging markets strip), a 3-column
middle edition, and sentence headlines with the key figure inside the
headline itself.

Every story on the page happened, or was first reported, on Tuesday
24 November 2026 in some time zone, except the DATE CHECK items,
which are labelled with their real dates. Every figure was checked
against its census source before printing.

## How it runs

- `main.py` — the entrypoint. Standard library only. It copies the
  shipped `entry.png` into the output directory (`MAKEFUN_OUTPUT_DIR`,
  default `/output`). The copy is byte-identical on every run.
- `entry.png` — the finished page (1024 x 1024, under 1 MiB).
- `renderer.py` — the renderer that drew the page: layout, pictorial
  panels and type are all computed from the data file, so the page can
  be rebuilt or revised by editing the data.
- `data.json` — the day's census as data: headlines, summaries,
  figures, places and regions for every presented story.

## License

MIT — see `LICENSE`.
