//
//  AppModel.swift
//  OpenMaskVision
//
//  Created by Alexander Zank on 30.09.24.
//

import SwiftUI
import ARKit

/// Maintains app-wide state
@MainActor
@Observable
class AppModel {
  let immersiveSpaceID = "ImmersiveSpace"
  enum ImmersiveSpaceState {
    case closed
    case inTransition
    case open
  }

  var immersiveSpaceState = ImmersiveSpaceState.closed

  var outputFolder = URL.documentsDirectory
  let session = ARKitSession()
}
