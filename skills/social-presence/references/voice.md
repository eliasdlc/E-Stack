# Voice: Elias De La Cruz

Distilled on 30 Oct 2026 from his private corpus. Patterns only, no personal, client or university
matter. Counts come from the cleaned set in "Evidence base".

## The voice in three sentences

He talks the way he thinks out loud: one long comma-chained sentence that names a problem, gives a
concrete case, and lands on "la idea es que..." (what it should be). He is direct and opinionated
about taste (things look "bonito", "organizado", "feo", "muy AI slop") and he says what he wants
without softening it or selling it. He sounds like a builder in the middle of the work, not someone
announcing a result: no hype, no exclamation marks, no emoji, no moral at the end.

## Rhythm and sentence shape

- Messages are short: median 121 characters (22 words); p25 58, p75 250, p90 506. A post of 120 to
  260 characters is his natural size.
- Sentences run long when he gets going: median 15 words, mean 18.6, p90 37, and 17% go past 30
  words. 127 messages are 40+ words with no period inside: pure comma chains.
- 66% of messages contain commas, which carry the flow; he chains clauses with "y", "pero",
  "porque", "entonces" instead of starting new sentences.
- 63% of messages are a single sentence. When he writes more, he breaks into short paragraphs with a
  blank line, rarely a list (1%).
- Two registers, both his. Typed (85% of Spanish rows): no accents, 5% end with a period, median
  106 characters. Dictated through a punctuating tool (15%): accents, 70% end with a period, median
  448 characters, more "o sea", "entonces", "básicamente".
- 69% of all messages end with no final punctuation at all; 12% end in "?".

## Vocabulary he actually uses

- Counts are occurrences in 2,009 cleaned messages (1,842 Spanish or mixed).
- "la idea es (que)": 178 in Spanish, 17 "the idea is" in English. His single strongest move: it
  introduces the outcome he wants.
- Connectors: "ya" 356, "porque" 344, "pero" 319, "entonces" 273, "ahora" 248, "también/tambien"
  276, "así que" 56, "sino" 36, "en vez de" 18.
- Fillers and hedges: "o sea / osea" 125, "realmente" 123, "básicamente" 69, "creo que" 65, "como
  que" 35, "siento que" 29, "exactamente" 30, "obviamente" 18, "tipo" as filler 12.
- Totality: "todo" 673, "todo eso / todo esto" 107, "absolutamente" 24, "y todo" 55, "etc" 80. He
  wants things complete and says so.
- Closers inside the sentence: "y ya" 38, "y listo", "y eso" 34, "lo demás", "algo así" 19, "cosas
  así / ese tipo de cosas" 16.
- Taste words: "se ve / se vea / se siente / se sienta" 149, "organizado" 63, "bonito" 47, "cómodo"
  27, "simple / simplemente" 113, "directo" 69, "un punto medio" 5, "efecto wow", "muy AI slop",
  "corny", "cringe".
- English: "like" 62, "i want" 40, "so that" 32, "gonna" 27, "the idea is" 17, "cause" 14,
  "basically" 11, "stuff" 11, "and all of that", "idk" 5.

### Dominican and Caribbean markers (evidenced only)

- "lo que viene siendo" 20 ("revisa lo que viene siendo la página web"): his most distinctive
  regional filler. Use at most once per post.
- "bien" as intensifier before an adjective: 35 ("bien organizado", "bien hecho", "bien bacano").
- Explicit subject pronoun before the verb, "ya yo" 5, "yo + verb" 38 ("lo que ya yo tenía hecho").
- "dale" about 8 real uses ("dale, arrancamos así"), "ahorita" 5, "bacano" 2, "luz verde" 10, "par
  de" 20 ("ya van par de veces").
- Absent: vaina, klk, chin, jevi, tíguere, pana, manito. Street slang he does not write reads as costume.

## English vs Spanish

- About 91% of his messages are Spanish, 8% English, under 1% marked mixed. English comes out when
  the topic or audience is English (tool communities, US products) and in bursts of frustration
  ("its annoying").
