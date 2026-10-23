# Atlas of the Cosmos

A responsive, independent, personal NASA news + engineering + science learning website. This edition uses an AI-generated conceptual lunar landscape for a full-viewport, image-led homepage on desktop, tablet and mobile. News and learning content appears after scrolling. Built without a framework or paid services.

## What's included

- **Today:** editorial home, NASA headlines, news categories and search, a real NASA Artemis II Earthset photo and a moonscape website background image integrated into the theme.
- **Missions:** 8 guided mission pages, including a curated Artemis roadmap as of 23 October 2026.
- **Discover:** 6 beginner-friendly science rabbit holes.
- **Engineering Lab:** interactive rocket-equation, ellipse eccentricity explainer, clickable vehicle subsystems, 5 build prompts.
- **Learning Library:** 14 curated free original NASA / JPL resources, filtered by interest.
- **Saved & Notes:** browser-local bookmarks, notes, .txt export.
- **Scheduled refresh:** official NASA RSS fetched by `scripts/update_news.py` and committed to `data/news.js` / `data/news.json` by `.github/workflows/daily-update.yml` at about **07:00 IST daily**, subject to GitHub scheduler delays.

## Open it right now

Extract this ZIP and double-click `index.html`. The site works locally using the **23 October 2026 starter snapshot**. An internet connection is helpful for NASA links, remote imagery and fonts. The AI-generated lunar background image itself is bundled inside this package, so the core visual theme works locally. The snapshot does not auto-update on your laptop by itself.

## Publish + enable daily automatic updates (GitHub Pages)

1. Create a **new public repository** on GitHub (for example `atlas-of-the-cosmos`).
2. Upload **all extracted files and directories**, including `.github/workflows/daily-update.yml` (hidden folder), to the root of the repository. Commit to the default `main` branch.
3. In **Settings → Pages → Build and deployment**, select **GitHub Actions** as the publishing source (not “Deploy from a branch”). The included workflow both updates the feeds and deploys the current website. Your public URL will look like `https://YOUR-USERNAME.github.io/atlas-of-the-cosmos/`.
4. Under **Settings → Actions → General → Workflow permissions**, permit read and write if necessary; the workflow needs `contents: write` to commit updated data.
5. Open **Actions → Refresh NASA news and publish website → Run workflow** once to test. Inspect the log and check the date label on your published site after the Pages refresh completes.
6. The workflow also runs when you push to `main`. It normally runs every day at **01:30 UTC / 07:00 IST**; GitHub can delay scheduled runs and can disable them in inactive public repositories. If a feed is unavailable, the script preserves previous data rather than falsely presenting it as a fresh update.

**Important:** A packaged file is not a deployed website. The daily job only becomes active after you host it in a GitHub repository and enable GitHub Actions. It is not a ChatGPT automation, and ChatGPT will not independently edit it daily.

## Project structure

```
index.html
styles.css
app.js
data/news.js           # loaded directly by HTML, works with file://
data/news.json         # same data as JSON
scripts/update_news.py
.github/workflows/daily-update.yml
README.md
```

## Sources & reliability

- Official mission and news feeds: [NASA RSS](https://www.nasa.gov/rss-feeds/)
- Artemis source: [Artemis news](https://www.nasa.gov/artemis-news/)
- Mission context: [Artemis II updates](https://www.nasa.gov/artemis-ii-news-and-updates/)
- Free resources: [NASA Science learning](https://science.nasa.gov/learn/learning-resources/), [NESC Academy](https://nescacademy.nasa.gov/), [NASA 3D Resources](https://science.nasa.gov/3d-resources/), [NASA's Eyes](https://eyes.nasa.gov/)
- Image credit: NASA, [Artemis II Earthset](https://images.nasa.gov/details/art002e009288)

The curated **mission guide content is editorial and does not auto-rewrite** when NASA changes plans. The headline stream **does** update after deployment. Check source pages for current mission dates, especially Artemis. Never infer launch date certainty from old articles.

## Customization

- Edit `missions`, `topics`, `resources`, and `challenges` arrays at the beginning of `app.js`.
- Change theme colors in `:root` in `styles.css`.
- Add RSS URLs in `FEEDS` in `scripts/update_news.py`.
- Bookmarks/notes are intentionally stored only in the browser; clearing browser storage deletes them. Export your notes if you need a copy.

## Southern Ring background

- Official object: **Southern Ring Nebula (NGC 3132)**, observed by the James Webb Space Telescope (NIRCam).
- Photo CDN: https://cdn.esawebb.org/archives/images/wallpaper4/weic2207b.jpg
- NASA source/credit information: https://science.nasa.gov/asset/webb/southern-ring-nebula-nircam-image/
- Credit: NASA, ESA, CSA, STScI.
- This is an infrared composite assigned visible colours, not a visible-light photograph or AI-generated artwork.
- This independent site is not endorsed by NASA, ESA or the Webb team.

## Visual refinement

Unified all mission, learning, and engineering panels using neutral dark translucent glass. No saturated blue cards; homepage lunar hero and content are unchanged.

## Learning pathways & deployment fix

- Added three guided starting points on the homepage (Artemis, Webb and Engineering Lab).
- Fixed GitHub Pages publishing to include the bundled lunar background (`assets/moon-background.png`).
- Other approved visual styling is unchanged.
- The homepage background is AI-generated artwork, **not** an authentic NASA photograph. NASA photograph credits within editorial content are separate.
- Daily RSS refresh and deployment still require publishing on GitHub and enabling the included workflow.
