import Foundation
import SwiftUI

struct Source: Codable, Identifiable { let id, title, url, note: String }
struct Person: Codable, Identifiable {
    let id, name, call, temple, era, reign, summary, kind, note: String
    let parent: String?
    let birthOrder: Int?
    let sources: [String]
    var image: String?
}
struct Relation: Codable { let a, b, label, reverse: String; let sources: [String] }
struct FamilyLink: Codable, Identifiable {
    let from, to, kind: String
    let sources: [String]
    let note: String
    var id: String { from + "_" + kind + "_" + to }
}
struct Association: Codable, Identifiable {
    let from, to, role, inverse, period, note: String
    let sources: [String]
    var id: String { from + "_" + to + "_" + period }
}
struct HistoryEvent: Codable, Identifiable {
    let id, year, title, body, impact, kind: String
    let category: String?
    let people, sources: [String]
    let peopleRoles: [String: String]?
}
enum MajorEventCategory: String, CaseIterable, Hashable, Identifiable {
    case politics = "政治"
    case military = "军事"
    case culture = "文化"
    case economy = "经济"
    case society = "社会"
    var id: String { rawValue }
    var symbol: String {
        switch self {
        case .politics: return "building.columns"
        case .military: return "shield"
        case .culture: return "scroll"
        case .economy: return "chart.line.uptrend.xyaxis"
        case .society: return "person.3"
        }
    }
}
struct Artifact: Codable, Identifiable {
    let id, title, subtitle, symbol, body, note: String
    let image: String?
    let people, sources: [String]
    let dynasties: [String]?
}
struct Succession: Codable, Identifiable { let id, person, years, transition: String }
struct Tomb: Codable, Identifiable { let id, person, title, area, location, status, body, note: String; let sources: [String] }
struct ArticleSection: Codable, Identifiable {
    let id, title, text, kind: String
    let sources: [String]
    let people, events: [String]?
}
struct Article: Codable, Identifiable {
    let person, title, dek: String
    let sections: [ArticleSection]
    let sources: [String]
    var id: String { person }
    var characterCount: Int { sections.reduce(0) { $0 + $1.text.count } }
}
struct Portrait: Codable, Identifiable {
    let person: String
    let image: String?
    let title, attribution, date, collection, description, sourceURL, imageURL, status, searchNote: String
    let sourceIds: [String]
    let displayLabel: String?
    var id: String { person }
}
struct Dynasty: Codable, Identifiable {
    let id, name, years, note: String
    let selectable: Bool
    let sources: [String]
}
struct DynastySection: Codable, Identifiable {
    let id, title, text: String
}
struct DynastyProfile: Codable, Identifiable {
    let id, subtitle, overview: String
    let sections: [DynastySection]
    let sources: [String]
}
struct PrehistorySite: Codable, Identifiable {
    let dating: SiteDating
    let id, name, period, location, province, summary, discovery, significance: String
    let latitude, longitude: Double
    let sources: [String]
}
struct GeoPoint: Codable { let latitude, longitude: Double }
struct TerritoryRegion: Codable, Identifiable {
    let id, name, tone: String
    let labelLatitude, labelLongitude: Double
    let points: [GeoPoint]
}
struct TerritoryMap: Codable, Identifiable {
    let id, date, caption: String
    let centerLatitude, centerLongitude, latitudeDelta, longitudeDelta: Double
    let regions: [TerritoryRegion]
    let sources: [String]
}
struct EraTopicSource: Codable, Identifiable {
    let title, url: String
    var id: String { url }
}
struct EraTopicSection: Codable, Identifiable {
    let id, title, text: String
}
struct EraTopic: Codable, Identifiable {
    let id, name, call, years, category, summary: String
    let sections: [EraTopicSection]
    let sources: [EraTopicSource]
}
struct EraGuide: Codable {
    let title, subtitle, overview: String
    let topics: [EraTopic]
}
struct Content: Codable {
    let version: Int
    let reviewed: String
    let people: [Person]
    let sources: [Source]
    let relations: [Relation]
    let events: [HistoryEvent]
    let objects: [Artifact]
    let sequence: [Succession]
    let tombs: [Tomb]?
    let familyLinks: [FamilyLink]?
    let articles: [Article]?
    let portraits: [Portrait]?
    let associations: [Association]?
    let dynasties: [Dynasty]?
    let dynastyProfiles: [DynastyProfile]?
    let prehistorySites: [PrehistorySite]?
    let territoryMaps: [TerritoryMap]?
}
@Observable final class HistoryStore {
    let content: Content
    let zhouGuide: EraGuide?
    init() throws {
        guard let url = Bundle.main.url(forResource: "history", withExtension: "json") else { throw CocoaError(.fileNoSuchFile) }
        content = try JSONDecoder().decode(Content.self, from: Data(contentsOf: url))
        if let guideURL = Bundle.main.url(forResource: "zhou_topics", withExtension: "json") {
            zhouGuide = try JSONDecoder().decode(EraGuide.self, from: Data(contentsOf: guideURL))
        } else {
            zhouGuide = nil
        }
    }
    func person(_ id: String) -> Person { content.people.first { $0.id == id } ?? content.people[0] }
    var links: [FamilyLink] { content.familyLinks ?? [] }
    func parents(_ id: String) -> [FamilyLink] { links.filter { $0.from == id && ["father", "mother", "adoptiveFather", "adoptiveMother", "ritual"].contains($0.kind) }.sorted { $0.kind < $1.kind } }
    func children(_ id: String) -> [Person] {
        let ids = Set(links.filter { $0.to == id && ["father", "mother", "adoptiveFather", "adoptiveMother", "ritual"].contains($0.kind) }.map(\.from))
        return content.people.filter { ids.contains($0.id) }.sorted { ($0.birthOrder ?? 99) < ($1.birthOrder ?? 99) }
    }
    func spouses(_ id: String) -> [Person] { links.filter { $0.kind == "spouse" && ($0.from == id || $0.to == id) }.map { person($0.from == id ? $0.to : $0.from) } }
    func siblings(_ p: Person) -> [Person] {
        let parentIds = Set(parents(p.id).map(\.to))
        let ids = Set(links.filter { ["father", "mother"].contains($0.kind) && parentIds.contains($0.to) }.map(\.from))
        return content.people.filter { ids.contains($0.id) && $0.id != p.id }.sorted { ($0.birthOrder ?? 99) < ($1.birthOrder ?? 99) }
    }
    func siblingLabel(_ p: Person, relativeTo current: Person) -> String {
        if let a = p.birthOrder, let b = current.birthOrder { return a < b ? "兄" : "弟" }
        return "同辈"
    }
    func parentLabel(_ kind: String) -> String {
        switch kind {
        case "father": return "父亲"
        case "mother": return "母亲"
        case "adoptiveFather": return "嗣父"
        case "adoptiveMother": return "嗣母"
        default: return "礼制承继"
        }
    }
    func orderLabel(_ p: Person) -> String {
        guard let n = p.birthOrder else { return "子女" }
        return n == 1 ? "长子" : "第\(n)子"
    }
    func associates(_ id: String) -> [Association] { (content.associations ?? []).filter { $0.from == id || $0.to == id } }
    func events(_ id: String) -> [HistoryEvent] {
        content.events.filter { $0.people.contains(id) }.sorted {
            let a = Int($0.year.prefix(while: { $0.isNumber })) ?? 0
            let b = Int($1.year.prefix(while: { $0.isNumber })) ?? 0
            return a < b
        }
    }
    func eventCategory(_ event: HistoryEvent) -> MajorEventCategory {
        MajorEventCategory(rawValue: event.category ?? "") ?? .politics
    }
    func events(_ id: String, in category: MajorEventCategory) -> [HistoryEvent] {
        let featured: [String: Int] = [
            "v12_zhenghe_voyages": 0,
            "v12_yongle_dadian": 1,
            "v17_yongle_mobei": 0
        ]
        return events(id).filter { eventCategory($0) == category }.sorted { lhs, rhs in
            let left = featured[lhs.id] ?? 100
            let right = featured[rhs.id] ?? 100
            if left != right { return left < right }
            let leftYear = Int(lhs.year.prefix(while: { $0.isNumber })) ?? 0
            let rightYear = Int(rhs.year.prefix(while: { $0.isNumber })) ?? 0
            return leftYear < rightYear
        }
    }
    /// Opens a person's event shelf on its most useful category. The fixed
    /// category order resolves ties so the result stays stable as content grows.
    func preferredEventCategory(_ id: String) -> MajorEventCategory {
        MajorEventCategory.allCases.max { lhs, rhs in
            events(id, in: lhs).count < events(id, in: rhs).count
        } ?? .politics
    }
    func featuredEvents(_ id: String) -> [HistoryEvent] {
        if id == "yuanzhang" {
            return ["join", "poyang", "founding"].compactMap { key in content.events.first { $0.id == key } }
        }
        return Array(events(id).prefix(3))
    }
    func objects(_ id: String) -> [Artifact] { content.objects.filter { $0.people.contains(id) } }
    func tomb(_ id: String) -> Tomb? { content.tombs?.first { $0.person == id } }
    func article(_ id: String) -> Article? { content.articles?.first { $0.person == id } }
    func hasFamily(_ id: String) -> Bool { links.contains { $0.from == id || $0.to == id } }
    func portrait(_ id: String) -> Portrait? { content.portraits?.first { $0.person == id } }
    func image(_ id: String) -> String? {
        if let portrait = portrait(id) { return portrait.image }
        return person(id).image
    }
    func dynastyID(for personID: String) -> String { personID.hasPrefix("q_") ? "qing" : "ming" }
    func people(in dynastyID: String) -> [Person] { content.people.filter { self.dynastyID(for: $0.id) == dynastyID } }
    func sequence(in dynastyID: String) -> [Succession] { content.sequence.filter { self.dynastyID(for: $0.person) == dynastyID } }
    func objects(in dynastyID: String) -> [Artifact] {
        content.objects.filter { object in
            if let dynasties = object.dynasties { return dynasties.contains(dynastyID) }
            return object.people.contains { self.dynastyID(for: $0) == dynastyID }
        }
    }
    func tombs(in dynastyID: String) -> [Tomb] { (content.tombs ?? []).filter { self.dynastyID(for: $0.person) == dynastyID } }
    func defaultPerson(in dynastyID: String) -> String { dynastyID == "qing" ? "q_nurhaci" : "yuanzhang" }
    func validPerson(_ personID: String, in dynastyID: String) -> Bool {
        content.people.contains { $0.id == personID && self.dynastyID(for: $0.id) == dynastyID }
    }
    func dynasty(_ id: String) -> Dynasty? { content.dynasties?.first { $0.id == id } }
    func dynastyProfile(_ id: String) -> DynastyProfile? { content.dynastyProfiles?.first { $0.id == id } }
    func prehistorySite(_ id: String) -> PrehistorySite? { content.prehistorySites?.first { $0.id == id } }
    func territoryMap(_ id: String) -> TerritoryMap? { content.territoryMaps?.first { $0.id == id } }
    func eraTopic(_ id: String) -> EraTopic? { zhouGuide?.topics.first { $0.id == id } }
}
enum Theme {
    static let paper = Color(red: 245/255, green: 242/255, blue: 236/255)
    static let ink = Color(red: 24/255, green: 52/255, blue: 74/255)
    static let text = Color(red: 34/255, green: 39/255, blue: 43/255)
    static let cinnabar = Color(red: 122/255, green: 47/255, blue: 53/255)
    static let muted = Color(red: 103/255, green: 104/255, blue: 100/255)
    static let line = Color(red: 194/255, green: 194/255, blue: 184/255)
}
extension View {
    func paperCard() -> some View { padding(18).background(.white.opacity(0.48), in: RoundedRectangle(cornerRadius: 6)) }
}
struct LocalImage: View {
    let name: String?
    var compact = false
    var body: some View {
        if let name, let url = (Bundle.main.url(forResource: name, withExtension: "jpg") ?? Bundle.main.url(forResource: name, withExtension: "png")), let image = UIImage(contentsOfFile: url.path) {
            Image(uiImage: image).resizable().scaledToFit()
        } else {
            ZStack {
                Theme.paper
                VStack(spacing: 10) {
                    Image(systemName: "person.crop.square").font(.system(size: compact ? 24 : 35, weight: .ultraLight))
                    if !compact { Text("画像待考").font(.caption).tracking(2) }
                }.foregroundStyle(Theme.muted)
            }.accessibilityLabel("尚未选定可靠历史画像")
        }
    }
}

/// Quiet feedback for full-width navigation rows; respects Reduce Motion.
struct QuietRowStyle: ButtonStyle {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .opacity(configuration.isPressed ? 0.64 : 1)
            .animation(reduceMotion ? nil : .easeOut(duration: 0.16), value: configuration.isPressed)
    }
}
