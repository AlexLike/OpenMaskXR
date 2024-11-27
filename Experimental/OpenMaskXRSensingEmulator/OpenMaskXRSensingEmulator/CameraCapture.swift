//
//  CameraCapture.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 25.11.24.
//

import ARKit
import CoreImage.CIFilterBuiltins
import SwiftUI

struct CameraFrame {
  let timestamp: TimeInterval
  let extrinsics: float4x4
  let imageURL: URL
}

@Observable @MainActor
class CameraCapture {
  static let logger = Logger.of(CameraCapture.self)

  var intrinsics: float3x3?
  var frames = [CameraFrame]()

  private let imageFolder = {
    let imageFolder = FileManager.default.temporaryDirectory
      .appending(component: "\(UUID())-images")
    try? FileManager.default.createDirectory(at: imageFolder, withIntermediateDirectories: true)
    return imageFolder
  }()
  
  private let ciContext = CIContext()
  private var task: Task<Void, Never>?

  #if os(iOS)

    func startFrameDelivery(arSession: ARSession) {
      task = Task {
        // Query the most recent camera frame at 5fps.
        while (try? await Task.sleep(for: .milliseconds(200))) != nil {
          guard let frame = arSession.currentFrame
          else {
            Self.logger.info("Ignoring missing camera frames.")
            continue
          }
          
          // Populate intrinsics and process frames.
          intrinsics = intrinsics ?? frame.camera.intrinsics
          processFrame(
            timestamp: frame.timestamp,
            extrinsics: frame.camera.transform,
            cvPixelBuffer: frame.capturedImage
          )
        }
      }
    }

  #elseif os(visionOS)
    func startFrameDelivery(cameraFrameProvider: CameraFrameProvider) {
      guard let format = CameraVideoFormat.supportedVideoFormats(
        for: .main,
        cameraPositions: [.left]
      ).first,
        let arKitFrameUpdates = cameraFrameProvider.cameraFrameUpdates(for: format)
      else {
        Self.logger.warning("No camera format is supported.")
        return
      }

      task = Task {
        for await update in arKitFrameUpdates {
          let frame = update.primarySample

          // Downsample to 5fps.
          guard frame.parameters.captureTimestamp < (frames.last?.timestamp ?? -.infinity) + 0.2
          else { continue }
          
          // Populate intrinsics and process frames.
          intrinsics = intrinsics ?? frame.parameters.intrinsics
          processFrame(
            timestamp: frame.parameters.captureTimestamp,
            extrinsics: frame.parameters.extrinsics,
            cvPixelBuffer: frame.pixelBuffer
          )
        }
      }
    }
  #endif

  func processFrame(timestamp: TimeInterval, extrinsics: float4x4, cvPixelBuffer: CVPixelBuffer) {
    // Convert the video frame to sRGB.
    let image = CIImage(cvPixelBuffer: cvPixelBuffer)
    guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB),
          let jpeg = ciContext.jpegRepresentation(of: image, colorSpace: colorSpace)
    else {
      Self.logger.warning("Cannot convert video frame to RGB image.")
      return
    }

    // Encode to JPEG and save in the temporary directory.
    let imageURL = imageFolder.appending(component: "\(frames.count).jpeg")
    do { try jpeg.write(to: imageURL) }
    catch {
      Self.logger.warning("Cannot write image to \(imageURL). Reason: \(error.localizedDescription)")
      return
    }

    // Publish the frame.
    frames.append(
      CameraFrame(
        timestamp: timestamp,
        extrinsics: extrinsics,
        imageURL: imageURL
      )
    )
  }
}
