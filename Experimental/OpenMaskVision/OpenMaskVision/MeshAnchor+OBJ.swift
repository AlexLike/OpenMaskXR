//
//  MeshAnchor+OBJ.swift
//  OpenMaskVision
//
//  Created by Alexander Zank on 30.09.24.
//

import ARKit

extension MeshAnchor.Geometry {
  /// The [Wavefront OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file) representation of this mesh anchor's geometry.
  var objRepresentation: String {
    var objString = ""
    
    // TODO: This still has some bug! (But in principle should be accurate...)

    // Write vertices "v <x> <y> <z>"
    precondition(vertices.format == .float3)
    for i in stride(
      from: vertices.offset,
      to: vertices.offset + vertices.count * vertices.stride,
      by: vertices.stride
    ) {
      let vertex = vertices.buffer.contents().advanced(by: i)
        .assumingMemoryBound(to: SIMD3<Float>.self).pointee
      objString += "v \(vertex.x) \(vertex.y) \(vertex.z)\n"
    }

    // Write normals "vn <x> <y> <z>"
    precondition(normals.format == .float3)
    for i in stride(
      from: normals.offset,
      to: normals.offset + normals.count * normals.stride,
      by: normals.stride
    ) {
      let normal = normals.buffer.contents().advanced(by: i)
        .assumingMemoryBound(to: SIMD3<Float>.self).pointee
      objString += "vn \(normal.x) \(normal.y) \(normal.z)\n"
    }

    // Write faces "f <v1>//<vn1> <v2>//<vn2> <v3>//<vn3>"
    precondition(faces.primitive == .triangle)
    for i in 0..<faces.count {
      let faceBase = faces.buffer.contents().advanced(by: i * 3 * faces.bytesPerIndex)
      let face = (0..<3).map { offset in
        faceBase.advanced(by: offset * faces.bytesPerIndex).assumingMemoryBound(to: UInt32.self)
          .pointee
      }
      objString += "f \(face[0])//\(face[0]) \(face[1])//\(face[1]) \(face[2])//\(face[2])\n"
    }

    return objString
  }
}
