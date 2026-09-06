import SwiftUI

/// A bounded overview. Growing collections live one level below this page.
struct PersonPage: View {
    let store: HistoryStore
    let personID: String
    @Environment(\.dynamicTypeSize) private var typeSize
    @State private var selectedEventCategory: MajorEventCategory
    init(store: HistoryStore, personID: String) {
        self.store = store
        self.personID = personID
        _selectedEventCategory = State(initialValue: store.preferredEventCategory(personID))
    }
    var p: Person { store.person(personID) }
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 30) {
                HStack(alignment: .top, spacing: 18) {
                    if store.portrait(p.id) != nil || store.image(p.id) != nil {
                        NavigationLink(value: DetailRoute.portrait(p.id)) {
                            VStack(spacing: 7) {
                                LocalImage(name: store.image(p.id), compact: true).frame(width: 74, height: 100)
                                if let label = store.portrait(p.id)?.displayLabel { Text(label).font(.caption2).foregroundStyle(Theme.muted) }
                            }
                        }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("portraitEntry")
                    }
                    VStack(alignment: .leading, spacing: 8) {
                        Text(p.kind).font(.caption.weight(.medium)).foregroundStyle(Theme.cinnabar)
                        Text(p.name).font(.system(.largeTitle, design: .serif)).foregroundStyle(Theme.ink)
                        Text(p.call).font(.subheadline).foregroundStyle(Theme.muted)
                        if p.kind == "皇帝" { Text("在位 \(p.reign)").font(.caption).monospacedDigit() }
                    }.frame(maxWidth: .infinity, alignment: .leading)
                }
                if !typeSize.isAccessibilitySize { Text(p.summary).font(.body).lineSpacing(7).fixedSize(horizontal: false, vertical: true) }
                if let article = store.article(p.id) {
                    NavigationLink(value: DetailRoute.article(p.id)) {
                        HStack(alignment: .center, spacing: 14) {
                            VStack(alignment: .leading, spacing: 5) {
                                Text("生平长读").font(.headline).foregroundStyle(Theme.ink)
                                if !typeSize.isAccessibilitySize { Text(article.title).font(.caption).foregroundStyle(Theme.muted).lineLimit(2) }
                            }
                            Spacer(minLength: 8)
                        }.padding(.vertical, 17).frame(maxWidth: .infinity, alignment: .leading).contentShape(Rectangle())
                            .overlay(alignment: .top) { Rectangle().fill(Theme.line.opacity(0.8)).frame(height: 0.5) }
                            .overlay(alignment: .bottom) { Rectangle().fill(Theme.line.opacity(0.8)).frame(height: 0.5) }
                    }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("articleEntry")
                }
                PersonQuickLinks(items: quickLinks)
                if p.kind == "皇帝" && !store.events(p.id).isEmpty {
                    MajorEventsPanel(store: store, personID: p.id, selection: $selectedEventCategory, previewLimit: 2)
                }
                if typeSize.isAccessibilitySize {
                    DisclosureGroup("人物简介") { Text(p.summary).font(.body).lineSpacing(5).padding(.top, 10) }
                }
            }.padding(24)
        }.background(Theme.paper).foregroundStyle(Theme.text)
            .navigationTitle("人物概览").navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
    }
    var relationSummary: String {
        var parts: [String] = []
        if let father = store.parents(p.id).first(where: { $0.kind == "father" }) { parts.append("父亲\(store.person(father.to).name)") }
        if !store.children(p.id).isEmpty { parts.append("\(store.children(p.id).count)位子女") }
        if parts.isEmpty { return store.hasFamily(p.id) ? "家族亲属与往来人物" : "往来人物与关系变迁" }
        return parts.joined(separator: "，")
    }
    var heritageSummary: String {
        ([store.tomb(p.id)?.title].compactMap { $0 } + store.objects(p.id).map(\.title)).joined(separator: "、")
    }
    var quickLinks: [PersonQuickItem] {
        var items: [PersonQuickItem] = []
        if store.hasFamily(p.id) || !store.associates(p.id).isEmpty { items.append(.init(id: "category_relationships", title: "人物关系", subtitle: relationSummary, route: .personSection(p.id, .relationships))) }
        if p.kind != "皇帝" && !store.events(p.id).isEmpty { items.append(.init(id: "category_events", title: "重大事件", subtitle: "\(store.events(p.id).count)项相关事件", route: .personEvents(p.id, store.preferredEventCategory(p.id)))) }
        if store.tomb(p.id) != nil || !store.objects(p.id).isEmpty { items.append(.init(id: "category_remains", title: "遗珍与陵寝", subtitle: heritageSummary, route: .personSection(p.id, .remains))) }
        items.append(.init(id: "category_records", title: "称号与资料", subtitle: p.kind == "皇帝" ? "庙号、年号与史料依据" : "生平称号与史料依据", route: .personSection(p.id, .records)))
        return items
    }
}

