# Publishing checklist

## Set up GitHub

Suggested repository name: **chess-bruh-philidor-anki**

Suggested description:
> Chess Bruh — every move, your turn. An image-based Anki deck for the Philidor speedrun: 11,046 cards, 292 games, Stockfish analysis.

Suggested topics:
`chess` `anki` `philidor` `spaced-repetition` `stockfish` `python`

## First upload

- Upload this folder's contents to the repository root.
- Review the scope disclosures and source-data terms before publishing.
- Choose a license for original code; no license has been assumed for you.
- Confirm `README.md` displays correctly.
- Keep `.apkg` files out of Git history. Use Releases for downloadable builds.

## Publish the deck

1. Create a release, for example `v1.0.0`.
2. Attach `Philidor-Speedrun.apkg` from the delivered deck, or build it locally.
3. Optionally attach `philidor-games.pgn`.
4. Mention the card count, game count, analysis settings and archive-based coverage limitation in the release notes.
5. After publishing, replace the README's generic Releases instruction with the actual release URL if desired.
6. Test downloading and importing the package in Anki.

## Before every release

- Verify card and media counts.
- Check board orientation and a few move answers for both colors.
- Confirm source links and explanatory limitations remain accurate.
- Update counts when the selected game set changes.
