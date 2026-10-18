import Foundation
import SwiftUI

enum SourceProvenance: String {
    case historicalText = "古籍转录"
    case museum = "文博机构"
    case heritage = "考古与遗产"
    case scholarship = "学术研究"
    case archive = "图像与档案"
    case news = "新闻机构"
    case publicInstitution = "公共机构"
    case reference = "辅助参考"

    static func host(for url: String) -> String {
        guard let host = URL(string: url)?.host?.lowercased() else { return "来源网页" }
        return host.hasPrefix("www.") ? String(host.dropFirst(4)) : host
    }

    static func classify(title originalTitle: String, url: String) -> SourceProvenance {
        let sourceHost = host(for: url)
        let title = originalTitle.lowercased()
        let historicalTextHosts = ["zh.wikisource.org", "ctext.org", "shidianguji.com", "drbachinese.org", "laoziliao.net"]
        if historicalTextHosts.contains(where: { sourceHost == $0 || sourceHost.hasSuffix("." + $0) }) { return .historicalText }

        let museumHosts = [
            "dpm.org.cn", "chnmuseum.cn", "npm.gov.tw", "metmuseum.org", "chinamuseum.org.cn",
            "chnmus.net", "gansumuseum.com", "njmuseum.com", "hnmuseum.com", "beilin-museum.com",
            "bmy.com.cn", "sxhm.com", "kzbwg.cn", "kyuhaku.jp", "npm.edu.tw", "hylae.com"
        ]
        if museumHosts.contains(where: { sourceHost == $0 || sourceHost.hasSuffix("." + $0) }) || title.contains("博物馆") || title.contains("museum") { return .museum }

        let heritageHosts = ["ncha.gov.cn", "whc.unesco.org", "kaogu.cssn.cn", "cach.org.cn", "ihchina.cn", "fhac.com.cn", "qingxiling.com", "shanxiqianling.com"]
        if heritageHosts.contains(where: { sourceHost == $0 || sourceHost.hasSuffix("." + $0) }) || sourceHost.hasPrefix("wwj.") || title.contains("考古") || title.contains("文化遗产") { return .heritage }

        let archiveHosts = ["nlc.cn", "ncl.edu.tw", "loc.gov", "fjlib.net", "commons.wikimedia.org", "saac.gov.cn", "nbdaj.gov.cn", "sdaj.hunan.gov.cn", "library.metro.tokyo.lg.jp", "gpi.culture.tw"]
        if archiveHosts.contains(where: { sourceHost == $0 || sourceHost.hasSuffix("." + $0) }) || sourceHost.contains("archive") || sourceHost.hasPrefix("lib.") || sourceHost.hasPrefix("memory.") { return .archive }

        let scholarshipHosts = ["cssn.cn", "nopss.gov.cn", "cambridge.org", "academic.oup.com", "plato.stanford.edu", "britannica.com", "qinghistory.cn"]
        if scholarshipHosts.contains(where: { sourceHost == $0 || sourceHost.hasSuffix("." + $0) }) || sourceHost.hasSuffix(".edu.cn") || sourceHost.hasSuffix(".ac.cn") || sourceHost.hasSuffix(".cas.cn") || sourceHost.hasSuffix(".sinica.edu.tw") || sourceHost.hasSuffix(".harvard.edu") || sourceHost.hasSuffix(".uchicago.edu") { return .scholarship }

        let newsHosts = ["chinanews.com.cn", "xinhuanet.com", "people.com.cn"]
        if newsHosts.contains(where: { sourceHost == $0 || sourceHost.hasSuffix("." + $0) }) { return .news }
        if sourceHost.hasSuffix(".gov.cn") || sourceHost == "gov.cn" || sourceHost.hasSuffix(".gov.hk") { return .publicInstitution }
        return .reference
    }
}

struct Source: Codable, Identifiable {
    let id, title, url, note: String

