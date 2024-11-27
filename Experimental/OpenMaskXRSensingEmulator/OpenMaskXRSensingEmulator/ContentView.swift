//
//  ContentView.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 12.11.24.
//

import ARKit
import Combine
import RealityKit
import Spatial
import SwiftUI

struct ContentView: View {
  static let logger = Logger.of(ContentView.self)

  @State var marker = Marker(isVisualized: true)
  @State var environmentMesh = EnvironmentMesh(isVisualized: true)
  @State var cameraCapture = CameraCapture()

  @State var isPreparingExport = false
  @State var sensingDataToExport: SensingData?

  var body: some View {
    RealityView { content in
      // Configure RealityKit and ARKit.
      let rkSession = SpatialTrackingSession()
      #if !targetEnvironment(simulator) && os(iOS)
        // On iOS, only one ARSession can exist, so we pass it to RealityKit.

        let rkConfig = SpatialTrackingSession.Configuration(
          tracking: [.world, .image],
          sceneUnderstanding: [.collision]
        )

        let arSession = ARSession()
        guard let arConfig = rkConfig.arConfiguration() as? ARWorldTrackingConfiguration
        else { preconditionFailure("Unsupported AR Configuration.") }
        arConfig.detectionImages = ARReferenceImage.referenceImages(
          inGroupNamed: "AR",
          bundle: .main
        )

        arSession.run(arConfig)
        await rkSession.run(
          rkConfig,
          session: arSession,
          arConfiguration: arConfig
        )

        content.camera = .spatialTracking

        // Capture camera frames.
        cameraCapture.startFrameDelivery(arSession: arSession)
      #elseif os(visionOS)
        // On visionOS, our ARKitSession can exist besides the one RealityKit uses.

        await rkSession.run(.init(tracking: [.world, .image]))

        let arKitSession = ARKitSession()
        let cameraFrameProvider = CameraFrameProvider()

        if (try? await arKitSession.run([cameraFrameProvider])) == nil {
          Self.logger.error("Failed to start ARKitSession with CameraFrameProvider.")
        }

        // Capture camera frames
        cameraCapture.startFrameDelivery(cameraFrameProvider: cameraFrameProvider)
        // TODO: Add reconstruction entities manually.
      #endif

      // Track the marker.
      marker.startTracking(content: content)

      // Collect reconstruction mesh chunks.
      environmentMesh.startReconstruction(realityViewContent: content)
    }
    .frame(maxWidth: .infinity, maxHeight: .infinity)
    .ignoresSafeArea()
    .overlay(alignment: .bottom) {
      Button("Export Sensing Data") {
        isPreparingExport = true
        Task {
          sensingDataToExport = SensingData(
            mesh: await environmentMesh.finalizeReconstruction(),
            intrinsics: cameraCapture.intrinsics ?? .init(0),
            cameraFrames: cameraCapture.frames,
            markerTransform: marker.transform ?? .init(1)
          )
        }
      }
      .buttonStyle(.borderedProminent)
      .buttonBorderShape(.capsule)
      .disabled(isPreparingExport)
    }
    .overlay {
      if isPreparingExport {
        VStack {
          ProgressView("Exporting...")
            .controlSize(.large)
            .font(.title3)
            .foregroundStyle(.primary)
            .tint(.primary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(.thinMaterial)
      }
    }
    .fileExporter(
      isPresented: Binding(
        get: { sensingDataToExport != nil },
        set: {
          sensingDataToExport = $0 ? sensingDataToExport : nil
          isPreparingExport = $0
        }
      ),
      document: sensingDataToExport,
      contentTypes: [.folder],
      defaultFilename: Date.now.formatted(Date.ISO8601FormatStyle(
        dateSeparator: .dash,
        dateTimeSeparator: .space,
        timeSeparator: .omitted,
        timeZone: .current
      ))
    ) {
      switch $0 {
      case let .success(url):
        Self.logger.info("Exported sensing data to URL \(url.absoluteString)")
      case let .failure(error):
        Self.logger
          .error(
            "Failed to export sensing data. Reason: \(error.localizedDescription, privacy: .public)"
          )
      }
    }
  }
}

#Preview {
  ContentView()
}
