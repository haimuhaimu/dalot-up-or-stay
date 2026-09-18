import AppKit
import Foundation
import Vision

guard CommandLine.arguments.count == 2 else {
    fputs("usage: swift detect_faces.swift IMAGE\n", stderr)
    exit(2)
}

let imagePath = CommandLine.arguments[1]
guard
    let image = NSImage(contentsOfFile: imagePath),
    let tiff = image.tiffRepresentation,
    let bitmap = NSBitmapImageRep(data: tiff),
    let cgImage = bitmap.cgImage
else {
    fputs("unable to open image: \(imagePath)\n", stderr)
    exit(3)
}

let width = CGFloat(cgImage.width)
let height = CGFloat(cgImage.height)
let request = VNDetectFaceRectanglesRequest()
let handler = VNImageRequestHandler(cgImage: cgImage, orientation: .up, options: [:])

do {
    try handler.perform([request])
} catch {
    fputs("face detection failed: \(error)\n", stderr)
    exit(4)
}

let observations = (request.results ?? []).sorted {
    let ay = (1.0 - $0.boundingBox.origin.y - $0.boundingBox.height) * height
    let by = (1.0 - $1.boundingBox.origin.y - $1.boundingBox.height) * height
    if abs(ay - by) > 25 { return ay < by }
    return $0.boundingBox.origin.x < $1.boundingBox.origin.x
}

for (index, face) in observations.enumerated() {
    let box = face.boundingBox
    let x = box.origin.x * width
    let y = (1.0 - box.origin.y - box.height) * height
    let w = box.width * width
    let h = box.height * height
    print("\(index),\(String(format: "%.2f", x)),\(String(format: "%.2f", y)),\(String(format: "%.2f", w)),\(String(format: "%.2f", h)),\(String(format: "%.4f", face.confidence))")
}
