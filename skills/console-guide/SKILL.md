---
name: console-guide
description: Writes the step by step guide Elias follows by hand in a web console or dashboard (Cloudflare, Neon, Vercel, GitHub settings, Firebase, Supabase, app stores, DNS, billing) when no CLI or API can do the job. Use for "guide me", "step by step", "what do I put in", "where is it", "how do I do it in the console", the Spanish equivalent, or when a task needs a value only he can produce in a browser. Not when a CLI or API can do it.
---

# Guiding Elias through a web console

The guide is a script he runs on a screen you cannot see. Write every line so
it works without him asking a question back: the exact place, the exact label,
the exact value.

## Before writing a single step

1. **Try to not need the console.** `gh secret set`, `gh api`, `npx vercel`,
   `firebase`, `gcloud`, `supabase`, `curl` against a public API. If a CLI or
   API does the whole thing, do it yourself and ask him only for the login or
   the approval the CLI cannot give. Reading a value out of a console counts
   as "needs his hands" only when no CLI you are already authenticated with
   returns it.
2. **Check the current UI before describing it.** Fetch the provider's docs
   page for that exact screen (WebFetch) and read the labels from there.
   Consoles move buttons every few months; a guide written from memory is the
   one that fails. When the docs and your memory disagree, the docs win, and
   when you still are not sure, say "the button is called X or Y" naming both.
3. **Split by what he produces.** One guide per value he has to bring back.
   "Create the token" and "paste the token" go in separate blocks.

## How each step is written

- **One step, one screen.** A step is: where he is, what he clicks or types,
  and what appears next. If a click opens a new page or a modal, that is the
  end of the step and the next one starts with what that page shows.
- **Deep link first.** Every step that starts a page gives the full URL that
  lands on that screen, not the site root. Cloudflare has `?to=` links,
  Vercel and GitHub have stable settings paths, Neon has per project paths.
  If a deep link needs an id you do not have, give the URL up to the id and
  say what the id looks like.
- **What he sees after login.** The first step of a guide always says what
  the landing page shows and where the thing he needs is on it: "top right",
  "left sidebar, Storage section", "the green button".
- **Labels in their exact text and language.** `Create API token`, not "the
  create button". If the console is in Spanish for him, say the Spanish label
  and the English one in parentheses.
- **Every input, its value.** A form is listed field by field, in the order
  the form shows them, with the exact value to type or the exact option to
  pick. Fields he must leave alone are named with "leave it as it is". A field
  you are not sure exists gets "if it appears" in front.
- **Every value he must bring back gets a name and a destination.** "Copy
  `Access Key ID` and paste it into `~/.config/secrets/kino.env` as
  `R2_ACCESS_KEY_ID=`". A secret goes straight into its file, not through the
  chat; `request_secret` cannot fill a file, because it hands the agent only a
  reference that a T3 tool consumes. Say when a value is shown only once so he copies it before closing.
- **The success check is his, and concrete.** End every guide with what the
  screen shows when it worked, and what you will run on your side to confirm
  it, so he knows he is done.
- **Name every trap next to the field where it happens.** The pooled string
  that looks like the direct one, the token that expires, the scope that
  silently grants too much.

## Format

Numbered steps, one action each, 15 words or less when possible. Field lists
as `Field → value` lines under the step. Values to type in backticks. Steps
follow each other directly, with no prose between them. At most one guide per message unless he asked for all
of them at once; then separate them with a heading per value he brings back.

## After he says "done"

Verify from your side before moving on: the secret exists (`gh secret list`),
the bucket answers (`curl --aws-sigv4`), the connection string is direct
(`psql` or the `-pooler` check), the deploy ran (`gh run list`). Report the
command and its output. His "done" is the trigger for your check, not the
end of the step.

The incident behind these rules is in `references/history.md`; read it only
when changing a rule.
