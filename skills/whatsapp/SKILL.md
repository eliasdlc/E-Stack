---
name: whatsapp
description: Reads Elias's own WhatsApp from his read-only archive on agentbox through the `whatsapp` MCP (list_chats, get_messages, search_messages), for questions about what someone wrote him, what was agreed in a chat, a date, price or link sent there, or a summary of a conversation, even when he does not say "WhatsApp". Use for "qué me dijo X", "busca en mis chats", "lo que hablamos de", "en el grupo de", "mi WhatsApp", "revisa los mensajes de", "cuándo quedamos con", "what did X text me". Also owns the archive itself (GUI, linking, exports, the nightly digest to Kino). Not for writing a message for him to send (the channel rule in his rules covers that), not for an audio or video file he attaches (media), and never for sending anything.
---

# WhatsApp

Elias's WhatsApp is archived on agentbox by `whatsapp-archivo`
(github.com/eliasdlc/whatsapp-archivo), linked as a companion device since
8 Nov 2026 with 30 days of history before that. Read it through the `whatsapp`
MCP, because that server opens the database read only and has no way to reach
WhatsApp.

| Need | Tool |
|---|---|
| Find the chat | `list_chats` with part of the name or number; the jid it returns is the key |
| Read a conversation, or a date range | `get_messages` with the chat jid, `from` and `to` as YYYY-MM-DD (end inclusive, America/Santo_Domingo) |
| Find who said something, or where | `search_messages` with the words, optionally one chat and dates |

Voice notes arrive as text: the archive transcribes them with local Whisper,
so a quote from one can be off by a word; say it came from an audio.

## Privacy

The messages are other people's private words, so quote the line that answers
the question and summarize the rest. They never enter a file, a commit, a PR, a
capture, a ticket or a Postplan page unless Elias asks for that exact text to
go there; captures of the GUI use the fake demo data of the repo's tests.

## When it does not answer

| Symptom | What it means | What to do |
|---|---|---|
| The `whatsapp` tools are missing | The MCP is not installed on this machine | `agents mcp status`, then `agents mcp sync` |
| The tools time out from the laptop | agentbox is off or off the tailnet | Say so; the archive lives only there |
| A chat ends days ago | The device was unlinked or disconnected | The GUI at https://agentbox.<tailnet>.ts.net:8790 shows the state; relinking is his, from the GUI |
| Nothing older than 30 days before linking | That is where the archive starts | In the GUI, "Pedir 50 anteriores al teléfono" asks the phone for more, one chat at a time |

## The archive

The GUI (tailnet only) reads, searches and downloads a chat whole or by dates
(txt, zip with media, json, csv). Every night at 22:00 the digest sends verified
tasks to Kino and a Telegram summary with the chats waiting for his answer.
How it runs, its units and its traps live in that repo's AGENTS.md.
