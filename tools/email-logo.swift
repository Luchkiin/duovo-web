// Renders the email logotype PNGs from the Figma SVG in source/logos/.
// Run from the site folder: swift tools/email-logo.swift
// Output (assets/email/, copied into the built site by build.py):
//   duovo-logotype@2x.png        black logotype with a 2-px halo in the email background colour (#F4F1EB),
//                                so it stays readable when an email app turns the background dark but leaves images alone.
//   duovo-logotype-white@2x.png  white logotype for clients that honour the template's dark-mode CSS.
// 149 × 41 pt at 2x = 298 × 82 px plus the halo padding.
import AppKit

let site = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let svgURL = site.appendingPathComponent("source/logos/logotype-large-light.svg")
let outDir = site.appendingPathComponent("assets/email")
try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

let svg = try String(contentsOf: svgURL, encoding: .utf8)
let scale: CGFloat = 2
let pad: CGFloat = 2            // px, room for the halo
let pointSize = CGSize(width: 149, height: 41)

func image(colour: String) -> NSImage {
    let data = svg.replacingOccurrences(of: "\"black\"", with: "\"\(colour)\"").data(using: .utf8)!
    guard let image = NSImage(data: data) else { fatalError("SVG could not be loaded") }
    return image
}

func render(_ name: String, ink: String, halo: String?) throws {
    let w = Int(pointSize.width * scale + 2 * pad), h = Int(pointSize.height * scale + 2 * pad)
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8,
                               samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                               colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    rep.size = NSSize(width: w, height: h)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    NSGraphicsContext.current?.imageInterpolation = .high
    let base = NSRect(x: pad, y: pad, width: pointSize.width * scale, height: pointSize.height * scale)
    if let halo {
        let haloImage = image(colour: halo)
        // Stamp the halo colour in a ring of offsets around the shape.
        for step in 0..<24 {
            let a = CGFloat(step) / 24 * 2 * .pi
            for r in [CGFloat(1), pad] {
                haloImage.draw(in: base.offsetBy(dx: cos(a) * r, dy: sin(a) * r))
            }
        }
    }
    image(colour: ink).draw(in: base)
    NSGraphicsContext.restoreGraphicsState()
    let png = rep.representation(using: .png, properties: [:])!
    try png.write(to: outDir.appendingPathComponent(name))
    print(name, w, "x", h, png.count, "bytes")
}

try render("duovo-logotype@2x.png", ink: "#000000", halo: "#F4F1EB")
try render("duovo-logotype-white@2x.png", ink: "#FFFFFF", halo: nil)
