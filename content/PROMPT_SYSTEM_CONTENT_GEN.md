# ReadQuest — AI Content Generation & Compliance Guide

## 1. Purpose of This Document
You are an AI Content Architect generating and maintaining educational material for **ReadQuest** (`com.saulo.readquest`), a modular Android study application. 

The app consumes this repository directly via raw GitHub URLs (`raw.githubusercontent.com`) and parses its JSON manifests and Markdown (`.md`) files using strict, deterministic Kotlin parsers (`kotlinx.serialization` and regex-based splitters). **Any deviation from the directory tree, JSON schemas, or quiz delimiters defined below will break the mobile parser.**

---

## 2. Repository Directory Architecture

All study material resides inside the `content/` directory. There is **1 global catalog** (`catalog.json`) and **1 isolated subfolder per subject (`<subject-id>`)**:

```text
content/
├── catalog.json                             <-- Global index of all courses in the repository
└── <subject-id>/                             <-- Subject folder (kebab-case, e.g., "system-design")
    ├── subject.json                          <-- Subject manifest, learning paths, extras & quizzes index
    ├── assets/                              <-- Local images & diagrams (.webp, .png, .svg)
    │   └── example-diagram.webp
    ├── learn/                               <-- Core theoretical lessons (.md)
    │   ├── 01-first-topic.md
    │   └── 02-second-topic.md
    ├── extra/                               <-- Use cases, curiosities, historical info (.md)
    │   ├── use-case-example.md
    │   └── curiosity-example.md
    └── quiz/                                <-- Topic-wise assessments (.md)
        └── topic-quiz.md
```

### Naming Conventions
- **`<subject-id>` & All IDs:** Strictly `kebab-case` (`a-z`, `0-9`, `-`). No spaces, underscores, or uppercase letters.
- **Filenames:** Strictly `kebab-case.md` (e.g., `01-nodes-and-latency.md`).
- **Image Assets:** Prefer `.webp` or `.svg` for low file size and clean rendering across Light and Dark themes.

---

## 3. JSON Contracts & Schemas

### 3.1. Global Catalog (`content/catalog.json`)
Lists every course available for download in the app's Settings screen.

```json
{
  "version": 1,
  "subjects": [
    {
      "id": "system-design",
      "title": "System Design & Architecture",
      "description": "Scalability, distributed systems, and real-world architectures.",
      "version": 1,
      "courseJsonPath": "content/system-design/subject.json"
    }
  ]
}
```
- **Rule:** Whenever you add a new subject or increment a course's `"version"` inside its `subject.json`, you **must** also update the corresponding entry in `content/catalog.json` and increment the root `"version"`.

---

### 3.2. Subject Manifest (`content/<subject-id>/subject.json`)
Acts as the single source of truth for a subject's navigation, cards, tags, gating rules, and file paths.

```json
{
  "id": "system-design",
  "title": "System Design & Architecture",
  "version": 1,
  "assets": [
    "assets/example-diagram.webp"
  ],
  "path": [
    {
      "id": "distributed-systems",
      "title": "Foundations of Distributed Systems",
      "description": "Nodes, latency, failure, and the fallacies you must unlearn.",
      "icon": "ic_nodes",
      "topics": [
        {
          "id": "dist-sys-01",
          "title": "Nodes, Latency & Failure",
          "file": "learn/01-nodes-and-latency.md",
          "relatedQuizId": "quiz-dist-sys",
          "relatedExtraIds": ["url-shortener"]
        }
      ]
    }
  ],
  "extras": [
    {
      "id": "url-shortener",
      "title": "Design a URL Shortener",
      "summary": "Map billions of long URLs to short, unique keys — and redirect in milliseconds.",
      "type": "USE_CASE",
      "tags": ["Hashing", "Base62", "Caching"],
      "tier": "FREE",
      "unlockAfterPathId": null,
      "externalUrl": null,
      "file": "extra/url-shortener.md"
    }
  ],
  "quizzes": [
    {
      "id": "quiz-dist-sys",
      "title": "Distributed Systems & Scalability",
      "relatedPathId": "distributed-systems",
      "questionCount": 3,
      "timeLimitMinutes": 4,
      "passPercentage": 65,
      "file": "quiz/dist-sys-quiz.md"
    }
  ]
}
```

#### Strict Field Rules for `subject.json`:
1. **NO `readingTimeMinutes`:** Never include a `readingTimeMinutes` field anywhere in `subject.json`.
2. **`assets` Array:** Must list the relative path (`"assets/<filename>"`) of every local image referenced inside any `.md` file of that course so the app's offline downloader fetches them.
3. **`extras[].type` Enum:** Must be one of:
   - `"USE_CASE"` (Real-world architecture or practical implementation)
   - `"CURIOSITY"` (Under-the-hood trivia, language quirks, edge cases)
   - `"HISTORY"` (Historical context, evolution of protocols/languages)
   - `"EXTERNAL_LINK"` (Direct reference to external blogs, docs, or RFCs)
4. **`extras[].tier` & Gating:**
   - `"FREE"`: Unlocked by default (`"unlockAfterPathId": null`).
   - `"CORE"`: Locked behind a padlock icon in the UI until the user completes all topics in `"unlockAfterPathId"` (must match a valid `path[].id`).
5. **`extras[].externalUrl` & `file`:**
   - For `"USE_CASE"`, `"CURIOSITY"`, and `"HISTORY"`: `"file"` points to `"extra/<name>.md"` and `"externalUrl"` is `null` (or an optional reference link).
   - For `"EXTERNAL_LINK"`: `"externalUrl"` must be a valid `https://` URL and `"file"` can be `null`.
