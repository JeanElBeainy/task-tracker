# Reflection

This reflection covers what was learned until now in the 3 modules and the two features I added to the Task Tracker: due dates with an overdue filter, and the activity log.

## Which AI tools I used, and for what

I started this project in Cursor, then partway through switched to DeepSeek running inside Claude Code in VSCode for the rest of the implementation work on both features. I modified the settings.json inside the .claude folder on my machine to DeepSeek's API and used it through Claude Code.

## One moment AI helped

DeepSeek and other AI models were noticeably good at surfacing details I had not thought to check myself, including edge cases I would likely have missed if I had written the logic alone. It caught scenarios I was not specifically prompting for, which is exactly the kind of help this workflow is supposed to provide.

## One moment AI slowed me down

The same tool also cost me time in a different situation. When I asked it to fix issues that were genuinely simple, it sometimes responded by creating new files and adding several new functions instead of making the small, direct edit the fix actually needed. Untangling that extra structure afterward took longer than the original bug would have taken to fix by hand.

## One place my review changed the result

The clearest lesson from this project was about when review matters most. I learned that reviewing prompts and their output carefully at the very beginning of a task matters far more than reviewing later, because once several steps had been built on top of an early decision, it became close to impossible to revert everything back to where things started. Catching a problem early meant a small correction. Catching the same kind of problem several prompts later meant unwinding a whole chain of changes.

## Overall

Comparing Cursor and DeepSeek showed me that different tools fail in different ways. One tended to miss less on its own, the other tended to overbuild simple fixes into something larger than needed. The habit that mattered most with both was the same: read the very first outputs closely, since that is the point where correcting course is still cheap. That is the habit I plan to keep using in later modules.