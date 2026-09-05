import Foundation

struct SiteDating: Codable {
    let older, younger: Double
    let isPoint: Bool
    let label: String
    let sources: [String]
    func includes(_ age: Double, step: Double) -> Bool {
        isPoint ? abs(age - older) <= step / 2 : younger <= age && age <= older
    }
}

enum PrehistoryScale: String, CaseIterable, Identifiable {
    case early = "远古人类", farming = "定居农业", origins = "文明起源"
    var id: String { rawValue }
    var older: Double { switch self { case .early: 2_120_000; case .farming: 22_000; case .origins: 6_950 } }
    var younger: Double { switch self { case .early: 12_000; case .farming: 6_950; case .origins: 3_750 } }
    var step: Double { switch self { case .early: 10_000; case .farming: 50; case .origins: 50 } }
    var initialAge: Double { switch self { case .early: 1_700_000; case .farming: 10_000; case .origins: 4_950 } }
    var sliderRange: ClosedRange<Double> { -older ... -younger }
    func label(_ age: Double) -> String {
        if self == .origins { return "约公元前\(Int(age - 1950))年" }
        if age >= 10_000 {
            return "距今约\(String(format: "%g", age / 10_000))万年"
        }
        return "距今约\(Int(age))年"
    }
}
