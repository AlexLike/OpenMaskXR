//
//  Logger.swift
//  OpenMaskXRSensingEmulator
//
//  Created by Alexander Zank on 17.11.24.
//

import OSLog

enum Logger {
  static func of<T>(_ type: T.Type) -> os.Logger {
    return os.Logger(subsystem: Bundle.main.bundleIdentifier!, category: String(describing: type))
  }
}
