"""Finds the app in app/ and wraps it in an Xcode project the CI Mac can build.

Accepts either an app playground (app/Something.swiftpm/) or plain Swift files
in app/. Writes .preview/build/project.json (an XcodeGen spec) and exports
APP_NAME and BUNDLE_ID for the later steps.
"""
import json
import os
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app"
BUILD = ROOT / ".preview" / "build"
RESULTS = ROOT / "results"
SKIP = {"Package.swift", "Package.resolved", ".build", ".swiftpm", ".DS_Store", ".git"}


def fail(message: str) -> None:
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "setup-error.txt").write_text(message + "\n")
    print(f"::error::{message}")
    sys.exit(1)


def main() -> None:
    if not APP_DIR.is_dir():
        fail("There is no app/ folder. Put your .swiftpm (or your .swift files) inside a folder called app.")

    playgrounds = sorted(p for p in APP_DIR.glob("*.swiftpm") if p.is_dir())
    source = playgrounds[0] if playgrounds else APP_DIR
    if len(playgrounds) > 1:
        print(f"::warning::Found {len(playgrounds)} .swiftpm folders; previewing {source.name}.")

    package = source / "Package.swift"
    package_text = package.read_text(errors="ignore") if package.exists() else ""

    name_match = re.search(r'\.iOSApplication\(\s*name:\s*"([^"]+)"', package_text) or re.search(r'name:\s*"([^"]+)"', package_text)
    display_name = name_match.group(1) if name_match else (source.stem if source != APP_DIR else "My App")
    safe = re.sub(r"[^A-Za-z0-9]", "", display_name) or "MyApp"

    ios_match = re.search(r'\.iOS\(\s*"(\d+(?:\.\d+)?)"\s*\)', package_text) or re.search(r"\.iOS\(\.v(\d+)\)", package_text)
    deployment = ios_match.group(1) if ios_match else "17.0"
    if "." not in deployment:
        deployment += ".0"

    if re.search(r"\.package\s*\(", package_text):
        print("::warning::Your Package.swift uses other Swift packages. This preview doesn't download them yet, so the build may fail.")

    sources = BUILD / "AppSources"
    if BUILD.exists():
        shutil.rmtree(BUILD)
    shutil.copytree(source, sources, ignore=lambda _dir, names: [n for n in names if n in SKIP or n.endswith(".xcodeproj")])

    swift_files = list(sources.rglob("*.swift"))
    if not swift_files:
        fail(f"No .swift files found in {source.relative_to(ROOT)}.")
    if not any("@main" in f.read_text(errors="ignore") for f in swift_files):
        fail("None of your Swift files has @main. Your app needs one struct marked @main that conforms to App.")

    usage = "This preview build may ask for this permission."
    settings = {
        "PRODUCT_NAME": display_name,
        "PRODUCT_BUNDLE_IDENTIFIER": f"com.preview.{safe.lower()}",
        "GENERATE_INFOPLIST_FILE": "YES",
        "INFOPLIST_KEY_CFBundleDisplayName": display_name,
        "INFOPLIST_KEY_UILaunchScreen_Generation": "YES",
        "INFOPLIST_KEY_UIApplicationSceneManifest_Generation": "YES",
        "INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad": "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight",
        "INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone": "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight",
        "INFOPLIST_KEY_NSCameraUsageDescription": usage,
        "INFOPLIST_KEY_NSMicrophoneUsageDescription": usage,
        "INFOPLIST_KEY_NSPhotoLibraryUsageDescription": usage,
        "INFOPLIST_KEY_NSSpeechRecognitionUsageDescription": usage,
        "INFOPLIST_KEY_NSLocationWhenInUseUsageDescription": usage,
        "INFOPLIST_KEY_NSMotionUsageDescription": usage,
        "TARGETED_DEVICE_FAMILY": "1,2",
        "SWIFT_VERSION": "5.0",
        "CODE_SIGNING_ALLOWED": "NO",
        "CODE_SIGNING_REQUIRED": "NO",
        "MARKETING_VERSION": "1.0",
        "CURRENT_PROJECT_VERSION": "1",
    }
    spec = {
        "name": "App",
        "options": {"deploymentTarget": {"iOS": deployment}},
        "targets": {
            "App": {
                "type": "application",
                "platform": "iOS",
                "sources": [{"path": "AppSources"}],
                "settings": {"base": settings},
            }
        },
    }
    (BUILD / "project.json").write_text(json.dumps(spec, indent=2))

    bundle_id = settings["PRODUCT_BUNDLE_IDENTIFIER"]
    env_file = os.environ.get("GITHUB_ENV")
    if env_file:
        with open(env_file, "a") as f:
            f.write(f"APP_NAME={display_name}\nBUNDLE_ID={bundle_id}\nAPP_SOURCE={source.relative_to(ROOT)}\n")

    print(f"App: {display_name}  ({source.relative_to(ROOT)}, {len(swift_files)} Swift files, iOS {deployment}+)")
    os.chdir(BUILD)
    if os.system("xcodegen generate --spec project.json --quiet") != 0:
        fail("Couldn't create the Xcode project from your files.")


if __name__ == "__main__":
    main()
