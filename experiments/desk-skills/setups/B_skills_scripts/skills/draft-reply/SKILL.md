---
name: draft-reply
description: Draft (never send) a reply email to someone in Alex's inbox, offering times when Alex is free.
version: 1.0.0
metadata:
  hermes:
    tags: [email, draft]
    requires_toolsets: [terminal]
---
# Draft reply

## When to Use
When asked to draft a reply to an email in inbox/.

## Procedure
1. read_file the email (e.g. inbox/05.eml). Note the sender in the From: line — the reply goes TO that person, never to Alex.
2. Get Alex's free times: `python3 $HERMES_HOME/skills/find-free-slot/scripts/cal_week.py calendar.ics` (terminal).
3. Pick two 1-hour times on different days, fully inside FREE ranges, between 09:00 and 17:00.
4. write_file drafts/reply_NN.eml:
```
To: <sender name and address from From:>
Subject: Re: <original subject>

Hi <first name>,

<one line answering their request>:
- <Day HH:MM-HH:MM>
- <Day HH:MM-HH:MM>

Best,
Alex
```

## Pitfalls
- Never send. Only write the draft file.
- To: is the email's sender.

## Verification
Re-read the draft: To is the sender; each time is inside a FREE range printed by cal_week.py.
