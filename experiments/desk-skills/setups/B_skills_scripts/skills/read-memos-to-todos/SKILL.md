---
name: read-memos-to-todos
description: Turn Alex's voice memo transcripts (out/transcripts/memo*.txt) into the to-do list out/todo.md.
version: 1.0.0
metadata:
  hermes:
    tags: [todo, memos]
---
# Read memos to todos

## When to Use
When asked to make Alex's to-do list.

## Procedure
1. Read each file: out/transcripts/memo1.txt, out/transcripts/memo2.txt, out/transcripts/memo3.txt (read_file). These memos are the ONLY source of to-dos — not the emails.
2. For every sentence where Alex says he must/needs to/should do something (send, renew, book, call, order, reply, pick up, pay…), write one item. Skip opinions and musings.
3. Keep any day or date Alex said as "(due: …)".
4. write_file out/todo.md:
```
# To-do
- [ ] <task in Alex's words> (due: <day>)
- [ ] <task>
```

## Verification
Re-read each memo and check every action sentence has exactly one item.
