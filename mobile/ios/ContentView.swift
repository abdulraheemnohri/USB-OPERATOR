import SwiftUI
struct ContentView: View {
 @State private var hostURL = "https://your-paired-host.example"
 @State private var status = "Not connected"
 var body: some View { NavigationStack { Form { Section("USB-OPERATOR host") { TextField("Paired host URL",text:$hostURL).textInputAutocapitalization(.never).keyboardType(.URL); Button("Check connection") { Task { await checkHost() } }; Text(status).foregroundStyle(.secondary) }; Section("Safety") { Text("This companion is a dashboard. Hardware commands remain governed by the paired host agent's local policy and approval workflow.") } }.navigationTitle("USB-OPERATOR") } }
 private func checkHost() async { guard let url=URL(string:hostURL+"/health") else { status="Invalid URL"; return }; do { let (_,response)=try await URLSession.shared.data(from:url); status=(response as? HTTPURLResponse)?.statusCode == 200 ? "Host reachable" : "Host returned an error" } catch { status="Connection failed: " + error.localizedDescription } }
}