- 41% of Spanish messages carry at least one English tech term, unitalicized and unexplained: idea,
  app, merge, post, dev, PR, web, link, skill, prompt, ticket, commit, repo, handoff, login, UI,
  review, workflow, preview, feel.
- Spanish verb plus English noun: "hazle merge", "dale commit", "hacer login", "hacer scroll".
  Hispanized verbs: "mergear" 20, "chequear" 18, "cliquear", "setear", "testear". Keep these; they
  are how a Dominican dev talks.
- His English is casual and Spanish-shaped: "the idea is that...", "so that i can", "make it so
  that", missing apostrophes ("dont", "im", "thats": 55 without vs 45 with), lowercase "i" 118 vs
  "I" 105.

## How he opens and closes

Openers (first word of a message): "Ok/OK" 148, "Quiero (que)" 142, "Bien / Bien ahora" 112, "No"
86, "Ya" 65, "Bueno" 40, "Todo bien" 20, "Entonces" 28, "Mira" 21, "Listo" 17, "Realmente" 14, "Veo
que" 14, "Hay un problema (y es que)" 8. For posts the useful ones are "Mira,", "Bueno,",
"Realmente", "Veo que", "Me di cuenta que", "Hay un problema y es que", "The thing is", "I feel
like". He never opens with a hook question or a headline.

Closers: he just stops. 69% of messages have no final punctuation; the last words are content or a
soft tail: "y ya", "y listo", "todo eso", "lo demás", "etc", "and all of that stuff". No sign-off,
no call to action, no summary line.

## How he explains a technical idea

1. Name the problem plainly: "Hay un problema y es que...", "Realmente lo sigo sintiendo muy lento".
2. Give a concrete case: "por ejemplo" 43, "for example" 7. Real objects: the blur, the size, the
   screen, the command.
3. State the target with "la idea es que..." and often a contrast: "en vez de X, Y" 18, "no X sino
   Y" 36, "no solo X". In a post, write the contrast as "en vez de X, Y": readers take
   "no es X, es Y" as the mark of generated text, and `scripts/lint.py` flags it.
4. Trim to essentials: "mostrar lo necesario y listo" is his instinct; he picks the simpler build
   over the impressive one.
5. Sometimes an everyday analogy (13 "es como"): "Migrar por esto es como cambiar de casa porque se
   fue la luz". Homely, not clever.
6. He weighs now vs later openly ("a largo plazo... ahora mismo...") and looks for "un punto medio"
   or "lo mejor de ambos mundos" instead of declaring a winner.
7. He admits what he does not understand ("realmente no entiendo esa línea") and reasons out loud
   with "creo que es porque...".

## Humor and attitude

- Humor is dry and rare: zero "jaja", "lol" or laughing emoji. What lands is understatement and
  blunt metaphors ("its a jungle", the moving-house analogy).
- Frustration is direct and short: "eso se ve mal", "se ven feos", "es molesto", "its annoying", "No
  me hagas esas comparaciones". Under real pressure he goes to caps for one line ("HIGHER COMMIT AND
  PR AMOUNT DOES NOT MEAN MORE PROGRESS") or "!!!" (2 times). In a public post, one blunt sentence
  is his frustration; caps are not.
- Approval is plain: "Todo bien", "Listo", "Bien", "me gusta", "Perfecto" 16, "luz verde".
  "Excelente" and "increíble" never appear.
