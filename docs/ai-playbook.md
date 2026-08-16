# AI Coding Playbook

## 1. When I reach for AI first

- Create a summary / documentation of the project
- Explore the language stack to be used before starting my project
- For my workflow, like create a draft first and then implementation

## 2. When I do not reach for AI

- Anything that involves storing secrets in .env files so that they do not get leaked and get abused (if AI API model was leaked, then the attacker may abuse the key and let the user spend a lot of money)
- Design decisions I need to own because AI does not have "feelings" to know the requirements that I really want (or the design)

## 3. My non-negotiables

- I will not run AI on "bypass permission" mode so that it does not run dangerous commands (like rm -rf on Linux, or delete system32 files on Windows)
- I will not auto-accept AI answers without reading them and understanding the code
- When in doubt, I will ask for more clarifications

## 4. My review rules

- Run the test files and manually test the feature (basics)
- Check edge cases and error handling
- Check the API (backend)'s return codes if they correctly match the actual problem

## 5. What I am still figuring out

- How to know how much context is too much or too little
- How to keep AI-written code consistent while being similar to my old coding style before AI

## Decision Card

AI-Assisted Coding - Module 5 Prompt Library
- For a new feature I reach for: brainstorm the approach, design it and let AI implement it
- Re-read: module 4 implementation and mark what changed (30 days from today, to 2026-09-15)
- For a code review I reach for: ask for security concerns and create test files
- For debugging I reach for: paste the error and let AI explain it
- For infrastructure I reach for: CI configurations, docker files and verifications
- I will never paste secrets / api keys into an AI tool
- My one rule is: read and verify everything before committing