struct PersonQuickItem: Identifiable {
    let id, title, subtitle: String
    let route: DetailRoute
}

struct PersonQuickLinks: View {
    @Environment(\.dynamicTypeSize) private var typeSize
    let items: [PersonQuickItem]
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("继续了解").font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink).padding(.bottom, 8)
            ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
                NavigationLink(value: item.route) {
                    VStack(alignment: .leading, spacing: 5) {
                        Text(item.title).font(.headline).foregroundStyle(Theme.ink)
                        if !item.subtitle.isEmpty { Text(item.subtitle).font(.caption).foregroundStyle(Theme.muted).lineLimit(typeSize.isAccessibilitySize ? nil : 2) }
                    }.frame(maxWidth: .infinity, minHeight: 54, alignment: .leading).padding(.vertical, 12).contentShape(Rectangle())
                }.buttonStyle(QuietRowStyle()).accessibilityIdentifier(item.id)
                if index < items.count - 1 { Rectangle().fill(Theme.line.opacity(0.5)).frame(height: 0.5) }
            }
        }
    }
}

enum PersonSection: String, Hashable {
    case relationships = "人物关系", events = "重大事件", remains = "遗珍", records = "称号与资料"
}
enum FamilyGroup: String, Hashable { case children = "子女", siblings = "同辈" }

struct NavigationRow: View {
    let title, subtitle, symbol: String
    let route: DetailRoute
    let identifier: String
    var compactAtLargeSizes = false
    @Environment(\.dynamicTypeSize) private var typeSize
    var body: some View {
        NavigationLink(value: route) {
            HStack(alignment: .center, spacing: 13) {
                VStack(alignment: .leading, spacing: 5) {
                    Text(title).font(.headline).foregroundStyle(Theme.ink)
                    if !subtitle.isEmpty && !(compactAtLargeSizes && typeSize.isAccessibilitySize) { Text(subtitle).font(.caption).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true) }
                }
                Spacer(minLength: 8)
            }.frame(maxWidth: .infinity, minHeight: 44, alignment: .leading).padding(.vertical, 13).contentShape(Rectangle())
        }.buttonStyle(QuietRowStyle()).accessibilityIdentifier(identifier)
            .overlay(alignment: .bottom) { Rectangle().fill(Theme.line.opacity(0.45)).frame(height: 0.5) }
    }
}

