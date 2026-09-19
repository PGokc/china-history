import Foundation

/// A heading below the reading edge belongs to the next section, even when it
/// is geometrically closer than the heading of the section still being read.
enum ReadingProgress {
    static func section(positions: [String: CGFloat], order: [String], readingEdge: CGFloat = 32) -> String? {
        order.last { id in positions[id].map { $0 <= readingEdge } ?? false }
    }
}
