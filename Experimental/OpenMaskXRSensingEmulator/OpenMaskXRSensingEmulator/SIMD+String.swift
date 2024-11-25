//
//  SIMD+String.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 19.11.24.
//

import simd

extension float3x3 {
  var matrixString: String {
    String(
      format: """
      %f %f %f
      %f %f %f
      %f %f %f
      """,
      columns.0.x, columns.1.x, columns.2.x,
      columns.0.y, columns.1.y, columns.2.y,
      columns.0.z, columns.1.z, columns.2.z
    )
  }
}

extension float4x3 {
  var matrixString: String {
    String(
      format: """
      %f %f %f %f
      %f %f %f %f
      %f %f %f %f
      """,
      columns.0.x, columns.1.x, columns.2.x, columns.3.x,
      columns.0.y, columns.1.y, columns.2.y, columns.3.y,
      columns.0.z, columns.1.z, columns.2.z, columns.3.z
    )
  }
}

extension float4x4 {
  init(extending affineTransform3DMatrix: float4x3) {
    self.init(
      SIMD4(affineTransform3DMatrix.columns.0, 0),
      SIMD4(affineTransform3DMatrix.columns.1, 0),
      SIMD4(affineTransform3DMatrix.columns.2, 0),
      SIMD4(affineTransform3DMatrix.columns.3, 1)
    )
  }
  
  init(extending affineTransform2DMatrix: float3x3) {
    self.init(
      SIMD4(affineTransform2DMatrix.columns.0, 0),
      SIMD4(affineTransform2DMatrix.columns.1, 0),
      SIMD4(affineTransform2DMatrix.columns.2, 0),
      SIMD4(SIMD3.zero, 1)
    )
  }

  var matrixString: String {
    String(
      format: """
      %f %f %f %f
      %f %f %f %f
      %f %f %f %f
      %f %f %f %f
      """,
      columns.0.x, columns.1.x, columns.2.x, columns.3.x,
      columns.0.y, columns.1.y, columns.2.y, columns.3.y,
      columns.0.z, columns.1.z, columns.2.z, columns.3.z,
      columns.0.w, columns.1.w, columns.2.w, columns.3.w
    )
  }
}
