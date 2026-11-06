import SwiftUI

/// A small starter screen. Replace this whole app folder with your own.
struct ContentView: View {
    @State private var taps = 0

    private let steps: [(String, String)] = [
        ("square.and.pencil", "Edit the Swift files in the app folder"),
        ("arrow.up.circle", "Commit and push to main"),
        ("hammer", "A GitHub Mac builds your app"),
        ("photo.on.rectangle", "Screenshots appear in preview-results")
    ]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    VStack(alignment: .leading, spacing: 8) {
                        Image(systemName: "sparkles")
                            .font(.system(size: 44))
                            .foregroundStyle(.indigo)
                        Text("It runs!")
                            .font(.largeTitle.bold())
                        Text("This app was built and screenshotted on a free GitHub Mac. You didn't need a Mac, an iPhone or an iPad.")
                            .font(.title3)
                            .foregroundStyle(.secondary)
                    }

                    VStack(alignment: .leading, spacing: 14) {
                        ForEach(Array(steps.enumerated()), id: \.offset) { index, step in
                            HStack(spacing: 14) {
                                Text("\(index + 1)")
                                    .font(.headline.monospacedDigit())
                                    .frame(width: 32, height: 32)
                                    .background(.indigo.opacity(0.15), in: Circle())
                                Label(step.1, systemImage: step.0)
                                    .font(.body)
                            }
                        }
                    }
                    .padding(20)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(.background.secondary, in: RoundedRectangle(cornerRadius: 20, style: .continuous))

                    Button {
                        taps += 1
                    } label: {
                        Label(taps == 0 ? "Tap me" : "Tapped \(taps) times", systemImage: "hand.tap")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)

                    NavigationLink("About this template") { AboutView() }
                }
                .padding(24)
                .frame(maxWidth: 700, alignment: .leading)
                .frame(maxWidth: .infinity)
            }
            .navigationTitle("Hello App")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct AboutView: View {
    var body: some View {
        List {
            Section("What this is") {
                Text("A starter app for the iOS Preview Without a Mac template.")
            }
            Section("Good to know") {
                Label("The camera, haptics and Apple Pencil don't exist in the simulator", systemImage: "info.circle")
                Label("Only Apple's own frameworks are available", systemImage: "shippingbox")
                Label("Each run takes about 8–12 minutes", systemImage: "clock")
            }
        }
        .navigationTitle("About")
    }
}
