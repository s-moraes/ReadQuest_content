# Working with Android Studio & Apache NetBeans

Senior Java and Kotlin engineers do not all live in vanilla IntelliJ IDEA or VS Code. Many enterprise teams maintain Swing/Java EE/Maven apps in **Apache NetBeans** or build mobile apps in **Android Studio**. Because **Claude Code** operates at the repository and terminal level, it pairs cleanly with both IDEs—even when an official companion plugin does not exist.

---

## Android Studio + Claude Code

Because Android Studio is built on the JetBrains IntelliJ Platform, it shares the same split-workflow strengths as IntelliJ IDEA, plus Android-specific CLI tooling (`adb`, `gradle`, `emulator`).

### 1. Fast Gradle & ADB Verification Loops
Android builds can be notoriously slow if an agent triggers full APK packaging on every edit. Guide Claude Code in `CLAUDE.md` to use **JVM unit tests** first and **lint/instrumentation** second:

```markdown
## Android Build & Test Commands
- Fast JVM unit tests (no emulator):
  `./gradlew :app:testDebugUnitTest --tests "*.AuthViewModelTest" -q`
- Kotlin / Android Lint:
  `./gradlew :app:lintDebug -q`
- Install & run instrumented test on connected device/emulator:
  `./gradlew :app:connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=...`
```

### 2. Pairing CLI Reasoning with Android Studio Visual Tools
| Task | Best Tool | Why |
| :--- | :--- | :--- |
| **ViewModels, Repositories, Room DAOs & unit tests** | **Claude Code** | Fast cross-file Kotlin/Java generation and test loops |
| **Logcat crash triage (`adb logcat -d`)** | **Claude Code** | Pipe `adb logcat -d -t 200 *:E \| claude -p "..."` directly |
| **Compose Preview & Layout Inspector** | **Android Studio** | Visual UI alignment, recomposition counts, and view hierarchy |
| **Memory Profiler, Network Inspector & ANR traces** | **Android Studio** | Live heap dumps and main-thread frame timelines |

Because Android Studio also supports JetBrains companion plugins, you can share active diagnostics or run Claude Code in Android Studio's embedded terminal (or an external `tmux` pane).

---

## Apache NetBeans + Claude Code

**Apache NetBeans** remains a staple in legacy Java EE / Jakarta EE, Swing (`Matisse` GUI builder), and classic Maven/Ant shops. Unlike VS Code or JetBrains, NetBeans does not have a dedicated Claude Code companion plugin—which makes **terminal-first orchestration** the ideal pattern.

### 1. How the File-Sync Workflow Works
1. Run `claude` in a terminal (or `tmux` pane) at the project root.
2. Keep NetBeans open on the same repository. NetBeans automatically detects external filesystem modifications when you focus the window (or via **Source -> Scan for External Changes**).
3. Let Claude Code handle cross-file edits, Maven pom updates, and JUnit runs (`./mvnw test -q`), while you use NetBeans for:
   - **Swing Form Editor (`.form` + `.java`):** Never let an agent hand-edit NetBeans' `.form` XML or `GEN-BEGIN` / `GEN-END` guarded blocks—keep `CLAUDE.md` explicit about leaving `.form` files to NetBeans!
   - **JPDA Step-Debugging & Ant/Maven Payara/WildFly deploys:** Attach NetBeans' debugger to your local application server when tracing complex EJB/JSF state.

### 2. Essential `CLAUDE.md` Rule for NetBeans Projects

```markdown
## NetBeans Guardrails
- NEVER edit `*.form` files or code inside `// <editor-fold>` /
  `//GEN-BEGIN` / `//GEN-END` guarded blocks; those are managed
  exclusively by the NetBeans GUI Builder.
- Do not modify `nbproject/private/` (user-local IDE state).
```

Adding that two-line rule prevents one of the most frustrating NetBeans corruptions when using any AI coding agent.
