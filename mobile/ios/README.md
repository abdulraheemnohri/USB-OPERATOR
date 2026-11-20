# iOS companion

This folder defines the iOS companion direction. iOS does not provide unrestricted generic USB host access to arbitrary devices. The supported initial role is a secure dashboard for a paired Windows/Linux/macOS host agent over HTTPS. Direct accessory support must use Apple-supported accessory frameworks and the device manufacturer's protocol.

Create the Xcode project in Xcode and add ContentView.swift. Configure the host URL only after pairing and certificate validation are implemented; do not hardcode production credentials.
