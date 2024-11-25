//
//  EnvironmentMesh.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 17.11.24.
//

import ModelIO
import RealityKit
import Spatial
import SwiftUI

@Observable @MainActor
class EnvironmentMesh {
  /// Whether to render environment mesh chunks.
  let isVisualized: Bool
  
  init(isVisualized: Bool) {
    self.isVisualized = isVisualized
  }
  
  /// The RealityKit entities holding chunks of the environment mesh.
  private(set) var reconstructionEntities = Set<Entity>()

  private let logger = Logger.of(Marker.self)
  private var subscriptions = [EventSubscription]()

  /// Begin collecting reconstruction entities from a RealityKit scene.
  ///
  /// A reconstruction entity has a `SceneUnderstandingComponent` and an active `ModelComponent`.
  /// It describes one chunk of the environment mesh, and updates over time to better approximate reality.
  /// - Parameter realityViewContent: The `RealityView` content proxy.
  func startReconstruction(realityViewContent: some RealityViewContentProtocol) {
    // Listen for mesh updates on reconstruction entities.
    subscriptions.append(realityViewContent.subscribe(
      to: ComponentEvents.DidActivate.self,
      componentType: ModelComponent.self
    ) { [weak self] event in
      guard let self,
            event.entity.components.has(SceneUnderstandingComponent.self),
            var modelComponent = event.entity.components[ModelComponent.self]
      else { return }

      let (isNew, _) = reconstructionEntities.insert(event.entity)
      if isNew {
        logger.info("Discovered new reconstruction entity.")

        // Highlight in a color that doesn't mimick its neighboring chunks.
        if isVisualized {
          let material = SimpleMaterial(
            color: .debug(i: reconstructionEntities.count),
            isMetallic: false
          )
          modelComponent.materials.append(material)
          event.entity.components.set(modelComponent)
        }
      }
    })
  }

  /// Merges all reconstruction mesh chunks into one Model I/O environment mesh.
  func finalizeReconstruction() async -> MDLMesh {
    var vertices = [SIMD3<Float>]()
    var indices = [UInt32]()

    for entity in reconstructionEntities {
      guard entity.isActive else {
        logger.info("Ignoring inactive reconstruction entity.")
        continue
      }

      // Access the model of this reconstruction entity.
      guard let model = entity.components[ModelComponent.self],
            model.mesh.contents.instances.count == 1,
            let modelTransform = model.mesh.contents.instances.first?.transform,
            model.mesh.contents.models.count == 1,
            let modelParts = model.mesh.contents.models.first?.parts,
            modelParts.count == 1,
            let modelPart = modelParts.first,
            let modelIndices = modelPart.triangleIndices
      else {
        logger.info("Ignoring reconstruction entity without a valid model.")
        continue
      }

      // Append its triangle indices, making sure that they match the new vertex indices.
      let indexOffset = UInt32(vertices.count)
      for index in modelIndices {
        indices.append(index + indexOffset)
      }

      // Append its transformed vertices, making sure to transform them to world space first.
      let transform = entity.transformMatrix(relativeTo: nil) * modelTransform
      for position in modelPart.positions.elements {
        let p = transform * SIMD4(position, 1)
        vertices.append(SIMD3(p.x, p.y, p.z) / p.w)
      }

      await Task.yield()
    }

    // Copy the mesh data into a Model I/O buffer.
    let vertexBuffer = vertices.withUnsafeMutableBufferPointer { pointer in
      MDLMeshBufferData(
        type: .vertex,
        data: Data(
          bytesNoCopy: pointer.baseAddress!,
          count: pointer.count * MemoryLayout<SIMD3<Float>>.stride,
          deallocator: .none
        )
      )
    }
    let vertexDescriptor = MDLVertexDescriptor()
    vertexDescriptor.attributes = [MDLVertexAttribute(
      name: MDLVertexAttributePosition,
      format: .float3,
      offset: 0,
      bufferIndex: 0
    )]
    vertexDescriptor.layouts = [MDLVertexBufferLayout(stride: MemoryLayout<SIMD3<Float>>.stride)]

    // Copy the index data into a Model I/O buffer.
    let indexBuffer = indices.withUnsafeMutableBufferPointer { pointer in
      MDLMeshBufferData(
        type: .index,
        data: Data(
          bytesNoCopy: pointer.baseAddress!,
          count: pointer.count * MemoryLayout<UInt32>.stride,
          deallocator: .none
        )
      )
    }
    let submesh = MDLSubmesh(
      indexBuffer: indexBuffer,
      indexCount: indices.count,
      indexType: .uInt32,
      geometryType: .triangles,
      material: nil
    )

    // Assemble the Model I/O mesh from vertices and indices.
    let mesh = MDLMesh(
      vertexBuffer: vertexBuffer,
      vertexCount: vertices.count,
      descriptor: vertexDescriptor,
      submeshes: [submesh]
    )

    return mesh
  }
}
