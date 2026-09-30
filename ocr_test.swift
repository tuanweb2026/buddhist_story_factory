import Foundation
import PDFKit
import Vision

let pdfURL = URL(fileURLWithPath: "data/pdf/LongYeuThuong_13_21.pdf")
guard let doc = PDFDocument(url: pdfURL) else {
    print("Cannot open PDF")
    exit(1)
}

print("Total pages: \(doc.pageCount)")

for pageIndex in 0..<doc.pageCount {
    guard let page = doc.page(at: pageIndex) else { continue }
    let pageRect = page.bounds(for: .mediaBox)
    let renderer = ImageRenderer(page: page, rect: pageRect)
    if let cgImage = renderer.render() {
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["vi-VN", "en-US"]
        request.usesLanguageCorrection = true

        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        try? handler.perform([request])

        guard let observations = request.results else { continue }
        let text = observations.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
        if !text.isEmpty {
            print("=== PAGE \(pageIndex + 1) ===")
            print(text)
        }
    }
}

class ImageRenderer {
    let page: PDFPage
    let rect: CGRect
    init(page: PDFPage, rect: CGRect) {
        self.page = page
        self.rect = rect
    }
    func render() -> CGImage? {
        let scale: CGFloat = 2.0
        let width = Int(rect.width * scale)
        let height = Int(rect.height * scale)
        let colorSpace = CGColorSpaceCreateDeviceRGB()
        guard let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0, space: colorSpace, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return nil }
        context.scaleBy(x: scale, y: scale)
        context.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
        context.fill(rect)
        page.draw(with: .mediaBox, to: context)
        return context.makeImage()
    }
}
