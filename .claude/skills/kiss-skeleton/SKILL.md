---
name: kiss-skeleton
description: |
  Framework-agnostic project structure guide following the KISS principle. Use this skill when starting a new project, adding a new feature and unsure where to put the code, deciding between views/services/utils/controllers/logic/core, or when a codebase is growing and everything is ending up in a single folder. Also use it when the user asks how to organize app logic, what the difference between a service and a util is, or how to structure a clean separation between UI and business logic. Works with any language or framework.
---

# KISS Project Structure

The goal is simple: every file has an obvious home, and you never have to ask "where does this go?" The answer comes from what the code *does*, not from the framework it uses.

## Recommended layout

```
my-project/
├── assets/               ← static files bundled with the app
│   ├── icons/
│   ├── fonts/
│   ├── images/
│   └── lang/             ← i18n / localization files
│
├── data/                 ← runtime-generated, user-owned (gitignore this)
│   ├── config.json
│   └── cache/
│
├── docs/                 ← technical documentation for developers
│   ├── architecture.md   ← system design decisions and layer responsibilities
│   ├── builds/           ← build, packaging, and release guides
│   └── api/              ← internal API contracts, endpoint specs
│
└── app/
    ├── views/            ← UI only: render state, forward events
    ├── services/         ← stateful operations and external systems
    ├── controllers/      ← orchestration (only when needed)
    ├── logic/            ← stateless domain rules and algorithms
    ├── utils/            ← pure helper functions
    └── core/             ← app-wide: config, i18n, constants, base classes
```

Not every project needs every folder. Start with `views/`, `services/`, and `utils/`. Add `logic/`, `controllers/`, and `core/` when the need is clear — not in advance.

---

## What goes where

### `views/`

Render state. Forward user events. That's it.

A view is correct when you can describe it as: *"when the state is X, show Y; when the user does Z, call the service."* If a view method is computing something beyond that, it belongs elsewhere.

```
✓ Display a list of files from a service
✓ Show a spinner while an operation is running
✓ Call service.start() when a button is clicked
✗ Compute whether the server should be running
✗ Read/write config files
✗ Format a file size (that's logic or utils)
```

### `services/`

Stateful operations. Services own connections, sessions, and mutable app state. They interact with external systems: file system, network, databases, hardware.

```
✓ ServerService  — starts/stops an HTTP server, holds the session
✓ ConfigService  — reads and writes the config file
✓ FileService    — lists, downloads, uploads files
✗ Pure computation (that's logic or utils)
✗ UI rendering (that's views)
```

A service is the answer to "who manages the state of X?" — one service per domain area.

### `logic/`

Stateless domain rules. No side effects, no imports from views or services. Takes input, returns output.

Logic is different from utils in that it knows about your domain — it encodes *your* rules, not just string manipulation.

```
✓ validate_port(value: int) -> bool
✓ compute_greeting(hour: int) -> str          # domain rule: what counts as "morning"
✓ build_qr_payload(token: str) -> dict
✓ parse_upload_limit(raw: str) -> int | None
✗ format_bytes(n: int) -> str                # no domain knowledge → utils
✗ normalize_path(p: str) -> str              # generic → utils
```

### `utils/`

Pure, generic helper functions. No domain knowledge. Could be extracted into a library and used in a completely different project.

```
✓ format_uptime(seconds: int) -> str
✓ normalize_path(path: str, kind: str) -> str
✓ truncate(text: str, max_len: int) -> str
✗ validate_port(value)   # knows about your port rules → logic
✗ anything with state    # → services
```

The rule: if you could paste this function into a different app with zero changes, it's a util.

### `controllers/`

Thin orchestration layer between views and services. Only add this when a single user action needs to coordinate multiple services — otherwise, views can call services directly.

```
✓ A "Save settings" action that updates ConfigService, restarts ServerService,
  and refreshes i18n — all as one atomic step
✗ An action that only calls one service (the view can do this directly)
```

When a view starts importing three different services to handle one button click, that's the signal to introduce a controller.

### `core/`

App-wide infrastructure that doesn't fit elsewhere. Think of it as the foundation everything else builds on.

```
✓ Config schema / defaults
✓ i18n / translation loader
✓ App-level constants and enums
✓ Base classes for views or services
✓ Dependency injection container (if used)
✗ Business logic (that's logic/)
✗ Utility functions (that's utils/)
```

### `docs/`

Technical documentation for developers — not end-user manuals. If a human maintainer needs to understand a non-obvious decision, it goes here. If a user needs to know how to use the product, it goes elsewhere (README, help screens, website).

```
docs/
├── architecture.md     ← why the layers are structured as they are
├── builds/             ← how to compile, package, and release
│   └── macos.md
└── api/                ← internal contracts, endpoint specs, auth flow
```

The test for whether something belongs in `docs/`: "would a new developer on this project need to read this to contribute confidently?" If yes — docs. If it's just a reminder of how to run the app — README.

### `assets/`

Static files bundled and shipped with the app. Never generated at runtime.

```
assets/
├── icons/          ← app icons in various sizes
├── fonts/          ← custom typefaces
├── images/         ← illustrations, backgrounds
└── lang/
    ├── en.json     ← all UI strings keyed
    └── es.json
```

### `data/`

Created at runtime, owned by the user or the running instance. Always gitignore this directory.

```
data/
├── config.json     ← user preferences (written by ConfigService)
└── cache/          ← ephemeral, can be deleted safely
```

---

## Decision guide

When you don't know where something goes, ask these questions in order:

1. **Does it render UI or respond to user input?** → `views/`
2. **Does it own state, manage connections, or talk to external systems?** → `services/`
3. **Is it a domain rule or validation specific to this app?** → `logic/`
4. **Is it a generic helper with no domain knowledge?** → `utils/`
5. **Does it coordinate multiple services for one user action?** → `controllers/`
6. **Is it shared infrastructure the whole app depends on?** → `core/`

---

## Layer dependencies (what can import what)

```
views      → services, logic, utils, core
controllers → services, logic, utils, core
services   → logic, utils, core
logic      → utils, core
utils      → core (rarely)
core       → (nothing in app/)
```

The hard rule: **lower layers never import from higher layers.**

- `services/` never imports from `views/`
- `logic/` never imports from `services/` or `views/`
- `utils/` never imports from `logic/`, `services/`, or `views/`

If you find yourself doing any of the above, the code is in the wrong layer.

---

## Growth path

Start minimal. Add layers only when the need is concrete:

| Project stage | Layers to use |
|---|---|
| Prototype / small feature | `views/` + `utils/` |
| Growing app with external integrations | add `services/` |
| Domain rules multiplying | add `logic/` |
| Actions coordinating 2+ services | add `controllers/` |
| Shared config, i18n, constants | add `core/` |

A project with three files does not need six folders.