    var host: String { SourceProvenance.host(for: url) }
    var provenance: SourceProvenance { SourceProvenance.classify(title: title, url: url) }
}
struct Person: Codable, Identifiable {
    let id, name, call, temple, era, reign, summary, kind, note: String
    let dynasty: String?
    let parent: String?
    let birthOrder: Int?
    let birthOrderNote: String?
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
    /// Editorial placement for period labels; never displayed as an exact date.
    let sortYear: Int?
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
    var collectionCategory: CollectionCategory {
        if symbol == "brain.head.profile" { return .ideas }
        if ["book.closed", "music.note", "doc.text"].contains(symbol) { return .texts }
        if symbol.hasPrefix("building.columns") { return .architecture }
        return .objects
    }
}
struct Succession: Codable, Identifiable {
    let id, person, years, transition: String
    let eraLabel, polity: String?
}
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
    let aliases: [String]?
    let sections: [DynastySection]?
    let evidenceNote: String?
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
    var host: String { SourceProvenance.host(for: url) }
    var provenance: SourceProvenance { SourceProvenance.classify(title: title, url: url) }
}
struct EraTopicSection: Codable, Identifiable {
    let id, title, text: String
}
struct EraTopic: Codable, Identifiable {
    let id, name, call, years, category, summary: String
    let period: String?
    let sections: [EraTopicSection]
    let sources: [EraTopicSource]
}
struct EraGuide: Codable {
    let title, subtitle, overview: String
    let topics: [EraTopic]
}
struct ReignPeriod: Codable { let label: String; let start, end: Int }
struct ReignContext: Codable {
    let person: String
    let periods: [ReignPeriod]
    let people, events, sources: [String]
    let note: String
    var periodLabel: String { periods.map(\.label).joined(separator: "；") }
}
struct Content: Codable {
    let version: Int
    let reignContexts: [ReignContext]?
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
        let parentIds = Set(parents(p.id).filter { ["father", "mother"].contains($0.kind) }.map(\.to))
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
        guard let n = p.birthOrder else { return p.birthOrderNote ?? "子女" }
        return n == 1 ? "长子" : "第\(n)子"
    }
    func childLabel(_ child: Person, of parentID: String) -> String {
        let kinds = Set(links.filter { $0.from == child.id && $0.to == parentID }.map(\.kind))
        if kinds.contains("father") || kinds.contains("mother") { return orderLabel(child) }
        if kinds.contains("adoptiveFather") || kinds.contains("adoptiveMother") { return "嗣子" }
        return "礼制承继"
    }
    func hasNonBiologicalChildren(_ id: String) -> Bool {
        links.contains { $0.to == id && ["adoptiveFather", "adoptiveMother", "ritual"].contains($0.kind) }
    }
    func childrenHeading(_ id: String) -> String { hasNonBiologicalChildren(id) ? "子女与承继" : "子女" }
    func associates(_ id: String) -> [Association] { (content.associations ?? []).filter { $0.from == id || $0.to == id } }
    func events(_ id: String) -> [HistoryEvent] {
        content.events.filter { $0.people.contains(id) }.sorted {
            EventChronology.precedes($0.year, placement: $0.sortYear, id: $0.id,
                                     $1.year, placement: $1.sortYear, id: $1.id)
        }
    }
    func reignContext(_ id: String) -> ReignContext? { content.reignContexts?.first { $0.person == id } }
    func reignEvents(_ id: String) -> [HistoryEvent] {
        guard let context = reignContext(id) else { return events(id) }
        let ids = Set(context.events)
        return events(id).filter { ids.contains($0.id) }
    }
    func eventCategory(_ event: HistoryEvent) -> MajorEventCategory {
        MajorEventCategory(rawValue: event.category ?? "") ?? .politics
    }
    func events(_ id: String, in category: MajorEventCategory, inReignOnly: Bool = true) -> [HistoryEvent] {
        let featured: [String: Int] = [
            "v12_zhenghe_voyages": 0,
            "v40m1_voyages_yongle": 0,
            "v12_yongle_dadian": 1,
            "v17_yongle_mobei": 0
        ]
        return (inReignOnly ? reignEvents(id) : events(id)).filter { eventCategory($0) == category }.sorted { lhs, rhs in
            let left = featured[lhs.id] ?? 100
            let right = featured[rhs.id] ?? 100
            if left != right { return left < right }
            return EventChronology.precedes(lhs.year, placement: lhs.sortYear, id: lhs.id,
                                            rhs.year, placement: rhs.sortYear, id: rhs.id)
        }
    }
    /// Opens a person's event shelf on its most useful category. The fixed
    /// category order resolves ties so the result stays stable as content grows.
    func preferredEventCategory(_ id: String, inReignOnly: Bool = true) -> MajorEventCategory {
        MajorEventCategory.allCases.max { lhs, rhs in
            events(id, in: lhs, inReignOnly: inReignOnly).count < events(id, in: rhs, inReignOnly: inReignOnly).count
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
    func dynastyID(for personID: String) -> String {
        if let id = content.people.first(where: { $0.id == personID })?.dynasty { return id }
        assertionFailure("Person \(personID) has no explicit dynasty")
        return "ming"
    }
    func dynastyName(_ id: String) -> String {
        if id == "song_liao_xia_jin" { return "宋辽夏金" }
        if id == "three_kingdoms" { return "三国" }
        if id == "jin" { return "两晋" }
        if id == "northern_southern" { return "南北朝" }
        if id == "five_dynasties" { return "五代十国" }
        return (dynasty(id)?.name ?? "") + "朝"
    }
    func sequenceIntroduction(_ id: String) -> String {
        switch id {
        case "xia": return "这里按《史记·夏本纪》等传世文献呈现十七王次序。约前2070—前1600是夏代整体断代框架，不能平均拆成个人王年；目前也没有可像晚商甲骨文那样逐王校验的同时代文字，因此每一行都明确标作传统王序。"
        case "shang": return "这里按传世文献并经甲骨文校核的三十王次序排列商王。商王使用日名系统，当时并无后世皇帝、庙号和年号制度；早商与中商的精确在位年缺少可靠共识，因此不强行配置公历起止。"
        case "zhou": return "这里把西周十二王与东周二十五王分组呈现。共和行政是厉王出奔后的执政阶段，并非一位周王；前841年以前的绝对王年采用常用断代方案并明确标示，前841年以后使用连续纪年。"
        case "qin": return "前221年，秦王政采用“皇帝”称号。这里列出秦帝国使用皇帝称号的始皇帝与二世；子婴即位后降称秦王，另见人物与秦亡事件。"
        case "han": return "这里列出实际即位的西汉与东汉皇帝。西汉前、后少帝保留称号并标明名讳争议；孺子婴未称帝，王莽所建新朝及新莽末年诸政权另见人物与事件。"
        case "three_kingdoms": return "曹魏、蜀汉、孙吴在时间上并行，各有自己的继承次序。这里按政权分组列出实际称帝者；曹操、孙坚等追尊君主，以及孙策等未称帝的奠基人物另见人物与事件。"
        case "jin": return "这里把西晋与东晋分组呈现。317年以后，东晋只控制南方部分地区；北方十六国与其长期并行，相关统治者、战争、迁徙与制度另见人物和事件。"
        case "northern_southern": return "南朝宋、齐、梁、陈与北方诸政权在时间上并行。这里按九条政权序列列出实际即位者；同年废立、短期并立和权臣控制均保留，不拼成一条虚假的全国帝序。"
        case "five_dynasties": return "907至979年间，中原五代与十个主要区域政权交错并立。这里把后梁至后周列为一条中原序列，再分别呈现吴、南唐、荆南、闽、楚、前蜀、后蜀、吴越、南汉与北汉；称帝、称王和藩镇名义均按当时材料区分。"
        case "sui": return "隋末并非一条整齐交接的帝序。杨侑在长安、杨浩在江都、杨侗在洛阳先后或同时被拥立；这里全部列出，并分别说明实际控制者、年号与统治范围。"
        case "tang": return "李唐皇位经历复位、武周改国与多次宫廷政变。武则天统治的武周单列，中宗与睿宗两次在位分别呈现。"
        case "song_liao_xia_jin": return "北宋、南宋与辽、西夏、金在很长时段内并立。这里按五条政权序列呈现实际即位者；条约、战争、互市、迁都与摄政另在人物和事件中展开，不把其他王朝降为宋史背景。"
        case "yuan": return "1271年忽必烈建国号元，此前已于1260年即蒙古大汗位。两都之战出现争位，文宗两次在位分列；1368年退出大都以后的北元另在生平中说明。"
        case "qing": return "从后金兴起到帝制终结，皇位传承始终与宗室、摄政和时代转折相连。努尔哈赤与皇太极属于入关前的两代统治者。"
        default: return "从洪武开国到崇祯亡国，明代皇位大体沿朱元璋一系传承，也经历靖难、土木堡之变与复辟等重要转折。朱祁镇两度在位，在序列中分段呈现。"
        }
    }
    func people(in dynastyID: String) -> [Person] { content.people.filter { self.dynastyID(for: $0.id) == dynastyID } }
    func sequence(in dynastyID: String) -> [Succession] { content.sequence.filter { self.dynastyID(for: $0.person) == dynastyID } }
    func objects(in dynastyID: String) -> [Artifact] {
        content.objects.filter { object in
            if let dynasties = object.dynasties { return dynasties.contains(dynastyID) }
            return object.people.contains { self.dynastyID(for: $0) == dynastyID }
        }
    }
    func tombs(in dynastyID: String) -> [Tomb] { (content.tombs ?? []).filter { self.dynastyID(for: $0.person) == dynastyID } }
    func defaultPerson(in dynastyID: String) -> String { sequence(in: dynastyID).first?.person ?? "yuanzhang" }
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
    /// Visible breathing room between the final content row and the floating tab bar.
    static let pageBottom: CGFloat = 44
    /// Use after `.padding(24)` so the combined bottom inset remains `pageBottom`.
    static let pageBottomAfterStandardPadding: CGFloat = 20
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
