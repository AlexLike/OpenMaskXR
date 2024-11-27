//
//  CIImage+YCbCrA.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 25.11.24.
//

import CoreImage
import CoreImage.CIFilterBuiltins

extension CIImage {
  var rgbFromYCbCrA: CIImage? {
    let filter = CIFilter.colorMatrix()
    filter.rVector = CIVector(x: 1, y: 0, z: 1.4020, w: -0.7010)
    filter.gVector = CIVector(x: 1, y: -0.3441, z: -0.7141, w: 0.5291)
    filter.bVector = CIVector(x: 1, y: 1.7720, z: 0, w: 0.8860)
    filter.aVector = CIVector(x: 0, y: 0, z: 0, w: 1)
    filter.inputImage = self
    return filter.outputImage
  }
}
