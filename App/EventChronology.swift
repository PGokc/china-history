import Foundation

/// Display dates retain their original precision. A broad period may have an
/// editorial placement year, which is an ordering aid rather than an event date.
enum EventChronology {
    static func year(_ label: String, placement: Int? = nil) -> Int? {
        if let placement { return placement }
        let digits = label.prefix(while: { $0.isNumber })
        guard (3...4).contains(digits.count), !label.dropFirst(digits.count).hasPrefix("世纪") else { return nil }
        return Int(digits)
    }

    static func precedes(_ lhs: String, placement left: Int?, id leftID: String,
                         _ rhs: String, placement right: Int?, id rightID: String) -> Bool {
        let a = year(lhs, placement: left) ?? Int.max
        let b = year(rhs, placement: right) ?? Int.max
        return a == b ? leftID < rightID : a < b
    }
}
