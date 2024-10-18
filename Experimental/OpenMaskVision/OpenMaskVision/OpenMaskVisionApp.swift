//
//  OpenMaskVisionApp.swift
//  OpenMaskVision
//
//  Created by Alexander Zank on 30.09.24.
//

import SwiftUI

@main
struct OpenMaskVisionApp: App {
  @State private var appModel = AppModel()

  var body: some Scene {
    WindowGroup {
      ContentView()
        .environment(appModel)
    }
    .windowResizability(.contentSize)

    ImmersiveSpace(id: appModel.immersiveSpaceID) {
      ImmersiveView()
        .environment(appModel)
        .onAppear {
          appModel.immersiveSpaceState = .open
        }
        .onDisappear {
          appModel.immersiveSpaceState = .closed
        }
    }
    .immersionStyle(selection: .constant(.mixed), in: .mixed)
  }
}
