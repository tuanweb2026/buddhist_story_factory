import Foundation
import PDFKit
import Vision

guard CommandLine.arguments.count > 1 else {
    print("Usage: swift macos_pdf_ocr.swift <path_to_pdf>")
    exit(1)
}

let pdfPath = CommandLine.arguments[1]
let pdfURL = URL(fileURLWithPath: pdfPath)
guard let doc = PDFDocument(url: pdfURL) else {
    print("")
    exit(0)
}

var allParagraphs: [String] = []

for pageIndex in 0..<doc.pageCount {
    guard let page = doc.page(at: pageIndex) else { continue }
    let pageRect = page.bounds(for: .mediaBox)
    let scale: CGFloat = 2.0
    let width = Int(pageRect.width * scale)
    let height = Int(pageRect.height * scale)
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    guard let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0, space: colorSpace, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { continue }
    context.scaleBy(x: scale, y: scale)
    context.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    context.fill(pageRect)
    page.draw(with: .mediaBox, to: context)
    
    guard let cgImage = context.makeImage() else { continue }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["vi-VN", "en-US"]
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try? handler.perform([request])

    if let observations = request.results {
        let lines = observations.compactMap { $0.topCandidates(1).first?.string }
        let text = lines.joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines)
        if text.count > 15 {
            allParagraphs.append(text)
        }
    }
}

print(allParagraphs.joined(separator: "\n\n"))