struct PersonSectionPage: View {
    let store: HistoryStore
    let personID: String
    let section: PersonSection
    @State private var selectedEventCategory: MajorEventCategory
    init(store: HistoryStore, personID: String, section: PersonSection, initialEventCategory: MajorEventCategory? = nil) {
        self.store = store
        self.personID = personID
        self.section = section
        _selectedEventCategory = State(initialValue: initialEventCategory ?? store.preferredEventCategory(personID))
    }
    var p: Person { store.person(personID) }
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                Text(p.name).font(.subheadline).foregroundStyle(Theme.cinnabar)
                switch section {
                case .relationships: relationships
                case .events:
                    MajorEventsPanel(store: store, personID: p.id, selection: $selectedEventCategory, previewLimit: nil)
                case .remains:
                    if let t = store.tomb(p.id) {
                        NavigationRow(title: t.title, subtitle: "陵寝　\(t.area)", symbol: "mountain.2", route: .tomb(t.id), identifier: "tombCard")
                    }
                    ForEach(store.objects(p.id)) { o in
                        NavigationRow(title: o.title, subtitle: o.subtitle, symbol: o.symbol, route: .object(o.id), identifier: "personObject_\(o.id)")
                    }
                case .records: records
                }
            }.padding(24)
        }.background(Theme.paper).foregroundStyle(Theme.text)
            .navigationTitle(section.rawValue).navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
    }
    var relationships: some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(store.parents(p.id)) { link in
                NavigationRow(title: store.person(link.to).name, subtitle: "\(store.parentLabel(link.kind))　\(store.person(link.to).call)", symbol: "person", route: .person(link.to), identifier: "parent_\(link.to)")
            }
            ForEach(store.spouses(p.id)) { person in
                NavigationRow(title: person.name, subtitle: "配偶　\(person.call)", symbol: "person", route: .person(person.id), identifier: "spouse_\(person.id)")
            }
            if !store.children(p.id).isEmpty {
                NavigationRow(title: "子女", subtitle: "\(store.children(p.id).count)位，按排行", symbol: "person.2", route: .relatives(p.id, .children), identifier: "allChildren")
            }
            if !store.siblings(p).isEmpty {
                NavigationRow(title: "同辈", subtitle: "\(store.siblings(p).count)位，同父或同母", symbol: "person.2", route: .relatives(p.id, .siblings), identifier: "allSiblings")
            }
            if store.hasFamily(p.id) {
                NavigationRow(title: "家族图", subtitle: "在亲属之间切换", symbol: "point.3.connected.trianglepath.dotted", route: .family(p.id), identifier: "explore_\(p.id)")
            }
            if !store.associates(p.id).isEmpty {
                NavigationRow(title: "往来人物", subtitle: "君臣、对手与关系变迁", symbol: "person.2.wave.2", route: .connections(p.id), identifier: "allAssociates")
            }
        }
    }
    var records: some View {
        VStack(alignment: .leading, spacing: 22) {
            fact("常用称呼", p.call)
            if p.kind == "皇帝" { fact("庙号", p.temple); fact("实际在位", p.reign); fact("年号纪年", p.era) }
            else if !p.temple.isEmpty && !["不适用", "无庙号"].contains(p.temple) { fact("追尊与称号", p.temple) }
            if !p.note.isEmpty { fact("生平补记", p.note) }
            if store.portrait(p.id) != nil { NavigationRow(title: "画像与出处", subtitle: store.portrait(p.id)?.title ?? "", symbol: "photo", route: .portrait(p.id), identifier: "recordPortrait") }
            let links = store.links.filter { $0.from == p.id || $0.to == p.id }
            if !links.isEmpty {
                DisclosureGroup("亲属关系的依据") {
                    VStack(alignment: .leading, spacing: 18) {
                        ForEach(links) { link in
                            VStack(alignment: .leading, spacing: 8) {
                                Text("\(store.person(link.from).name) → \(store.person(link.to).name)").font(.subheadline)
                                Text(link.kind == "spouse" ? "配偶" : store.parentLabel(link.kind)).font(.caption).foregroundStyle(Theme.muted)
                                Text(link.note).font(.caption).foregroundStyle(Theme.muted)
                                SourcesView(store: store, ids: link.sources, compact: true)
                            }
                        }
                    }.padding(.top, 12)
                }
            }
            SourcesView(store: store, ids: p.sources)
        }
    }
    func fact(_ name: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 7) { Text(name).font(.caption).foregroundStyle(Theme.muted); Text(value).lineSpacing(5).fixedSize(horizontal: false, vertical: true) }
    }
}

