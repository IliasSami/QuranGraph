# Source data issues

Problems found in the source texts while building and during the explanation pilot. Each one is handled in the
pipeline (never by silently editing a licensed text) and, where the source asks for it, reported to the publisher.

## Fixed or handled in the pipeline

| Source | Issue | Handling |
|---|---|---|
| Tanzil Uthmani / Simple | The Basmalah is written at the start of ayah 1 of every surah except 1 and 9 | Split into a separate `basmala` table for the surah header; both parts stay character-for-character Tanzil (`core/build_text.py`) |
| spa5k mirror `en-al-jalalayn` | 1:2 holds a passage from another, esoteric tafsir | Switched to the clean `tafsir-al-jalalayn` edition |
| spa5k mirror `en-asbab-al-nuzul-by-al-wahidi` | Not al-Wahidi: a mystical commentary (likely Kashf al-Asrar) | Removed; occasions of revelation come only from reports quoted in Ibn Kathir, Ma'ariful Qur'an and Zakaria's notes |
| spa5k mirrors (Ibn Kathir, Sa'di, Ma'ariful) | One passage's text is repeated under every ayah it covers | `qg ctx` prints each passage once (`grounding_text`) |
| QuranEnc Al-Mukhtasar (EN 27, BN 22, AR 24 ayat) | The text filed under an ayah is another ayah's explanation (its leading number differs) | Marked `misaligned` in `text.note`; hidden for that ayah and not citable (validator). 52 EN rows are repeated refrains with identical wording (`same-wording`) and are kept |

## To report to QuranEnc (their terms ask users to notify them)

- **bengali_mokhtasar: legacy-font characters** in about 815 ayat (e.g. 1:2 "¯্রষ্টা", 1:4 "মহত্ত¡", 1:7 "ত্রæটি",
  79:… "দÐায়মান", "আহŸান", 89:… "জিহŸা", "স্ত‚পীকৃত"). Included in the draft email (docs/permissions/EMAILS.md §1).
- **Al-Mukhtasar misaligned rows** (EN/BN/AR): full list from `SELECT source, surah, ayah, note FROM text WHERE note LIKE 'misaligned%'`.
- **Al-Mukhtasar 90:11** (EN and BN): says "he will cross the pass", where the other sources read the ayah as
  negative ("he has not attempted the steep path"). For the scholar reviewer to check before reporting.
- **Al-Mukhtasar 89:10**: EN explains "the pegs" as stakes used for punishment, BN as many soldiers (both views are
  in the classical tafsirs; the two language editions differ).

## For the reviewer (grounding mirrors, not shown on the site)

- Ma'ariful Qur'an gives no separate text for 79:6–24 (it repeats a truncated 79:5 passage).
- Al-Muyassar 79:16 appears to hold the text of 79:17–19; 90:1 and 90:2 entries read the same phrase differently.
- Ibn Kathir passages are cut at the bundle limit for long passages (e.g. 89:6–14, 90:13–20, the start of al-Baqarah);
  the full run should raise the limit or split long passages.
- Ma'ariful Qur'an 82:1 shows the commentary on 81:19–23; nothing for 81:24–29.
- Zakaria footnotes are cut at 1,500 characters in `qg ctx` (a bundle limit, not a source fault); raise it for the full run.
- Ma'ariful Qur'an 92:1 shows the commentary on 91:14–15.
- Zakaria footnote to 91:10 has a misspelled Arabic quote ("قَدْاَفْدَحَ" for أفلح). Report to QuranEnc.
- English Mukhtasar 92:5 reads "repatriation" where the Bangla edition has expiation (likely a translation slip). Report to QuranEnc.

## Priority review items from the pilot

- **94:2** "the burden": explained, as the sources do, in terms of sins/burden; touches the infallibility of the
  Prophet ﷺ. A qualified reviewer must approve the wording.
- **93:7** "found you unaware (dall)": wording must not suggest the Prophet ﷺ was astray.
- **89:22, 2:15, 2:7** (Allah's coming, "Allah mocks them", sealing of hearts): aqeedah wording.
- **90:2, 90:13, 109** (fighting in Makkah, freeing slaves, al-Kafirun): often-misquoted context.
- **Systematic (handled):** the tafsir mirrors repeat the previous surah's last passage under ayah 1 of the next
  surah (Ma'ariful Qur'an in 23 surahs, e.g. 82:1, 88:1, 92:1). `core/build_text.py` (`drop_carried_over`) removes those rows.
- Zakaria footnote at 87:4 writes حافظ where غثاء is meant. Report to QuranEnc.
- 88:22 ("you are not a controller over them"): some sources say it was abrogated by the command to fight — reviewer to check wording.
- Bangla Mukhtasar 84:15 says Allah returns him "to worldly life" (দুনিয়ার জীবনে); the English edition does not. Reviewer, then QuranEnc.
- English Mukhtasar 84:24–25 are labelled "34."/"35." (likely typos; currently hidden as misaligned — review whether to show).
- Long narrations (People of the Ditch, 85:4–10) are cut at the bundle limit in all grounding sources; raise the limit for story passages.
