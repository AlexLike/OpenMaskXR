//
//  ImmersiveView.swift
//  OpenMaskVision
//
//  Created by Alexander Zank on 30.09.24.
//

import ARKit
import ModelIO
import RealityKit
import SceneKit
import SwiftUI

struct ImmersiveView: View {
  @Environment(AppModel.self) var appModel

  var body: some View {
    RealityView { content in
      let meshResource = MeshResource.generateCylinder(height: 1, radius: 1)
      let entity = ModelEntity(mesh: meshResource)
      entity.transform.translation += [0, 1, -2]
      content.add(entity)

      guard let rkMesh = meshResource.contents.models.first?.parts.first else {
        print("Could not load mesh")
        return
      }

//          try? "hello".write(toFile: URL.documentsDirectory.appendingPathComponent("hey.txt").path(), atomically: true, encoding: .utf8)

      if SceneReconstructionProvider.isSupported
//              && CameraFrameProvider.isSupported
      {
        print("Scene Reconstruction begins")

        let sceneReconstructionProvider = SceneReconstructionProvider()
//            let cameraFrameProvider = CameraFrameProvider()

        Task { @MainActor in
          for await anchorUpdate in sceneReconstructionProvider.anchorUpdates {
            try? anchorUpdate.anchor.geometry.objRepresentation.write(
              to: .documentsDirectory.appendingPathComponent("\(anchorUpdate.timestamp).obj"),
              atomically: true,
              encoding: .utf8
            )
          }
        }

        try! await appModel.session.run([sceneReconstructionProvider])

//            Task {
//              for await cameraFrameUpdate in cameraFrameProvider.cameraFrameUpdates(for: .supportedVideoFormats(for: .main, cameraPositions: [.left]).first!)! {
//                print(cameraFrameUpdate.description)
//              }
//            }
      }
    }
  }
}

#Preview(immersionStyle: .mixed) {
  ImmersiveView()
    .environment(AppModel())
}