struct MajorEventsPanel: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.dynamicTypeSize) private var typeSize
    let store: HistoryStore
    let personID: String
    @Binding var selection: MajorEventCategory
    let previewLimit: Int?
    var filteredEvents: [HistoryEvent] { store.events(personID, in: selection) }
    var visibleEvents: [HistoryEvent] {
        guard let previewLimit else { return filteredEvents }
        return Array(filteredEvents.prefix(previewLimit))
    }
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            sectionTitle("重大事件")
            let categoryLayout = typeSize.isAccessibilitySize
                ? AnyLayout(VStackLayout(alignment: .leading, spacing: 0))
                : AnyLayout(HStackLayout(spacing: 0))
            categoryLayout {
                ForEach(MajorEventCategory.allCases) { category in
                    Button {
                        withAnimation(reduceMotion ? nil : .easeOut(duration: 0.18)) { selection = category }
                    } label: {
                        VStack(spacing: 8) {
                            Text(category.rawValue)
                                .font(.subheadline.weight(selection == category ? .semibold : .regular))
                                .foregroundStyle(selection == category ? Theme.ink : Theme.muted)
                            Rectangle()
                                .fill(selection == category ? Theme.cinnabar : .clear)
                                .frame(width: 24, height: 1.5)
                        }
                        .frame(maxWidth: .infinity, minHeight: 42)
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(QuietRowStyle())
                    .accessibilityIdentifier("eventCategory_\(category.rawValue)")
                    .accessibilityAddTraits(selection == category ? .isSelected : [])
                }
            }
            .accessibilityElement(children: .contain)

            if visibleEvents.isEmpty {
                Text("暂无条目")
                    .font(.subheadline).foregroundStyle(Theme.muted)
                    .frame(maxWidth: .infinity, minHeight: 60, alignment: .leading)
                .accessibilityIdentifier("majorEventsEmpty")
            } else {
                VStack(spacing: 0) {
                    ForEach(visibleEvents) { EventRow(event: $0) }
                }
            }

            if previewLimit != nil {
                NavigationLink(value: DetailRoute.personEvents(personID, selection)) {
                    Text("查看全部事件").frame(maxWidth: .infinity, alignment: .leading)
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(Theme.cinnabar)
                    .frame(minHeight: 44)
                }
                .buttonStyle(QuietRowStyle())
                .accessibilityIdentifier("category_events")
            }
        }
        .padding(.vertical, 4)
    }
}

struct FamilyMembersPage: View {
    let store: HistoryStore
    let personID: String
    let group: FamilyGroup
    var people: [Person] { group == .children ? store.children(personID) : store.siblings(store.person(personID)) }
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                VStack(alignment: .leading, spacing: 5) {
                    Text(store.person(personID).name).font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                    Text(group == .children ? "按已知排行列示" : "按亲缘关系列示").font(.caption).foregroundStyle(Theme.muted)
                }
                VStack(spacing: 0) {
                    ForEach(people) { person in
                        NavigationLink(value: DetailRoute.family(person.id)) {
                            VStack(alignment: .leading, spacing: 5) {
                                Text(group == .children ? store.orderLabel(person) : store.siblingLabel(person, relativeTo: store.person(personID)))
                                    .font(.caption2).foregroundStyle(Theme.cinnabar)
                                HStack(alignment: .firstTextBaseline, spacing: 10) {
                                    Text(person.name.replacingOccurrences(of: "爱新觉罗·", with: "")).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                                    Text(person.call).font(.caption).foregroundStyle(Theme.muted).lineLimit(1)
                                    Spacer(minLength: 0)
                                }
                            }.frame(maxWidth: .infinity, minHeight: 58, alignment: .leading).padding(.vertical, 11).contentShape(Rectangle())
                                .overlay(alignment: .bottom) { Rectangle().fill(Theme.line.opacity(0.45)).frame(height: 0.5) }
                        }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("member_\(person.id)")
                    }
                }
            }.padding(24)
        }.background(Theme.paper).navigationTitle(group.rawValue).navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
    }
}
