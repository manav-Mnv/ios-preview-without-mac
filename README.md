# 📱 iOS Preview Without a Mac

**Build your SwiftUI app and see it running on an iPhone and an iPad, without owning a Mac, an iPhone or an iPad.**

You push your Swift code. A free Mac at GitHub builds it, runs it in Apple's iPhone and iPad simulators, and sends back screenshots in light and dark mode, plus a short video. If your code has mistakes, you get the errors in plain English instead.

All you need is a **GitHub account** and a **web browser**.

---

## How to use it (5 minutes)

### 1. Make your own copy
Click the green **Use this template** button → **Create a new repository**. Give it a name and click **Create**.

> Public repos get **unlimited** free build time. Private repos get about 200 Mac minutes a month (about 20 previews). Keep a competition entry private.

### 2. Run it once with the example app
Your copy already contains a small example app in `app/HelloApp.swiftpm`. Open the **Actions** tab, then **Preview my app** → **Run workflow**. About 10 minutes later, open the **`preview-results`** branch (the branch menu at the top-left of the **Code** tab) and you'll see the screenshots.

### 3. Put your own app in
Replace what's inside the `app/` folder with your app. Either:

- **An app playground:** an `.swiftpm` folder from Swift Playground or Xcode. Upload it with **Add file → Upload files** (drag the whole folder in).
- **Just Swift files:** put your `.swift` files straight into `app/`. One of them needs `@main`:

```swift
import SwiftUI

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

No computer at all? Press **`.`** (the full-stop key) on your repo's page. It opens **github.dev**, a full code editor in your browser.

### 4. Push, wait, look
Every push to `main` starts a new preview. Watch it in **Actions**. When it finishes, open the **`preview-results`** branch:

| You get | When |
|---|---|
| iPhone and iPad screenshots, light and dark mode | The build worked |
| A short video of the app starting (`iphone-launch.mp4`) | The build worked |
| A list of errors with 💡 hints | Something didn't compile |
| A crash report | The app built but crashed while running |

---

## Optional: screenshot more than the first screen
The robot can't tap buttons, so for a deeper screen your app must be able to *open* that screen by itself. Use a launch argument:

1. In your app, read it: `UserDefaults.standard.string(forKey: "screen")`
2. Show the matching screen when it equals, say, `"settings"`.
3. Add a line to `screens.txt`:

```
settings | -screen settings
```

The example app does this for its About screen. Look at `app/HelloApp.swiftpm/HelloApp.swift`.

---

## What it can't do
- **No live tapping.** You see still pictures and a short video, not a Mac you can control. Each change takes about 8–12 minutes to show up.
- **No camera, haptics, Apple Pencil, motion or real AR.** The simulator doesn't have them. If your app needs them, add a sample or demo mode so it still shows something.
- **No packages from the internet yet.** Apple's built-in frameworks work: SwiftUI, Vision, Core ML, Charts, AVFoundation, SwiftData and so on. Swift packages listed in `Package.swift` aren't downloaded.
- **Not a replacement for a real device before a competition.** For the Swift Student Challenge, run your final playground at least once in Swift Playground or Xcode on a real Mac or iPad (borrow one from a club or lab).
- **No App Store uploads.** That needs Apple signing certificates, which is out of scope.

---

## Common problems

| Problem | Fix |
|---|---|
| "There is no app/ folder" | Keep the folder name exactly `app`, in the top level of the repo. |
| "None of your Swift files has @main" | Add an `@main struct … : App` (see step 3). |
| `no such module 'X'` | `X` is a third-party package. Remove it, or use an Apple framework instead. |
| The screenshot shows a blank or launch screen | Your app takes a while to start. Add a repository variable `PREVIEW_WAIT` = `15`, or put `PREVIEW_WAIT: 15` under `env:` in the workflow. |
| The run is stuck in "Queued" | GitHub's free Macs are busy. Wait a few minutes. |

---

## How it works
1. `.github/workflows/preview.yml` asks GitHub for a `macos-latest` machine and picks its newest Xcode.
2. `.preview/make_project.py` finds your app in `app/` and, using [XcodeGen](https://github.com/yonaskolb/XcodeGen), wraps it in a temporary Xcode project.
3. `.preview/build.sh` builds it for the iOS Simulator with `xcodebuild` and saves the errors in plain text.
4. `.preview/shoot.sh` boots an iPhone and an iPad simulator with `xcrun simctl`, installs the app, launches it, and takes screenshots in light and dark mode, plus your extra screens.
5. `.preview/report.py` writes a `README.md` with the pictures and error hints, and `.preview/publish.sh` force-pushes it to the `preview-results` branch.

You never need to edit anything in `.preview/` or `.github/`.

---

Made by [Manav Sinh](https://github.com/manav-Mnv) for students learning Swift without Apple hardware. MIT licensed: use it, copy it, improve it.
