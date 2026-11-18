# Working rules for "{{TITLE}}"

Rules an AI agent (and any human collaborator) follows when working on this manuscript. For Claude Code, save this file as `CLAUDE.md`; for other tools, `AGENTS.md` or similar.

1. **Review every change critically before applying it.**
   - Do not take dictation, whether the suggestion comes from the author, an AI, or anyone else.
   - For each change ask: does it fit the persona, does it serve the theme, does it fit the chapter's situation, are the facts consistent, is it a good sentence?
   - Report anything you did not apply, or applied differently, with the reason.

2. **Read the invariants in `graph.json` before editing. After editing, update the graph and run the check.**
   - `storygraph check graph.json manuscript.docx`
   - When a scene changes, update its Event `evidence` (the sentence from the manuscript) and its edges.
   - When a scene is cut, run `storygraph impact` and re-read every setup or echo that lost its partner: does it still stand?

3. **Never edit the original.**
   - Save working versions under new numbered names. When a version is final, keep only the new final version and the original.
   - Keep abridged editions (e.g. for contests) as separate files, and list deliberately cut nodes in an exclusion file.

4. **Read `FEEDBACK_LOG.md` before working, and update it at the end of every round.**
   - Principles go in Part 1, the work record in Part 2, the AI's mistakes in Part 3.
   - Mark what the author said as [author] and the AI's reading as [interpretation].

5. **The author decides.** Ask before applying anything that changes the design (what a character means, the ending, how a symbol reads). Never insert a sentence just to prove a design.