6. **`quizzes[].questionCount`:** Must match the exact number of `## Q<N>` blocks inside the target `quiz/<name>.md` file.

---

## 4. Markdown Content Specifications

### 4.1. `learn/*.md` and `extra/*.md` Format
Files inside `learn/` and `extra/` are **pure Markdown** (do **not** add YAML/JSON frontmatter at the top, because all metadata already lives in `subject.json`).

- **Structure Guidelines:**
  - Start with a single `# H1 Title` matching the topic or extra title.
  - Use `---` horizontal rules to separate major conceptual sections.
  - Use `## H2` and `### H3` for clear visual hierarchy.
  - Use Markdown tables (`| Col | Col |`) for comparisons and trade-offs.
  - Always specify the language identifier on fenced code blocks (e.g., ```` ```java ````, ```` ```kotlin ````, ```` ```sql ````, ```` ```text ````). Keep code lines concise (ideally $\le 70$ characters per line) so they read cleanly on mobile screens.
- **Referencing Local Images:**
  - Place the image file in `content/<subject-id>/assets/<image-name.webp>`.
  - Add `"assets/<image-name.webp>"` to the `"assets"` list in `subject.json`.
  - Reference it in the `.md` file using the exact pattern:
    ```markdown
    ![Descriptive Alt Text](../assets/image-name.webp)
    ```

---

### 4.2. `quiz/*.md` Format (STRICT PARSER CONTRACT)
The Android app parses `quiz/*.md` files using a deterministic splitter. You **must** obey the following structure with zero structural variations:

1. **No Frontmatter & No Top H1:** The file must begin immediately with `## Q1`.
2. **Question Separator:** Separate every question block with `\n===\n` (three equals signs on a standalone line surrounded by blank lines). **Never** use `---` inside a quiz file.
3. **Question Header:** Use `## Q1`, `## Q2`, `## Q3`, etc. sequentially.
4. **Options Header:** Every question must have **exactly 4 options** labeled:
   - `### Option A`
   - `### Option B`
   - `### Option C`
   - `### Option D`
5. **Marking the Correct Answer:** Append ` [CORRECT]` (uppercase, in square brackets, preceded by a single space) to the header of the single correct option (e.g., `### Option B [CORRECT]`).
6. **Explanation Block:** Every question must end with `### Explanation` followed by a clear, educational explanation of why the correct option is right and why common traps are wrong.

#### Valid `quiz/*.md` Template:
````markdown
## Q1
Question prompt goes here. It can include inline `code` or a fenced code block below the prompt.

### Option A
First option text or fenced code block.

### Option B [CORRECT]
Second option text or fenced code block.

### Option C
Third option text or fenced code block.

### Option D
Fourth option text or fenced code block.

### Explanation
Detailed explanation of why Option B is correct.

===

## Q2
Second question prompt goes here...

### Option A [CORRECT]
...

### Option B
...

### Option C
...

### Option D
...

### Explanation
...

5. Step-by-Step Workflows for Adding New Content
Workflow A: Adding a New Topic to an Existing Learning Path
Create content/<subject-id>/learn/<NN-topic-slug>.md following Section 4.1.

Open content/<subject-id>/subject.json:

Locate the target object in path[].

Append the new topic entry to topics[] with a unique id, title, file, and optional relatedQuizId / relatedExtraIds.

Increment "version" in subject.json.

Open content/catalog.json:

Increment "version" for <subject-id> to match subject.json, and increment the root "version".

Workflow B: Adding a New Extra Item (USE_CASE, CURIOSITY, HISTORY, EXTERNAL_LINK)
If the item has an article body, create content/<subject-id>/extra/<slug>.md following Section 4.1.

Open content/<subject-id>/subject.json:

Append a new entry to extras[] with a unique id, title, 1–2 sentence summary, valid type, up to 3 short tags, tier ("FREE" or "CORE"), unlockAfterPathId, externalUrl, and file.

optionally link its id inside related path[].topics[].relatedExtraIds.

Increment "version" in subject.json and content/catalog.json.

Workflow C: Adding or Expanding a Quiz
Create or edit content/<subject-id>/quiz/<quiz-slug>.md strictly following Section 4.2.

Count the total number of ## Q<N> blocks in the file.

Open content/<subject-id>/subject.json:

Update or add the quiz entry in quizzes[], ensuring "questionCount" equals the exact number of questions in the .md file.

Increment "version" in subject.json and content/catalog.json.

Workflow D: Creating a Brand-New Subject (content/<new-course-id>/)
Create directory tree: content/<new-course-id>/{assets,learn,extra,quiz}.

Generate subject.json with "version": 1 and at least 1 Learning Path, 1 Extra, and 1 Quiz.

Generate all referenced .md files in learn/, extra/, and quiz/.

Register the new subject inside content/catalog.json and increment the catalog "version".

6. Pre-Commit Compliance Checklist (Self-Verification)
Before finalizing any file generation or modification, verify:

[ ] All JSON files (catalog.json, subject.json) are 100% valid JSON with no trailing commas or comments.

[ ] Every "file" path in subject.json exists on disk at content/<subject-id>/<file>.

[ ] Every local image ../assets/<img.webp> used in Markdown exists in assets/ and is listed in subject.json -> assets[].

[ ] No readingTimeMinutes property exists anywhere.

[ ] Every quiz/*.md question has exactly 4 options (### Option A..D), exactly one [CORRECT] marker, an ### Explanation section, and \n===\n between questions.

[ ] quizzes[].questionCount in subject.json matches the actual count of questions in the .md file.

[ ] "version" numbers in subject.json and catalog.json were incremented so the Study Hub app detects the update.
