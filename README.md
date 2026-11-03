# ReadQuest Study Content Repository

[![Validate Content Integrity](https://github.com/s-moraes/ReadQuest_content/actions/workflows/validate-content.yml/badge.svg)](https://github.com/s-moraes/ReadQuest_content/actions/workflows/validate-content.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Subjects](https://img.shields.io/badge/Subjects-5-success.svg)](#-available-subjects)
[![Topics](https://img.shields.io/badge/Topics-60-informational.svg)](#-available-subjects)
[![Quizzes](https://img.shields.io/badge/Quizzes-20-purple.svg)](#-available-subjects)
[![Target App](https://img.shields.io/badge/App-ReadQuest-orange.svg)](https://github.com/s-moraes/ReadQuest)

Official and curated technical study material designed specifically for **[ReadQuest](https://github.com/s-moraes/ReadQuest)** (`com.saulo.readquest`), an offline-first native Android study hub built with Jetpack Compose.

This repository hosts structured learning paths, architectural case studies, deep-dive extras, and active-recall assessments ready to be synced directly to your Android device for 100% offline study.

---

## 🚀 Quick Setup with ReadQuest

1. Open the **ReadQuest** application on your Android device.
2. Tap the **Settings** gear icon (⚙️) in the top-right corner.
3. In **Content Sync & Repository**, enter the repository URL:
   ```text
   https://github.com/s-moraes/ReadQuest_content
   ```
4. Tap **Sync Content from Web**.
5. Once synchronization finishes, all courses, quizzes, and diagrams are stored locally and accessible offline!

---

## 📚 Available Subjects

| Subject | ID | Paths | Topics | Quizzes | Extras | Description |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **System Design & Architecture** | `system-design` | 3 | 15 | 4 | 6 | Distributed systems, scalability, latency, CAP & PACELC theorems, data replication, and database sharding. |
| **Prep4Java: Foundations** | `java-foundations` | 4 | 18 | 6 | 4 | Java syntax, memory model, loops, operators, collections, exceptions, and certification preparation. |
| **Database Migrations with Flyway** | `flyway-migrations` | 3 | 7 | 2 | 4 | Schema evolution, versioned migrations, repeatable scripts, Spring Boot integration, and zero-downtime practices. |
| **Cloud-Native Concurrency & State** | `cloud-native-concurrency` | 2 | 6 | 3 | 4 | Microservices state handling, distributed coordination, cloud database locks, actor toolkits, and reactive parallelism. |
| **JEV-as-a-Judge: Decision-Only AI Evaluation** | `jev-as-a-judge` | 5 | 14 | 5 | 5 | Decision-only evaluation, calibrated confidence cascades, LLM-as-a-Judge cost reduction, production AI observability, and CMU empirical benchmarks. |

**Total:** 5 Complete Subjects • 60 In-Depth Lessons • 20 Self-Paced Quizzes • 23 Real-World Extras & Case Studies

---

## 📂 Content Architecture

The repository adheres strictly to the schema expected by the ReadQuest content engine:

```text
ReadQuest_content/
├── .github/workflows/
│   └── validate-content.yml       # Automated CI validation pipeline
├── content/
│   ├── catalog.json               # Master catalog registering all available subjects
│   ├── PROMPT_SYSTEM_CONTENT_GEN.md # Prompt guide for authoring new content with LLMs
│   └── <subject-id>/              # E.g. system-design, java-foundations
│       ├── subject.json           # Manifest declaring syllabus, paths, extras, and quizzes
│       ├── assets/                # Diagrams, WebP/SVG/PNG illustrations
│       ├── learn/                 # Topic markdown lessons (ordered sequentially)
│       ├── extra/                 # Enrichment articles, use cases, and deep dives
│       └── quiz/                  # Markdown assessment files
└── scripts/
    └── validate_content.py        # Offline local validator script
```

### Manifest Specifications

#### 1. Catalog (`content/catalog.json`)
Registers available subjects and points to their manifests:
```json
{
  "version": 5,
  "subjects": [
    {
      "id": "system-design",
      "title": "System Design & Architecture",
      "description": "Distributed systems, scalability, load balancing, caching, and database architecture.",
      "version": 1,
      "path": "content/system-design/subject.json"
    }
  ]
}
```

#### 2. Subject Manifest (`content/<subject-id>/subject.json`)
Declares modular learning paths, topics, extra reading materials, and quizzes:
- IDs must be `kebab-case`.
- Topics must point to valid `.md` files in `learn/`.
- Quizzes must specify `questionCount` matching the exact number of questions in `quiz/*.md`.
- Extras can specify `tier`: `"FREE"` or `"CORE"` (locked until prerequisite path completion).

#### 3. Quiz Markdown Format (`quiz/*.md`)
Quizzes require a strict syntax parsed directly by the Android app:
- Every question begins with `## Q<N>` (e.g. `## Q1`).
- Separate distinct questions with `\n===\n` (do not use `---`).
- Exactly 4 options (`### Option A` through `### Option D`).
- Designate the correct option with ` [CORRECT]` on its header line.
- End each question with an `### Explanation` block.

Example:
```markdown
## Q1: What guarantees linearizability in distributed storage?

### Option A
Eventual consistency across all asynchronous read replicas.

### Option B [CORRECT]
A strict global real-time ordering of operations so every read sees the latest write.

### Option C
Optimistic concurrency control with arbitrary retry windows.

### Option D
Multi-master master-slave topology without split-brain detectors.

### Explanation
Linearizability ensures operations appear to take effect instantaneously at some point in time between invocation and response, establishing a global real-time order.
```

---

## 🧪 Content Validation

Before committing or pushing new lessons or courses, you can validate the entire repository locally:

```bash
python3 scripts/validate_content.py
```

The script will verify:
- [x] Valid JSON syntax in `catalog.json` and all `subject.json` manifests.
- [x] All topic, extra, quiz, and asset files exist on disk.
- [x] No empty markdown lessons.
- [x] Exact match between `questionCount` in manifest and parsed `## Q<N>` questions.
- [x] Every question contains exactly one `[CORRECT]` tag and an `### Explanation` section.

Every push or pull request to `main` is also automatically checked via GitHub Actions.

---

## 🤖 Authoring New Content with AI

To rapidly author new high-quality technical subjects matching ReadQuest's format, use the structured generation prompt located at:

📄 [`content/PROMPT_SYSTEM_CONTENT_GEN.md`](content/PROMPT_SYSTEM_CONTENT_GEN.md)

Simply supply your target subject, topics list, and desired difficulty level to your LLM of choice (Gemini, Claude, GPT), and it will produce ready-to-use manifests and markdown lessons conforming to all validation rules.

---

## 🔗 Related Projects

- **[ReadQuest Android App](https://github.com/s-moraes/ReadQuest)**: The native Jetpack Compose companion app.

---

## 📄 License

This repository and its technical study contents are licensed under the **[MIT License](LICENSE)**.
Feel free to fork, expand, and tailor courses to your own study roadmap!
