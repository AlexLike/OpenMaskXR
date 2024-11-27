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
  let mesh: MDLMesh
  let intrinsics: float3x3
  let cameraFrames: [CameraFrame]
  let markerTransform: float4x4
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

    // Export the intrinsics in 4x4-matrix .txt form.
    guard let intrinsicsData = float4x4(extending: intrinsics)
      .matrixString
      .data(using: .utf8)
    else { throw Error.encodingFailed }
    let intrinsicsWrapper = FileWrapper(regularFileWithContents: intrinsicsData)
    
    // Export camera frames and extrinsics as enumerated .jpeg and .txt files.
    let imagesWrapper = FileWrapper(directoryWithFileWrappers: [:])
    let posesWrapper = FileWrapper(directoryWithFileWrappers: [:])
    for (i, cameraFrame) in self.cameraFrames.enumerated() {
      let imageWrapper = try FileWrapper(url: cameraFrame.imageURL)
      imageWrapper.preferredFilename = "\(i).jpeg"
      imagesWrapper.addFileWrapper(imageWrapper)
      
      guard let extrinsicsData = cameraFrame.extrinsics
        .matrixString
        .data(using: .utf8)
      else { throw Error.encodingFailed }
      let extrinsicsWrapper = FileWrapper(regularFileWithContents: extrinsicsData)
      extrinsicsWrapper.preferredFilename = "\(i).txt"
      posesWrapper.addFileWrapper(extrinsicsWrapper)
    }

    // Export the marker transform in 4x4-matrix .txt form.
    guard let markerTransformData = markerTransform
      .matrixString
      .data(using: .utf8)
    else { throw Error.encodingFailed }
    let markerTransformWrapper = FileWrapper(regularFileWithContents: markerTransformData)

    // Wrap all files in a folder
    return FileWrapper(directoryWithFileWrappers: [
      "mesh.obj": meshWrapper,
      "intrinsics.txt": intrinsicsWrapper,
      "markerTransform.txt": markerTransformWrapper,
      "images": imagesWrapper,
      "poses": posesWrapper
    ])
  }
}
