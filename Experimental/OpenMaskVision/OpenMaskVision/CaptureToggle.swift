//
//  ToggleImmersiveSpaceButton.swift
//  OpenMaskVision
//
//  Created by Alexander Zank on 30.09.24.
//

import SwiftUI

struct CaptureToggle: View {
  @Environment(AppModel.self) private var appModel

  @Environment(\.dismissImmersiveSpace) private var dismissImmersiveSpace
  @Environment(\.openImmersiveSpace) private var openImmersiveSpace

  var body: some View {
    Button {
      Task { @MainActor in
        switch appModel.immersiveSpaceState {
        case .open:
          appModel.immersiveSpaceState = .inTransition
          await dismissImmersiveSpace()

        case .closed:
          appModel.immersiveSpaceState = .inTransition
          switch await openImmersiveSpace(id: appModel.immersiveSpaceID) {
          case .opened:
            break

          case .userCancelled, .error:
            fallthrough

          @unknown default:
            appModel.immersiveSpaceState = .closed
          }

        case .inTransition:
          break
        }
      }
    } label: {
      Text(appModel
        .immersiveSpaceState == .open ? "End Capture" : "Start Capture")
    }
    .disabled(appModel.immersiveSpaceState == .inTransition)
    .fontWeight(.semibold)
  }
}
