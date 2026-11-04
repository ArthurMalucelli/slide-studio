// Tira o fundo da foto de uma pessoa, mesmo em fundo cheio de coisas. Usa o Vision do macOS 14 ou mais novo, sem instalar nada.
// Uso: swift recortar_pessoa.swift entrada.jpg saida.png
// Olhe o resultado ampliado: cabelo, dedos e objetos na mão são onde o recorte erra.
import Foundation
import Vision
import CoreImage
let a = CommandLine.arguments
guard a.count == 3 else { print("Uso: swift recortar_pessoa.swift entrada.jpg saida.png"); exit(2) }
let h = VNImageRequestHandler(url: URL(fileURLWithPath: a[1]))
let r = VNGenerateForegroundInstanceMaskRequest()
try h.perform([r])
guard let o = r.results?.first else { print("Nenhuma pessoa em destaque na foto."); exit(3) }
let b = try o.generateMaskedImage(ofInstances: o.allInstances, from: h, croppedToInstancesExtent: true)
try CIContext().writePNGRepresentation(of: CIImage(cvPixelBuffer: b), to: URL(fileURLWithPath: a[2]), format: .RGBA8, colorSpace: CGColorSpaceCreateDeviceRGB())
print("Recortado: \(a[2]). Confira cabelo e mãos ampliados.")
