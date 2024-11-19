//
//  SensingData.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 12.11.24.
//

@preconcurrency import ModelIO
import Spatial
import SwiftUI
import UniformTypeIdentifiers

struct SensingData {
  var mesh: MDLMesh
  var intrinsics: simd_float3x3
  var markerTransform: AffineTransform3D
  // TODO: Add posed images.
}

extension SensingData: FileDocument {
  static let readableContentTypes = [UTType.folder]

  enum Error: Swift.Error {
    case encodingFailed
    case decodingFailed
  }

  init(configuration _: ReadConfiguration) throws {
    preconditionFailure("SensingData cannot be read.")
  }

  func fileWrapper(configuration _: WriteConfiguration) throws -> FileWrapper {
    // Export the mesh as .OBJ with Model I/O.
    let tmpModelFile = FileManager.default.temporaryDirectory
      .appending(component: "\(UUID())-mesh.obj")
    let mdlAsset = MDLAsset()
    mdlAsset.add(mesh)
    try mdlAsset.export(to: tmpModelFile)
    let meshWrapper = try FileWrapper(url: tmpModelFile)
    meshWrapper.preferredFilename = "mesh.obj"

    // Export the intrinsics in .txt matrix form.
    guard let intrinsicsData = """
    \(intrinsics.columns.0.x) \(intrinsics.columns.1.x) \(intrinsics.columns.2.x)
    \(intrinsics.columns.0.y) \(intrinsics.columns.1.y) \(intrinsics.columns.2.y)
    \(intrinsics.columns.0.z) \(intrinsics.columns.1.z) \(intrinsics.columns.2.z)
    """.data(using: .utf8) else { throw Error.encodingFailed }
    let intrinsicsWrapper = FileWrapper(regularFileWithContents: intrinsicsData)

    // Export the marker transform to .json.
    let markerTransformData = try JSONEncoder().encode(markerTransform)
    let markerTransformWrapper = FileWrapper(regularFileWithContents: markerTransformData)

    // Wrap all files in a folder
    return FileWrapper(directoryWithFileWrappers: [
      "mesh.obj": meshWrapper,
      "intrinsics.txt": intrinsicsWrapper,
      "markerTransform.json": markerTransformWrapper,
    ])
  }
}
