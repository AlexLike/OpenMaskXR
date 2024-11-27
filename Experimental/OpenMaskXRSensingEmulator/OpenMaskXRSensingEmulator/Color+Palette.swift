//
//  Color+Palette.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 17.11.24.
//

import RealityKit

extension Material.Color {
  static func debug(i: Int) -> Material.Color {
    let palette = [
      Material.Color(red: 165 / 255, green: 0 / 255, blue: 38 / 255, alpha: 1),
      Material.Color(red: 215 / 255, green: 48 / 255, blue: 39 / 255, alpha: 1),
      Material.Color(red: 244 / 255, green: 109 / 255, blue: 67 / 255, alpha: 1),
      Material.Color(red: 253 / 255, green: 174 / 255, blue: 97 / 255, alpha: 1),
      Material.Color(red: 254 / 255, green: 224 / 255, blue: 144 / 255, alpha: 1),
      Material.Color(red: 255 / 255, green: 255 / 255, blue: 191 / 255, alpha: 1),
      Material.Color(red: 224 / 255, green: 243 / 255, blue: 248 / 255, alpha: 1),
      Material.Color(red: 171 / 255, green: 217 / 255, blue: 233 / 255, alpha: 1),
      Material.Color(red: 116 / 255, green: 173 / 255, blue: 209 / 255, alpha: 1),
      Material.Color(red: 69 / 255, green: 117 / 255, blue: 180 / 255, alpha: 1),
      Material.Color(red: 49 / 255, green: 54 / 255, blue: 149 / 255, alpha: 1),
    ]
    return palette[i % palette.count]
  }
}
