import SwiftUI

@main
struct HelloApp: App {
    var body: some Scene {
        WindowGroup {
            // Launch with `-screen about` (see screens.txt) to open the About screen directly.
            if UserDefaults.standard.string(forKey: "screen") == "about" {
                AboutView()
            } else {
                ContentView()
            }
        }
    }
}
