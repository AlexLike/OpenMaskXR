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

  @State var marker = Marker()
  @State var environmentMesh = EnvironmentMesh()

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
        guard let arConfig = rkConfig.arConfiguration()
        else { preconditionFailure("Unsupported ARKit Configuration.") }

        let arSession = ARSession()
        arSession.run(arConfig)

        await rkSession.run(
          rkConfig,
          session: arSession,
          arConfiguration: arConfig
        )
        content.camera = .spatialTracking
      
        // TODO: Setup camera frame, extrinsics, and intrinsics grabbing.

      #elseif os(visionOS)
        // On visionOS, our ARKitSession can exist besides the one RealityKit uses.
        await rkSession.run(.init(tracking: [.world, .image]))

        // TODO: Add reconstruction entities manually.
        // TODO: Setup camera frame, extrinsics, and intrinsics grabbing.
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
          let mesh = await environmentMesh.finalizeReconstruction()
          // TODO: Populate intrinsics and markerTransform.
          sensingDataToExport = SensingData(
            mesh: mesh,
            intrinsics: .init(),
            markerTransform: .init()
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
