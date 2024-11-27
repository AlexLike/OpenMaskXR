//
//  Marker.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 17.11.24.
//

import OSLog
import RealityKit
import Spatial
import SwiftUI

@Observable @MainActor
class Marker {
  /// Whether to render a virtual marker at the perceived location.
  let isVisualized: Bool

  init(isVisualized: Bool) {
    self.isVisualized = isVisualized
  }

  private let logger = Logger.of(Marker.self)
  private let marker = AnchorEntity(
    .referenceImage(from: .init(group: "AR", name: "Marker")),
    trackingMode: .continuous
  )

  func startTracking(content: some RealityViewContentProtocol) {
    // Track the image in Assets/AR/Marker.
    content.add(marker)

    // Draw an opaque representation of the tracked location.
    if isVisualized {
      let markerVisualization = {
        let entity = ModelEntity(mesh: .generatePlane(width: 0.420, depth: 0.297))
        let material = SimpleMaterial(color: .white.withAlphaComponent(0.5), isMetallic: false)
        entity.model?.materials.append(material)
        return entity
      }()
      marker.addChild(markerVisualization)
    }
  }

  var transform: float4x4? {
    marker.isActive
      ? marker.transformMatrix(relativeTo: nil)
      : nil
  }
}