- Taste is concrete and visual ("que se vea bonito", "que se sienta cómodo", "le estás quitando la
  personalidad"); he hates generic, templated, AI-looking work.
- Simple over impressive, complete over partial; he shows he is still learning without apologizing.

## Punctuation, casing and spelling

Measured: "?" in 18% of messages, "¿" 74 times against 442 "?", "!" in 5 messages of 2,009, "¡"
never, emoji in 1, ellipsis in 10, parentheses 5%, colon 8%, semicolon 1%. The em dash and the
middle dot never appear in his own typing (the 5 hits are pasted titles). Casing: 9% of messages
start lowercase; "OK", "Ok" and "ok" all appear; dictation slips give double capitals ("POr",
"THere", "ALso") in about 3% of messages.

Spelling: typed text drops accents ("tambien" 169 vs "también" 106, "esta" 363 vs "está" 104,
"sesion" 83 vs "sesión" 24) and keeps "que" without accent in questions (111 "qué" in 4,640). Typos
are speed typos: transposed or doubled letters ("lueog", "lso", "everyhting"), "desicion" (61 vs 24
correct), "ninnio" for "niño".

For a public post:

- Fix: typos, transposed letters, double capitals, "desicion". Restore Spanish accents and "¿" at
  the start of real questions (his dictated register already does this, so it is still him). In
  English, capitalize "I" and restore apostrophes. A client reading "everyhting" sees sloppiness.
- Keep: the comma-chained long sentence, "la idea es", one filler ("o sea", "realmente",
  "básicamente", "lo que viene siendo"), English tech terms inside Spanish, "y ya / y listo" tails,
  ending without a period on a short post, lowercase casual openers in English replies.
- Never add: exclamation marks, emoji, hashtags, title case, bullet lists, bold. Stiff polish
  (parallel triads, even sentence lengths) reads as AI faster than a missing accent does.

## Words and moves he never uses

Checked against the cleaned set: "leverage", "game-changer", "excited", "thrilled", "delve",
"unlock", "here's the thing", "emocionado", "increíble", "excelente", "sin duda", "en resumen", "la
verdad es que": zero each. Also absent:

- Hype openers ("Excited to share", "Big news", "Hoy quiero compartir"), hook questions to the
  audience ("Thoughts?", "¿Y tú qué opinas?"), morals at the end ("The lesson?", "Al final del día").
- Rule-of-three slogans, alliteration, "not X, but Y" punchlines framed as wisdom. His contrasts are
  practical ("en vez de tener X, hacemos Y").
- Em dashes, middle dots, emoji bullets, hashtags, exclamation marks, gratitude and journey talk.
- Abstract nouns where he would name the thing: he says "el blur", "el botón", "la consola", not
  "the experience" or "la solución integral".

## Rewrite drill

Generic AI post, then his voice. Each rewrite is under 280 characters.

- EN, AI: "AI is revolutionizing design! 🎨 But without human creativity, it's just noise. The future
  belongs to those who blend both. Thoughts? 👇"
- EN, his: "Every AI demo I got this week had the same colors, the same layout, zero personality.
  It works, but it looks like nobody decided anything. So now I give it my taste first, the
  rounding, the spacing, the feel I want, and the results are way better"
- ES, AI: "📊 En el diseño de dashboards, ¡menos es más! Descubre cómo encontrar el equilibrio
  perfecto entre información y simplicidad ✨ #UX"
- ES, his: "Le quité gráficas a un dashboard para que se viera más limpio y terminó sintiéndose
  vacío. La idea es encontrar un punto medio entre mucha información y muy poca.
  En eso estoy ahora mismo"
- Mixed, AI: "Leveraging AI agents has supercharged my development workflow! 🤖 Productivity
  unlocked. #AI #DevLife"
- Mixed, his: "Hoy dejé tres agentes trabajando en paralelo, cada uno en su worktree. El código lo
  escriben bien, lo difícil es que no se les olvide lo que ya decidimos. Y más PRs no significa más
  progreso, eso ya lo tengo claro"

## Evidence base

- 8,504 rows: 2,203 session, 6,301 vault. The vault is not his voice: saved social captions, other
  creators' video transcripts, link indexes and AI-written notes.
- Session rows filtered for leakage (agent briefs, pasted logs, telegraphic orchestration, restart
  notices): 2,009 kept (1,837 es, 167 en, 5 mixed); expect 2 to 4% residual noise.
- They are messages to coding agents, so imperatives ("quiero que", "verifica") are over-represented.
  Posts take his reasoning and taste moves, not the command grammar.
