//
//  ContentView.swift
//  OpenMaskVision
//
//  Created by Alexander Zank on 30.09.24.
//

import RealityKit
import RealityKitContent
import SwiftUI

struct ContentView: View {
  var body: some View {
    VStack(alignment: .center) {
      Label("OpenMaskXR Scene Capture", systemImage: "vision.pro")
        .labelStyle(.titleAndIcon)
        .font(.title)
        .multilineTextAlignment(.center)
      Text("Collect posed RGB frames and reconstruction meshes of the environment.")
        .multilineTextAlignment(.center)
      HStack {
        CaptureToggle()
      }
    }
    .frame(maxWidth: 300)
    .padding()
  }
}

#Preview(windowStyle: .automatic) {
  ContentView()
    .environment(AppModel())
}
