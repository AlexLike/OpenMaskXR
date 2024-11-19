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
  var transform: AffineTransform3D?

  private let logger = Logger.of(Marker.self)
  private var subscriptions = [EventSubscription]()

  func startTracking(content: some RealityViewContentProtocol) {
    // Track the image in Assets/AR/Marker.
    let marker = AnchorEntity(
      .referenceImage(from: .init(group: "AR", name: "Marker")),
      trackingMode: .continuous
    )

    // Draw an opaque representation of the tracked location.
    let markerVisualization = {
      let entity = ModelEntity(mesh: .generatePlane(width: 0.420, depth: 0.297))
      let material = SimpleMaterial(color: .white.withAlphaComponent(0.5), isMetallic: false)
      entity.model?.materials.append(material)
      return entity
    }()
    marker.addChild(markerVisualization)
    content.add(marker)

    // Once the anchor becomes tracked, publish its transform.
    subscriptions.append(content.subscribe(
      to: ComponentEvents.DidChange.self,
      on: marker,
      componentType: Transform.self
    ) { [weak self] event in
      guard event.entity.isAnchored else { return }
      self?.transform = AffineTransform3D(truncating: event.entity.transformMatrix(relativeTo: nil))
    })
  }
}
